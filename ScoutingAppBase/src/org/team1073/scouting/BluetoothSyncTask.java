package org.team1073.scouting;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import android.app.Activity;
import android.app.AlertDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Environment;
import android.widget.Toast;

public class BluetoothSyncTask extends AsyncTask<String, String, Integer> {
	Activity activity;
	String clientName;
	Integer numFilesTransferred=0;
	Integer numFilesSent, numFilesRetrieved;
	BluetoothAdapter bluetoothAdapter;
	BluetoothSocket socket = null;
	Boolean connectionEstablished;
	DataOutputStream outStream = null;
	DataInputStream inStream = null;
	File directory = Environment.getExternalStorageDirectory();

	public BluetoothSyncTask(Activity activity, String clientName) {
		this.activity = activity;
		this.clientName = clientName;
		this.bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
	}
    protected Integer doInBackground(String... paths) {
    	
    	connectionEstablished = false;

/*
    	Integer retries = 0;

    	// establish a connection to an available bluetooth server
    	while (connectionEstablished != true && retries < 10 ){
    		connectionEstablished = connectToBluetoothServer();
    		if ( connectionEstablished != true ) {
	    		retries++;
                publishProgress( "Retrying Connection" );
	    		try {
	    			Thread.sleep(1000);
	    		}
	    		catch ( InterruptedException e ) {
	                publishProgress( "Sync Retry Delay Interrupted" );
	    		}
    		}
    	}
*/
    	connectionEstablished = connectToBluetoothServer();
    	if ( connectionEstablished == true ) {
    		
    		// loop through the paths that have been passed in and sync the
    		// directory with the server over a bluetooth connection
            publishProgress( "Syncing Files To Server" );

    		int count = paths.length;
            for (int i = 0; i < count; i++) {
        		HashSet<String> filesOnServer = new HashSet<String>();
        		HashSet<String> fileSetToRetrieve = new HashSet<String>();
        		List<String> filesToSend = new ArrayList<String>();
        		
            	getFilesOnServer(paths[i], filesOnServer);
            	getFilesToTransfer(paths[i], filesOnServer, filesToSend, fileSetToRetrieve);
            	List<String> filesToRetrieve = new ArrayList<String>(fileSetToRetrieve);            	
            	numFilesSent = sendFilesToServer( paths[i], filesToSend);
            	numFilesRetrieved = retrieveFilesFromServer( paths[i], filesToRetrieve);
            }
            
            numFilesTransferred = numFilesSent + numFilesRetrieved;
            disconnectFromBluetoothServer();
        }
    	
		return numFilesTransferred;
    }

    protected void onPostExecute(Integer result) {
    	if ( connectionEstablished == true )
    		Toast.makeText(activity, "" + numFilesTransferred + " Files Transferred", Toast.LENGTH_LONG).show();
    	else {
	        new AlertDialog.Builder(activity)
	        .setTitle("Bummer!")
	        .setMessage("Could Not Establish Connection To Server!")
	        .setNeutralButton("OK", null)
	        .show();
    	}
    }
    
    protected void onProgressUpdate(String... progressString) {
        Toast.makeText(activity, progressString[0], Toast.LENGTH_SHORT).show();
    }
    
    private boolean connectToBluetoothServer() {
    	final int REQUEST_ENABLE_BT = 2;
    	final UUID SYNC_SERVICE_ID = UUID.fromString("00001073-0000-1000-8000-00805F9B34F7");
    	boolean connected = false;
    	
		if (!bluetoothAdapter.isEnabled()) {
			Intent enableBtIntent = new Intent( BluetoothAdapter.ACTION_REQUEST_ENABLE);
			activity.startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
		}
		
		// Get all devices paired with this one.
		Set<BluetoothDevice> pairedDevices = bluetoothAdapter.getBondedDevices();
		
		// Cancel, discovery slows connection
		bluetoothAdapter.cancelDiscovery();

		// Client discovers the MAC address of server, if one exists
		if (pairedDevices.size() > 0) {
            publishProgress( "Connecting To Bluetooth Server" );

         // Loop through paired devices
            for (BluetoothDevice device : pairedDevices)
				try {
					socket = device.createRfcommSocketToServiceRecord(SYNC_SERVICE_ID);
					socket.connect();
					connected = true;
					break;
				} catch (Exception e) {}
		}
		
		return connected;
    }
    
    private void disconnectFromBluetoothServer() {
    	try {
			socket.close(); 
		} catch (Exception e) {}
    }
    
