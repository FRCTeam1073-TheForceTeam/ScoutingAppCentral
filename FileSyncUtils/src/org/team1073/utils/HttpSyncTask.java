package org.team1073.utils;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import org.team1073.utils.FileSyncUtils;

import android.app.Activity;
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
	FileSyncUtils syncHelper;

	public HttpSyncTask(Activity activity, String clientName, String hostAddr, String syncControl) {
		this.activity = activity;
		this.clientName = clientName;
		this.syncControl = syncControl;
		this.baseUrl = "http://" + hostAddr + "/sync/";
    	syncHelper = new FileSyncUtils( directory, clientName, null, null ); 
	}
	
    protected Integer doInBackground(String... paths) {
    	
		// loop through the paths that have been passed in and sync the
		// directory with the server over a bluetooth connection
        publishProgress( "Syncing Files To Server" );

		int count = paths.length;
        for (int i = 0; i < count; i++) {
    		HashSet<String> filesOnServer = new HashSet<String>();
    		
        	getFilesOnServer(paths[i], filesOnServer);
        	
    		if ( syncControl.equalsIgnoreCase("Download_Updates")) {
               	List<String> filesToRetrieve = new ArrayList<String>(filesOnServer);
        		numFilesRetrieved += syncHelper.retrieveFilesFromServer( paths[i], filesToRetrieve);
    		} else {
        		HashSet<String> fileSetToRetrieve = new HashSet<String>();
        		List<String> filesToSend = new ArrayList<String>();

	        	syncHelper.getFilesToTransfer(paths[i], filesOnServer, filesToSend, fileSetToRetrieve);
	        	List<String> filesToRetrieve = new ArrayList<String>(fileSetToRetrieve);            	
	        	numFilesSent += sendFilesToServer( paths[i], filesToSend);
	        	
	        	if ( syncControl.equalsIgnoreCase("Upload_Download"))
	        		numFilesRetrieved += retrieveFilesFromServer( paths[i], filesToRetrieve);
    		}
        }
        
        numFilesTransferred = numFilesSent + numFilesRetrieved;
    	
		return numFilesTransferred;
    }

    protected void onPostExecute(Integer result) {
    	Toast.makeText(activity, "" + numFilesTransferred + " Files Transferred", Toast.LENGTH_LONG).show();
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
    
	private Integer sendFilesToServer( String path, List<String> filesToSend) {
		boolean error = false;
		Iterator<String> iterator = filesToSend.iterator();
		String fileOnDevice;
		Integer filesTransferred = 0;
		
        publishProgress( "Sending Files To Server" );

        // Transfer the specified list of files to the transfer on the opened socket
		// connection
		while ( iterator.hasNext() && !error) {
			fileOnDevice = iterator.next();

			try {
				URL url = new URL(baseUrl + path + fileOnDevice);
				HttpURLConnection httpCon = (HttpURLConnection) url.openConnection();
				httpCon.setDoOutput(true);
				httpCon.setDoInput(true);
				httpCon.setRequestMethod("PUT");
				//httpCon.setChunkedStreamingMode(4096);
				httpCon.setRequestProperty("Content-Type", 
										   HttpURLConnection.guessContentTypeFromName(fileOnDevice));
				OutputStream outstream = httpCon.getOutputStream();
				
				String inputFile = directory + "/" + path + fileOnDevice;
				byte[] fileContents = syncHelper.readFileIntoBuffer(inputFile);
				outstream.write(fileContents);
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
					InputStream input = connection.getInputStream();
	                byte[] buffer = new byte[4096];
	                int bytesRead = - 1;

	                OutputStream output = new FileOutputStream( myFile );
	                while ( (bytesRead = input.read(buffer)) != -1) {
	                	if (bytesRead > 0) {
	                		output.write(buffer, 0, bytesRead);
	                	}
	                }
	                output.close();					
					
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

