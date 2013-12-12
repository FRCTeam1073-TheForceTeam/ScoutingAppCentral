/*
 * Copyright (C) 2009 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.team1073.bluetooth.sync;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.SequenceInputStream;
import java.util.UUID;

import org.team1073.utils.FileSyncUtils;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothServerSocket;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
/**
 * This class does all the work for setting up and managing Bluetooth
 * connections with other devices. It has a thread that listens for
 * incoming connections, a thread for connecting with a device, and a
 * thread for performing data transmissions when connected.
 */
public class BluetoothSyncService {
    // Debugging
    private static final String TAG = "BluetoothSyncService";
    private static final boolean D = true;

    // Name for the SDP record when creating server socket
    private static final String NAME_SECURE = "BluetoothSyncServer";
    private static final String NAME_INSECURE = "BluetoothChatInsecure";

    // Unique UUID for this application
    private static final UUID MY_UUID_SECURE =
        UUID.fromString("fa87c0d0-afac-11de-8a39-0800200c9a66");
    private static final UUID MY_UUID_INSECURE =
        UUID.fromString("8ce255c0-200a-11e0-ac64-0800200c9a66");
    
	private static final UUID SYNC_SERVICE_ID = 
			UUID.fromString("00001073-0000-1000-8000-00805F9B34F7");
	private static final UUID SYNC_SERVICE_ID_2 = 
			UUID.fromString("00001073-0000-1000-8000-00805F9B34F8");


	DataOutputStream outStream = null;
	DataInputStream inStream = null;
	File directory = Environment.getExternalStorageDirectory();
	final String serverName = "BluetoothServer";

	// Member fields
    private final BluetoothAdapter mAdapter;
    private final Handler mHandler;
    private AcceptThread mSecureAcceptThread;
    private AcceptThread mInsecureAcceptThread;
    private ConnectThread mConnectThread;
    private ConnectedThread mConnectedThread;
    private int mState;

    // Constants that indicate the current connection state
    public static final int STATE_NONE = 0;       // we're doing nothing
    public static final int STATE_LISTEN = 1;     // now listening for incoming connections
    public static final int STATE_CONNECTING = 2; // now initiating an outgoing connection
    public static final int STATE_CONNECTED = 3;  // now connected to a remote device

    /**
     * Constructor. Prepares a new BluetoothSync session.
     * @param context  The UI Activity Context
     * @param handler  A Handler to send messages back to the UI Activity
     */
    public BluetoothSyncService(Context context, Handler handler) {
        mAdapter = BluetoothAdapter.getDefaultAdapter();
        mState = STATE_NONE;
        mHandler = handler;
    }

    /**
     * Set the current state of the chat connection
     * @param state  An integer defining the current connection state
     */
    private synchronized void setState(int state) {
        if (D) Log.d(TAG, "setState() " + mState + " -> " + state);
        mState = state;

        // Give the new state to the Handler so the UI Activity can update
        mHandler.obtainMessage(BluetoothSync.MESSAGE_STATE_CHANGE, state, -1).sendToTarget();
    }

    /**
     * Return the current connection state. */
    public synchronized int getState() {
        return mState;
    }

    /**
     * Start the chat service. Specifically start AcceptThread to begin a
     * session in listening (server) mode. Called by the Activity onResume() */
    public synchronized void start() {
        if (D) Log.d(TAG, "start");

        // Cancel any thread attempting to make a connection
        if (mConnectThread != null) {mConnectThread.cancel(); mConnectThread = null;}

        // Cancel any thread currently running a connection
        if (mConnectedThread != null) {mConnectedThread.cancel(); mConnectedThread = null;}

        setState(STATE_LISTEN);

        // Start the thread to listen on a BluetoothServerSocket
        if (mSecureAcceptThread == null) {
            mSecureAcceptThread = new AcceptThread(true);
            mSecureAcceptThread.start();
        }
        if (mInsecureAcceptThread == null) {
            mInsecureAcceptThread = new AcceptThread(false);
            mInsecureAcceptThread.start();
        }
    }

