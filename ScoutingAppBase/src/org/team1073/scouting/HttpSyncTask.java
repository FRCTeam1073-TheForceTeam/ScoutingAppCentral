package org.team1073.scouting;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Environment;
import android.widget.Toast;

public class HttpSyncTask extends AsyncTask<String, String, Integer> {
	Activity activity;
	String clientName;
	String syncControl;
	Integer numFilesTransferred=0;
	Integer numFilesSent=0;
	Integer numFilesRetrieved=0;
	Boolean connectionEstablished;
	DataOutputStream outStream = null;
	DataInputStream inStream = null;
	File directory = Environment.getExternalStorageDirectory();
	String baseUrl;

	public HttpSyncTask(Activity activity, String clientName, String hostAddr, String syncControl) {
		this.activity = activity;
		this.clientName = clientName;
		this.syncControl = syncControl;
		this.baseUrl = "http://" + hostAddr + "/sync/";
	}
    protected Integer doInBackground(String... paths) {
    	
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
        	if ( syncControl.equalsIgnoreCase("Upload_Download"))
        		numFilesRetrieved = retrieveFilesFromServer( paths[i], filesToRetrieve);
        }
        
        numFilesTransferred = numFilesSent + numFilesRetrieved;

		return numFilesTransferred;
    }

    protected void onPostExecute(Integer result) {
    	Toast.makeText(activity, "" + numFilesTransferred + " Files Transferred", Toast.LENGTH_LONG).show();
    
/*
    	else {
	        new AlertDialog.Builder(activity)
	        .setTitle("Bummer!")
	        .setMessage("Could Not Establish Connection To Server!")
	        .setNeutralButton("OK", null)
	        .show();
    	}
*/
    }
    
    protected void onProgressUpdate(String... progressString) {
        Toast.makeText(activity, progressString[0], Toast.LENGTH_SHORT).show();
    }
    
    
    private void getFilesOnServer( String path, HashSet <String>filesOnServer ) {
    
		try {
	        publishProgress( "Retrieving File List From Server" );
	        
	        // create the HttpURLConnection
	        URL url = new URL(baseUrl + path);
	        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
	        
	        // just want to do an HTTP GET here
	        connection.setRequestMethod("GET");
	        // give it 15 seconds to respond
	        connection.setReadTimeout(15*1000);
	        connection.connect();

	        // read the output from the server
	        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
	        String line = null;
	        while ((line = reader.readLine()) != null)
	        {
				filesOnServer.add(line);
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
		
        publishProgress( "Sending Files To Server" );

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
				URL url = new URL(baseUrl + path + fileOnDevice);
				HttpURLConnection httpCon = (HttpURLConnection) url.openConnection();
				httpCon.setDoOutput(true);
				httpCon.setDoInput(true);
				httpCon.setRequestMethod("PUT");
				httpCon.setRequestProperty("Content-type", "text/plain");
				
				OutputStreamWriter outstream = new OutputStreamWriter(
				    httpCon.getOutputStream());
				outstream.write(buffer.toString());
				outstream.flush();

				int responseCode = httpCon.getResponseCode();
				if (responseCode >= 200 && responseCode <= 202)
					filesTransferred++;
				outstream.close();

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
		
        publishProgress( "Receiving Files From Server" );

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
		        URL url = new URL(baseUrl + path + fileOnServer);
		        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
		        
		        // just want to do an HTTP GET here
		        connection.setRequestMethod("GET");
		        // give it 15 seconds to respond
		        connection.setReadTimeout(15*1000);
		        connection.connect();

				int responseCode = connection.getResponseCode();
				if (responseCode >= 200 && responseCode <= 202) {
					File myFile = new File(myDir, fileOnServer);
			        FileWriter myWriter = new FileWriter(myFile);
					BufferedWriter writer = new BufferedWriter(myWriter);
	
					// read the output from the server
			        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
			        String line = null;
			        while ((line = reader.readLine()) != null)
			        {
						writer.write(line + "\n");
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