    private void getFilesOnServer( String path, HashSet <String>filesOnServer ) {
    
		try {
	        publishProgress( "Retrieving File List From Server" );
	
	        String cmdString = "GET " + path + "\n";
	    	cmdString += "From: " + clientName + "\n\n";
	    	outStream = new DataOutputStream(socket.getOutputStream());
			outStream.writeBytes(cmdString);
			
	    	String recvLine;
	        BufferedReader inBufStream = new BufferedReader(new InputStreamReader(socket.getInputStream()));
	
			inStream = new DataInputStream(socket.getInputStream());
			recvLine = inBufStream.readLine();
			if ( recvLine.contains("200 OK")) {
				// the next line is an empty line separating the response headers
				// from the response body
				recvLine = inBufStream.readLine();
	
				boolean done=false;
				while ( !done && (recvLine = inBufStream.readLine()) != null ) {
					if (recvLine.isEmpty()) {
						done = true;
					} else {
						filesOnServer.add(recvLine);
					}
				}
			}
		} catch(Exception e) {}
    }

    
    private void getFilesToTransfer( String path, HashSet<String> filesOnServer,
    								 List<String> filesToTransfer,
    								 HashSet<String> fileSetToRetrieve) {
    	
		// Get the list of files in the directory on this device and iterate
		// through the list, adding any file that is not already on the server to
    	// the list of files to be transferred
		File myDir = new File(directory + "/" + path);
		File[] listOfFiles = myDir.listFiles(); 
		String fileOnDevice;
		fileSetToRetrieve.addAll(filesOnServer);
 
		boolean error = false;
		if ( listOfFiles != null ) {
			int numFilesToTransfer = listOfFiles.length;
			for (int i = 0; i < numFilesToTransfer && !error; i++) 
			{
				if (listOfFiles[i].isFile()) 
				{
					fileOnDevice = listOfFiles[i].getName();
					
					// skip any file that ends with a .tmp suffix, indicating
					// that that file is a temporary file on the device.
					if ( fileOnDevice.endsWith(".tmp") )
						continue;
					
					//TODO: currently, we only check to see if the file is on the server,
					//      but it would be better to include a timestamp and/or checksum
					//      to verify to detect changed files, too, and transfer them.
					if (!filesOnServer.contains(fileOnDevice))
						filesToTransfer.add(fileOnDevice);
					else
						fileSetToRetrieve.remove(fileOnDevice);
				}
			}
		}
    }
    
	private Integer sendFilesToServer( String path, List<String> filesToSend) {
		File myDir = new File(directory + "/" + path);
		boolean error = false;
		Iterator<String> iterator = filesToSend.iterator();
		String fileOnDevice;
		Integer filesTransferred = 0;
		
		// Transfer the specified list of files to the transfer on the opened socket
		// connection
		while ( iterator.hasNext() && !error) {
			fileOnDevice = iterator.next();
			StringBuffer buffer = new StringBuffer();

			//TODO: This code will only work for a text file. Need to add the ability
			//      to transfer binary (image) files to the server based on file 
			//      extension.
			
			// Read the file into a local buffer
			try {
				File myFile = new File(myDir, fileOnDevice);
				FileReader myReader = new FileReader(myFile);
				BufferedReader reader = new BufferedReader(myReader);
				String line;
				while ((line = reader.readLine()) != null) {
					// skip empty lines in the file
					if ( !line.isEmpty() )
						buffer.append(line + "\n");
				}
			} catch(Exception e) {
				publishProgress( "Error Reading File: " + fileOnDevice );
				error = true;
			}
			
			// Transfer the buffered file to the server using an HTTP formatted
			// request
			try {
				String cmdString = "PUT " + path + fileOnDevice + "\n";
				cmdString += "From: " + clientName + "\n";
				cmdString += "Content Length: " + buffer.length() + "\n";
				cmdString += "\n";
				outStream = new DataOutputStream(socket.getOutputStream());
				outStream.writeBytes(cmdString + buffer.toString() + "\n" );
				
				String recvLine;
				inStream = new DataInputStream(socket.getInputStream());
				recvLine = inStream.readLine();
				if ( recvLine.contains("200 OK")) {
					filesTransferred++;
				}
			} catch(Exception e) { 
				publishProgress( "Error Transferring File: " + fileOnDevice );
				error = true; 
			}
		}
		return filesTransferred;
	}
	
	private Integer retrieveFilesFromServer( String path, List<String> filesToRetrieve) {
		File myDir = new File(directory + "/" + path);
		boolean error = false;
		Iterator<String> iterator = filesToRetrieve.iterator();
		String fileOnServer;
		Integer filesTransferred = 0;
		
		// Transfer the specified list of files to the transfer on the opened socket
		// connection
		while ( iterator.hasNext() && !error) {
			fileOnServer = iterator.next();

			//TODO: This code will only work for a text file. Need to add the ability
			//      to transfer binary (image) files to the server based on file 
			//      extension.
			
			// Retrieve the file from the server using an HTTP formatted
			// request
			try {
				String cmdString = "GET " + path + fileOnServer + "\n";
				cmdString += "From: " + clientName + "\n";
				cmdString += "\n";
				outStream = new DataOutputStream(socket.getOutputStream());
				outStream.writeBytes(cmdString + "\n" );
				
				String recvLine;
				inStream = new DataInputStream(socket.getInputStream());
				recvLine = inStream.readLine();
				if ( recvLine.contains("200 OK")) {
					// the next line is an empty line separating the response headers
					// from the response body
					recvLine = inStream.readLine();

					File myFile = new File(myDir, fileOnServer);
			        FileWriter myWriter = new FileWriter(myFile);
					BufferedWriter writer = new BufferedWriter(myWriter);
			        
					
					boolean done=false;
					while ( !done && (recvLine = inStream.readLine()) != null ) {
						if (recvLine.isEmpty()) {
							done = true;
						} else {
							writer.write(recvLine + "\n");
						}
					}
					writer.close();
					filesTransferred++;
				}
			} catch(Exception e) { 
				publishProgress( "Error Transferring File: " + fileOnServer );
				error = true; 
			}
		}
		return filesTransferred;
	}
	
}