    /**
     * Start the ConnectThread to initiate a connection to a remote device.
     * @param device  The BluetoothDevice to connect
     * @param secure Socket Security type - Secure (true) , Insecure (false)
     */
    public synchronized void connect(BluetoothDevice device, boolean secure) {
        if (D) Log.d(TAG, "connect to: " + device);

        // Cancel any thread attempting to make a connection
        if (mState == STATE_CONNECTING) {
            if (mConnectThread != null) {mConnectThread.cancel(); mConnectThread = null;}
        }

        // Cancel any thread currently running a connection
        if (mConnectedThread != null) {mConnectedThread.cancel(); mConnectedThread = null;}

        // Start the thread to connect with the given device
        mConnectThread = new ConnectThread(device, secure);
        mConnectThread.start();
        setState(STATE_CONNECTING);
    }

    /**
     * Start the ConnectedThread to begin managing a Bluetooth connection
     * @param socket  The BluetoothSocket on which the connection was made
     * @param device  The BluetoothDevice that has been connected
     */
    public synchronized void connected(BluetoothSocket socket, BluetoothDevice
            device, final String socketType) {
        if (D) Log.d(TAG, "connected, Socket Type:" + socketType);

        // Cancel the thread that completed the connection
        if (mConnectThread != null) {mConnectThread.cancel(); mConnectThread = null;}

        // Cancel any thread currently running a connection
        if (mConnectedThread != null) {mConnectedThread.cancel(); mConnectedThread = null;}

        // Cancel the accept thread because we only want to connect to one device
        if (mSecureAcceptThread != null) {
            mSecureAcceptThread.cancel();
            mSecureAcceptThread = null;
        }
        if (mInsecureAcceptThread != null) {
            mInsecureAcceptThread.cancel();
            mInsecureAcceptThread = null;
        }

        // Start the thread to manage the connection and perform transmissions
        mConnectedThread = new ConnectedThread(socket, socketType);
        mConnectedThread.start();

        // Send the name of the connected device back to the UI Activity
        Message msg = mHandler.obtainMessage(BluetoothSync.MESSAGE_DEVICE_NAME);
        Bundle bundle = new Bundle();
        bundle.putString(BluetoothSync.DEVICE_NAME, device.getName());
        msg.setData(bundle);
        mHandler.sendMessage(msg);

        setState(STATE_CONNECTED);
    }

    /**
     * Stop all threads
     */
    public synchronized void stop() {
        if (D) Log.d(TAG, "stop");

        if (mConnectThread != null) {
            mConnectThread.cancel();
            mConnectThread = null;
        }

        if (mConnectedThread != null) {
            mConnectedThread.cancel();
            mConnectedThread = null;
        }

        if (mSecureAcceptThread != null) {
            mSecureAcceptThread.cancel();
            mSecureAcceptThread = null;
        }

        if (mInsecureAcceptThread != null) {
            mInsecureAcceptThread.cancel();
            mInsecureAcceptThread = null;
        }
        setState(STATE_NONE);
    }

    /**
     * Write to the ConnectedThread in an unsynchronized manner
     * @param out The bytes to write
     * @see ConnectedThread#write(byte[])
     */
    public void write(byte[] out) {
        // Create temporary object
        ConnectedThread r;
        // Synchronize a copy of the ConnectedThread
        synchronized (this) {
            if (mState != STATE_CONNECTED) return;
            r = mConnectedThread;
        }
        // Perform the write unsynchronized
        r.write(out);
    }

    /**
     * Indicate that the connection attempt failed and notify the UI Activity.
     */
    private void connectionFailed() {
        // Send a failure message back to the Activity
        Message msg = mHandler.obtainMessage(BluetoothSync.MESSAGE_TOAST);
        Bundle bundle = new Bundle();
        bundle.putString(BluetoothSync.TOAST, "Unable to connect device");
        msg.setData(bundle);
        mHandler.sendMessage(msg);

        // Start the service over to restart listening mode
        BluetoothSyncService.this.start();
    }

    /**
     * Indicate that the connection was lost and notify the UI Activity.
     */
    private void connectionLost() {
        // Send a failure message back to the Activity
        Message msg = mHandler.obtainMessage(BluetoothSync.MESSAGE_TOAST);
        Bundle bundle = new Bundle();
        bundle.putString(BluetoothSync.TOAST, "Connection Closed");
        msg.setData(bundle);
        mHandler.sendMessage(msg);

        // Start the service over to restart listening mode
        BluetoothSyncService.this.start();
    }

