package org.team1073.utils;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
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
	String syncControl;
	Integer numFilesTransferred=0;
	Integer numFilesSent=0;
	Integer numFilesRetrieved=0;
	BluetoothAdapter bluetoothAdapter;
	BluetoothSocket socket = null;
	Boolean connectionEstablished;
	File directory = Environment.getExternalStorageDirectory();
	
	public BluetoothSyncTask(Activity activity, String clientName, String syncControl) {
		this.activity = activity;
		this.clientName = clientName;
		this.syncControl = syncControl;
		this.bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
	}
    protected Integer doInBackground(String... paths) {
    	
    	connectionEstablished = false;

/*
    	Integer retries = 0;

    	// establish a connection to an available bluetooth server
    	while (connectionEstablished != true && retries < 10 ){
    		connectionEstablished = connectToBluetoothServer("00001073-0000-1000-8000-00805F9B34F7");
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
    	connectionEstablished = connectToBluetoothServer("00001073-0000-1000-8000-00805F9B34F7");
    	if ( connectionEstablished == true ) {
    		
        	try {
				FileSyncUtils syncHelper = new FileSyncUtils( directory, clientName, 
															  socket.getInputStream(), 
															  socket.getOutputStream() );
        	
	    		// loop through the paths that have been passed in and sync the
	    		// directory with the server over a bluetooth connection
	
	    		int count = paths.length;
	            for (int i = 0; i < count; i++) {
	        		HashSet<String> filesOnServer = new HashSet<String>();
	        		
	    	        publishProgress( "Retrieving File List From Server" );
	        		syncHelper.getFilelistFromServer(paths[i], filesOnServer);
	        		
	        		if ( syncControl.equalsIgnoreCase("Download_Updates")) {
	                    publishProgress( "Downloading Files From Server" );
	                   	List<String> filesToRetrieve = new ArrayList<String>(filesOnServer);
	            		numFilesRetrieved += syncHelper.retrieveFilesFromServer( paths[i], filesToRetrieve);
	        		} else {
		        		HashSet<String> fileSetToRetrieve = new HashSet<String>();
		        		List<String> filesToSend = new ArrayList<String>();
		        		syncHelper.getFilesToTransfer(paths[i], filesOnServer, filesToSend, fileSetToRetrieve);
		            	
		                publishProgress( "Sending Files To Server" );
		               	numFilesSent += syncHelper.sendFilesToServer( paths[i], filesToSend);
		            	
		            	if ( syncControl.equalsIgnoreCase("Upload_Download")) {
		                    publishProgress( "Receiving Files From Server" );
		                   	List<String> filesToRetrieve = new ArrayList<String>(fileSetToRetrieve);
		            		numFilesRetrieved += syncHelper.retrieveFilesFromServer( paths[i], filesToRetrieve);
		            	}
	        		}
	            }
	            
	            numFilesTransferred = numFilesSent + numFilesRetrieved;
			} catch (IOException e) {
				e.printStackTrace();
			}
        	
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
    
    private boolean connectToBluetoothServer(String serviceUuidStr) {
    	final int REQUEST_ENABLE_BT = 2;
    	final UUID SYNC_SERVICE_ID = UUID.fromString(serviceUuidStr);
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
		if (pairedDevices.size() == 0) {
            publishProgress( "No Paired Devices" );
		}
		else {
            // Loop through paired devices
            for (BluetoothDevice device : pairedDevices) {
            	publishProgress( "Connecting to " + device.getName() );
				try {
					socket = device.createRfcommSocketToServiceRecord(SYNC_SERVICE_ID);
					socket.connect();
					connected = true;
	            	publishProgress( "Connected to " + device.getName() );
					break;
				} catch (Exception e) {
	            	publishProgress( "Error connecting to " + device.getName() + " Msg: " + e.getMessage() );					
				}
            }
		}
		
		return connected;
    }
    
    private void disconnectFromBluetoothServer() {
    	try {
			socket.close(); 
		} catch (Exception e) {}
    }
	
}