    /**
     * This thread runs while listening for incoming connections. It behaves
     * like a server-side client. It runs until a connection is accepted
     * (or until cancelled).
     */
    private class AcceptThread extends Thread {
        // The local server socket
        private final BluetoothServerSocket mmServerSocket;
        private String mSocketType;

        public AcceptThread(boolean secure) {
            BluetoothServerSocket tmp = null;
            mSocketType = secure ? "Secure":"Insecure";

            // Create a new listening server socket
            try {
                if (secure) {
//                    tmp = mAdapter.listenUsingRfcommWithServiceRecord(NAME_SECURE,
//                            MY_UUID_SECURE);
                    tmp = mAdapter.listenUsingRfcommWithServiceRecord(NAME_SECURE,
                    		SYNC_SERVICE_ID);
                } else {
//                    tmp = mAdapter.listenUsingInsecureRfcommWithServiceRecord(
//                            NAME_INSECURE, MY_UUID_INSECURE);
                    tmp = mAdapter.listenUsingInsecureRfcommWithServiceRecord(
                            NAME_INSECURE, SYNC_SERVICE_ID_2);
                }
            } catch (IOException e) {
                Log.e(TAG, "Socket Type: " + mSocketType + "listen() failed", e);
            }
            mmServerSocket = tmp;
        }

        public void run() {
            if (D) Log.d(TAG, "Socket Type: " + mSocketType +
                    "BEGIN mAcceptThread" + this);
            setName("AcceptThread" + mSocketType);

            BluetoothSocket socket = null;

            // Listen to the server socket if we're not connected
            while (mState != STATE_CONNECTED) {
                try {
                    // This is a blocking call and will only return on a
                    // successful connection or an exception
                    socket = mmServerSocket.accept();
                } catch (IOException e) {
                    Log.e(TAG, "Socket Type: " + mSocketType + "accept() failed", e);
                    break;
                }

                // If a connection was accepted
                if (socket != null) {
                    synchronized (BluetoothSyncService.this) {
                        switch (mState) {
                        case STATE_LISTEN:
                        case STATE_CONNECTING:
                            // Situation normal. Start the connected thread.
                            connected(socket, socket.getRemoteDevice(),
                                    mSocketType);
                            break;
                        case STATE_NONE:
                        case STATE_CONNECTED:
                            // Either not ready or already connected. Terminate new socket.
                            try {
                                socket.close();
                            } catch (IOException e) {
                                Log.e(TAG, "Could not close unwanted socket", e);
                            }
                            break;
                        }
                    }
                }
            }
            if (D) Log.i(TAG, "END mAcceptThread, socket Type: " + mSocketType);

        }

        public void cancel() {
            if (D) Log.d(TAG, "Socket Type" + mSocketType + "cancel " + this);
            try {
                mmServerSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "Socket Type" + mSocketType + "close() of server failed", e);
            }
        }
    }


    /**
     * This thread runs while attempting to make an outgoing connection
     * with a device. It runs straight through; the connection either
     * succeeds or fails.
     */
    private class ConnectThread extends Thread {
        private final BluetoothSocket mmSocket;
        private final BluetoothDevice mmDevice;
        private String mSocketType;

        public ConnectThread(BluetoothDevice device, boolean secure) {
            mmDevice = device;
            BluetoothSocket tmp = null;
            mSocketType = secure ? "Secure" : "Insecure";

            // Get a BluetoothSocket for a connection with the
            // given BluetoothDevice
            try {
                if (secure) {
                    tmp = device.createRfcommSocketToServiceRecord(
                            MY_UUID_SECURE);
                } else {
                    tmp = device.createInsecureRfcommSocketToServiceRecord(
                            MY_UUID_INSECURE);
                }
            } catch (IOException e) {
                Log.e(TAG, "Socket Type: " + mSocketType + "create() failed", e);
            }
            mmSocket = tmp;
        }

        public void run() {
            Log.i(TAG, "BEGIN mConnectThread SocketType:" + mSocketType);
            setName("ConnectThread" + mSocketType);

            // Always cancel discovery because it will slow down a connection
            mAdapter.cancelDiscovery();

            // Make a connection to the BluetoothSocket
            try {
                // This is a blocking call and will only return on a
                // successful connection or an exception
                mmSocket.connect();
            } catch (IOException e) {
                // Close the socket
                try {
                    mmSocket.close();
                } catch (IOException e2) {
                    Log.e(TAG, "unable to close() " + mSocketType +
                            " socket during connection failure", e2);
                }
                connectionFailed();
                return;
            }

            // Reset the ConnectThread because we're done
            synchronized (BluetoothSyncService.this) {
                mConnectThread = null;
            }

            // Start the connected thread
            connected(mmSocket, mmDevice, mSocketType);
        }

        public void cancel() {
            try {
                mmSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "close() of connect " + mSocketType + " socket failed", e);
            }
        }
    }

    /**
     * This thread runs during a connection with a remote device.
     * It handles all incoming and outgoing transmissions.
     */
    private class ConnectedThread extends Thread {
        private final BluetoothSocket mmSocket;
        private final InputStream mmInStream;
        private final OutputStream mmOutStream;
        public static final int BUFSIZE = 8192;

        public ConnectedThread(BluetoothSocket socket, String socketType) {
            Log.d(TAG, "create ConnectedThread: " + socketType);
            mmSocket = socket;
            InputStream tmpIn = null;
            OutputStream tmpOut = null;

            // Get the BluetoothSocket input and output streams
            try {
                tmpIn = socket.getInputStream();
                tmpOut = socket.getOutputStream();
            } catch (IOException e) {
                Log.e(TAG, "temp sockets not created", e);
            }

            mmInStream = tmpIn;
            mmOutStream = tmpOut;
        }

        public void run() {
            Log.i(TAG, "BEGIN mConnectedThread");
            
            try {
            	FileSyncUtils syncHelper = new FileSyncUtils( directory, serverName, mmInStream, mmOutStream );
	            String recvLine;
				Integer filesTransferred = 0;

		        byte[] buf = new byte[BUFSIZE];
		        InputStream inputStream = mmInStream;
		        
				boolean done=false;
		        while ( !done ) {
			        int bytesRead = 0;
			        int currBytesRead = 0;
			        int headerMarker = 0;
		        	
		        	// read up to the max buffer size into the local buffer, and find the marker between
		        	// the request headers and the body
	                bytesRead = inputStream.read(buf, 0, BUFSIZE);
	                if (bytesRead == 0) {
	                	done = true;
	                	continue;
	                } else if ( bytesRead == 1 ) {
	                	// skip empty lines as we scan for the next request <lf>
	                	if ( buf[0]=='\n' ) {
	                		continue;
	                	}
	                } else if ( bytesRead == 2 ) {
	                	// skip empty lines as we scan for the next request <cr><lf>
	                	if ( buf[0]=='\r' && buf[1]=='\n') {
	                		continue;
	                	}
	                } else if (bytesRead == -1) {
	                    // socket has been closed
	                    throw new IOException("Socket has been closed");
	                }		        
                    while (bytesRead > 0) {
                        currBytesRead += bytesRead;
                        headerMarker = syncHelper.findHeaderSeparator(buf, currBytesRead);
                        if (headerMarker > 0)
                            break;
                        bytesRead = inputStream.read(buf, currBytesRead, BUFSIZE - currBytesRead);
                    }
                    
                    // at this point, we have read enough from the stream to parse the headers
                    // we'll create a sequence input stream that will allow us to read from the local
                    // buffer beyond the headers and then the rest of the stream
                    if ( headerMarker < currBytesRead ) {
                        ByteArrayInputStream splitInputStream = new ByteArrayInputStream(buf, headerMarker, currBytesRead - headerMarker);
                        inputStream = new SequenceInputStream(splitInputStream, inputStream);
                        
                        // reset the input stream within the sync helper now that we have updated it following
                        // the initial buffer read operation
                        syncHelper.setInputStream(inputStream);
                    }                    	
		        
                	// create a buffered reader from the local byte array so that we can parse the headers
                    InputStream headerInputStream = new ByteArrayInputStream(buf);
	                BufferedReader inBufStream = new BufferedReader(new InputStreamReader(headerInputStream));
	                
					if ( !(recvLine = inBufStream.readLine()).isEmpty() ) {
						String[] recvTokens = recvLine.split(" ");
						if ( recvTokens.length > 1 ) {
							if ( recvTokens[0].equals("GET")) {
								// GET request
								File path = new File(directory + "/" + recvTokens[1]);
								String[] pathTokens = recvLine.split("/");
								
								// read the rest of the file line by line and parse headers we care about
								while (!(recvLine = inBufStream.readLine()).isEmpty()) {
									String[] tokens = recvLine.split(" ");
									/*
									if ( tokens.length > 1 && tokens[0].startsWith("From:")) {
										msg = "GET request from " + tokens[1];
					                    mHandler.obtainMessage(BluetoothSync.MESSAGE_READ, msg.length(), 
					                    		               -1, msg.getBytes()).sendToTarget();
									}
									*/
								}

								if ( !path.exists() ) {
									String responseCode = "404 Not Found";
									//sendResponse(responseCode);
									syncHelper.sendResponse(responseCode);
									
								} else if ( path.isDirectory() ) {
									//sendDirectoryListing( path );
									String msg = "Sending File List: " + pathTokens[pathTokens.length-1];
				                    mHandler.obtainMessage(BluetoothSync.MESSAGE_READ, msg.length(), 
				                    		               -1, msg.getBytes()).sendToTarget();
									syncHelper.sendFilelistToClient(recvTokens[1]);
								} else {
									//sendFile( path );
									String msg = "Sending File: " + pathTokens[pathTokens.length-1];
				                    mHandler.obtainMessage(BluetoothSync.MESSAGE_READ, msg.length(), 
				                    		               -1, msg.getBytes()).sendToTarget();
									syncHelper.sendFileToClient(recvTokens[1]);
								}
							} else if ( recvTokens[0].equals("PUT") ) {
								// PUT request
								File path = new File(directory + "/" + recvTokens[1]);
								String[] pathTokens = recvLine.split("/");
								String msg = "Receiving File: " + pathTokens[pathTokens.length-1];
			                    mHandler.obtainMessage(BluetoothSync.MESSAGE_READ, msg.length(), 
			                    		               -1, msg.getBytes()).sendToTarget();

								Integer contentLength = 0;

								// read the headers
								while (!(recvLine = inBufStream.readLine()).isEmpty()) {
									String[] tokens = recvLine.split(" ");
									if ( tokens.length > 1 && tokens[0].startsWith("Content-Length:")) {
										
										contentLength = Integer.parseInt(tokens[1]);
										/*
										msg = "PUT content length: " + tokens[1];
					                    mHandler.obtainMessage(BluetoothSync.MESSAGE_READ, msg.length(), 
					                    		               -1, msg.getBytes()).sendToTarget();
					                    */
									}
								}

								//String responseCode = storeToFile( path, contentLength, inputStream );
								//sendResponse(responseCode);
								String responseCode = syncHelper.storeToFile(recvTokens[1], contentLength);
								syncHelper.sendResponse(responseCode);
							}
							filesTransferred++;
						}
					}
				}
				
				String msg = "Files Transferred: " + filesTransferred;
	            mHandler.obtainMessage(BluetoothSync.MESSAGE_READ, msg.length(), 
	            		               -1, msg.getBytes()).sendToTarget();
	            
            } catch (IOException e) {
                Log.e(TAG, "disconnected", e);
                connectionLost();
                // Start the service over to restart listening mode
                BluetoothSyncService.this.start();
            }
        }
		  
        /**
         * Write to the connected OutStream.
         * @param buffer  The bytes to write
         */
        public void write(byte[] buffer) {
            try {
                mmOutStream.write(buffer);

                // Share the sent message back to the UI Activity
                mHandler.obtainMessage(BluetoothSync.MESSAGE_WRITE, -1, -1, buffer)
                        .sendToTarget();
            } catch (IOException e) {
                Log.e(TAG, "Exception during write", e);
            }
        }

        public void cancel() {
            try {
                mmSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "close() of connect socket failed", e);
            }
        }
    }
}
