package org.team1073.utils;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.SequenceInputStream;
import java.net.HttpURLConnection;
import java.security.MessageDigest;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;

import android.os.AsyncTask;

public class FileSyncUtils {
	private static final int BUFSIZE = 8192;
	private static final String EOL = "\r\n";
	private final File mBaseDirectory;
	private final String mDeviceName;
    private InputStream mInStream;
    private OutputStream mOutStream;
    private AsyncTask<String, String, Integer> mParent;
    
    public FileSyncUtils( File baseDirectory, String deviceName, InputStream inStream, OutputStream outStream) {
    	mBaseDirectory = baseDirectory;
    	mDeviceName = deviceName;
    	mInStream = inStream;
    	mOutStream = outStream;
    }
    
    //
    // setInputStream() - mutator function to reset the input stream
    //
    public void setInputStream( InputStream inStream ) {
    	mInStream = inStream;
    }
    
    //
    // setOutputStream() - mutator function to reset the output stream
    //
    public void setOutputStream( OutputStream outStream ) {
    	mOutStream = outStream;
    }
    
    //
    // getFileListFromServer() - called from the client to retrieve the list of files
    //                           in the specified path. The retrieved file list is 
    //                           returned in the hash set passed into this function
    //
    // TODO: change the HashSet to be file information, not just a set of filenames
    //
    public void getFilelistFromServer( String path, HashSet<String> filesOnServer ) {
    	DataOutputStream outStream = new DataOutputStream(mOutStream);
    	
		try {	
	        String cmdString = "GET " + "/" + path + EOL;
	    	cmdString += "From: " + mDeviceName + EOL + EOL;
			outStream.writeBytes(cmdString);
			
	    	String recvLine;
	        BufferedReader inBufStream = new BufferedReader(new InputStreamReader(mInStream));
	
			recvLine = inBufStream.readLine();
			if ( recvLine.contains("200 OK")) {

				// read the rest of the headers from the input stream
				boolean headersDone = false;
				while ( !headersDone && (recvLine = inBufStream.readLine()) != null ) {
					if (recvLine.isEmpty()) {
						headersDone = true;
					} else {
						// process the header string - currently we will ignore all headers
					}
				}
					
				// read and process the body of the response, which is expected to be a 
				// series of text strings, each containing file information
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
    
    //
    // createLocalDirectories() - Function will verify that the directories
    //                            referenced by this path exist, creating them
    //                            if they don't already exist
    public boolean createLocalDirectories( String path )
    {
    	boolean error = false;
    	
    	try {
    		File myDir = new File(mBaseDirectory + "/" + path);
    		myDir.mkdirs();
		} catch(Exception e) {
			error = true;
		}
    	
    	return error;
    }
    
    //
    // getFilesToTransfer() - Function compares the set of files on the server device
    //                        with the contents of the specified local directory and
    //                        builds two sets of files to be transferred: one containing
    //                        the files to be pushed to the server, and one containing
    //                        the files to be retrieved from the server
    //
    public void getFilesToTransfer( String path, HashSet<String> filesOnServer,
			                        List<String> filesToSend,
			                        HashSet<String> fileSetToRetrieve) {

		// Get the list of files in the directory on this device and iterate
		// through the list, adding any file that is not already on the server to
		// the list of files to be transferred
		File myDir = new File(mBaseDirectory + "/" + path);
		myDir.mkdirs();
		File[] listOfFiles = myDir.listFiles(); 
		String fileOnDevice;
		
		// initialize the retrieve set with all files on the server; we'll remove
		// the ones that we already have on the local disk
		fileSetToRetrieve.addAll(filesOnServer);
		
		if ( listOfFiles != null ) {
			int numFiles = listOfFiles.length;
			for (int i=0; i<numFiles; i++) 
			{
				if (listOfFiles[i].isFile()) 
				{
					fileOnDevice = listOfFiles[i].getName();
		
					// skip any file that ends with a .tmp suffix, indicating
					// that that file is a temporary file on the device.
					if ( fileOnDevice.endsWith(".tmp") ) {
						fileSetToRetrieve.remove(fileOnDevice);
						continue;
					}
					
					// skip any file that ends with a .mp4 suffix, since the 
					// application is having trouble with those file types.
					if ( fileOnDevice.endsWith(".mp4") ) {
						fileSetToRetrieve.remove(fileOnDevice);
						continue;
					}
					
					//TODO: currently, we only check to see if the file is on the server,
					//      but it would be better to include a timestamp and/or checksum
					//      to detect changed files, too, and transfer them.
					if (!filesOnServer.contains(fileOnDevice))
						filesToSend.add(fileOnDevice);
					else {
						String md5Str;
						try {
							md5Str = getMD5Checksum( mBaseDirectory + "/" + path + "/" + fileOnDevice );
						} catch (Exception e) {
						    e.printStackTrace();							
						}
						
						fileSetToRetrieve.remove(fileOnDevice);
					}
				}
			}
		}
	}
    
    //
    // getFilesToSend() - Function builds a list of files to be sent from the
    //                    specified local directory
    //
    public void getFilesToSend( String path, List<String> filesToSend) {

		// Get the list of files in the directory on this device and iterate
		// through the list, adding any file that is not already on the server to
		// the list of files to be transferred
		File myDir = new File(mBaseDirectory + "/" + path);
		myDir.mkdirs();
		File[] listOfFiles = myDir.listFiles(); 
		String fileOnDevice;
		
		if ( listOfFiles != null ) {
			int numFiles = listOfFiles.length;
			for (int i=0; i<numFiles; i++) 
			{
				if (listOfFiles[i].isFile()) 
				{
					fileOnDevice = listOfFiles[i].getName();
		
					// skip any file that ends with a .tmp suffix, indicating
					// that that file is a temporary file on the device.
					if ( fileOnDevice.endsWith(".tmp") ) {
						continue;
					}
					
					// skip any file that ends with a .mp4 suffix, since the 
					// application is having trouble with those file types.
					if ( fileOnDevice.endsWith(".mp4") ) {
						continue;
					}
					
					filesToSend.add(fileOnDevice);
				}
			}
		}
	}
    
	public Integer sendFilesToServer( String path, List<String> filesToSend) {
		boolean error = false;
		Iterator<String> iterator = filesToSend.iterator();
		String fileOnDevice;
		Integer filesTransferred = 0;
		
		// Transfer the specified list of files to the transfer on the opened socket
		// connection
		while ( iterator.hasNext() && !error) {
			fileOnDevice = iterator.next();

			error = sendFileToServer( path+fileOnDevice );
			if ( !error ){
				filesTransferred++;
			}
		}
		return filesTransferred;
	}

	public boolean sendFileToServer( String filepath ) {
		
		boolean error = false;
		
		// Read the file into a local buffer and transfer the contents to the
		// server using an HTTP formatted request
		try {				
			// read the file contents into a byte array
			String inputFile = mBaseDirectory + "/" + filepath;
			byte[] fileContents = readFileIntoBuffer(inputFile);				

			// format the request and send to the server
			String cmdString = "PUT " + "/" + filepath + EOL;
			cmdString += "From: " + mDeviceName + EOL;
			cmdString += "Content-Length: " + fileContents.length + EOL;
			cmdString += "Content-Type: " + HttpURLConnection.guessContentTypeFromName(filepath) + EOL;
			cmdString += EOL;
			
			DataOutputStream outStream = new DataOutputStream(mOutStream);
			outStream.writeBytes(cmdString);
			outStream.write(fileContents);
			outStream.writeBytes(EOL);
			outStream.flush();
			
	        // read the response, and increment the transfer count if successful
			BufferedReader inBufStream = new BufferedReader(new InputStreamReader(mInStream));
			String recvLine;
			recvLine = inBufStream.readLine();
			
			//TODO: Should we read more headers, or will this be the extent of the response?
			if ( !recvLine.contains("200 OK")) {
				error = true;
			}
		} catch(Exception e) { 
			error = true; 
		}
		return error;
	}

	public boolean sendUpdateRequestToServer( String filepath ) {
		
		boolean error = false;
		
		// Send the update request to the server using an HTTP formatted POST request
		try {				
			// format the request and send to the server
			String cmdString = "POST " + "/" + filepath + EOL;
			cmdString += "From: " + mDeviceName + EOL;
			cmdString += "Content-Length: 0" + EOL;
			cmdString += EOL;
			
			DataOutputStream outStream = new DataOutputStream(mOutStream);
			outStream.writeBytes(cmdString);
			outStream.writeBytes(EOL);
			outStream.flush();
			
	        // read the response, and increment the transfer count if successful
			BufferedReader inBufStream = new BufferedReader(new InputStreamReader(mInStream));
			String recvLine;
			recvLine = inBufStream.readLine();
			
			//TODO: Should we read more headers, or will this be the extent of the response?
			if ( !recvLine.contains("200 OK")) {
				error = true;
			}
		} catch(Exception e) { 
			error = true; 
		}
		return error;
	}

    public void sendFileToClient( String filepath ) {

		try { 
			// read the file contents into a byte array
			String inputFile = mBaseDirectory + "/" + filepath;
			byte[] fileContents = readFileIntoBuffer(inputFile);				

			// format the response and send to the server
	        String responseString = "HTTP/1.0 " + "200 OK" + EOL;
	        responseString += "Content-Length: " + fileContents.length + EOL;
	        responseString += "Content-Type: " + HttpURLConnection.guessContentTypeFromName(filepath) + EOL;
	        responseString += EOL;
			
			// write out the response string with the file contents
	    	DataOutputStream outStream = new DataOutputStream(mOutStream);
			outStream.writeBytes(responseString);
			outStream.write(fileContents);
			outStream.writeBytes(EOL);
			outStream.flush();
							
		} catch(Exception e) { 

		}
    }
    
    public void sendFilelistToClient( String dirpath ) {

		File inputDir = new File(mBaseDirectory + "/" + dirpath);
    	File[] fileList = null;
		
		try {
			// retrieve the directory listing
			fileList = inputDir.listFiles();
			
	    	// write out the response string
	    	DataOutputStream outStream = new DataOutputStream(mOutStream);
	        String responseString = "HTTP/1.0 " + "200 OK" + EOL + EOL;
			outStream.writeBytes(responseString);
			
			// and then write out the list of files
			if ( fileList != null ) {
				int numFilesInDirectory = fileList.length;
				for (int i=0; i<numFilesInDirectory; i++) 
				{
					if (fileList[i].isFile()) 
					{
						String fileEntry = fileList[i].getName();
						// skip over any file that ends with a .tmp extension
						if ( !fileEntry.endsWith(".tmp") )
							outStream.writeBytes(fileEntry + EOL);
					}
				}
			}
			outStream.writeBytes(EOL);
			
		} catch(Exception e) { 

		}
    }

    public void sendResponse( String responseCode ) {
		try { 
	    	DataOutputStream outStream = new DataOutputStream(mOutStream);    	

	    	// write out the response string
	        String responseString = "HTTP/1.0 " + responseCode + EOL + EOL;
			outStream.writeBytes(responseString);
		} catch(Exception e) { 
			
		}
    }
    
	public Integer retrieveFilesFromServer( String path, List<String> filesToRetrieve) {
		boolean error = false;
		Iterator<String> iterator = filesToRetrieve.iterator();
		String fileOnServer;
		Integer filesTransferred = 0;
		        
		while ( iterator.hasNext() && !error) {
			fileOnServer = iterator.next();

			error = retrieveFileFromServer( path + fileOnServer );
			if ( !error ) {
				filesTransferred++;
			}
		}
			
		return filesTransferred;
	}
		

	public boolean retrieveFileFromServer( String filepath ) {
		boolean error = false;
		
		// Retrieve the file from the server using an HTTP formatted request
		try {
			String cmdString = "GET " + "/" + filepath + EOL;
			cmdString += "From: " + mDeviceName + EOL;
			cmdString += EOL;
			DataOutputStream outStream = new DataOutputStream(mOutStream);
			outStream.writeBytes(cmdString);

			byte[] buf = new byte[BUFSIZE];
			int bytesRead = 0;
	        int currBytesRead = 0;
	        int headerMarker = 0;
	        InputStream inputStream = mInStream;
        	
        	// read up to the max buffer size into the local buffer, and find the marker between
        	// the request headers and the body
            bytesRead = inputStream.read(buf, 0, BUFSIZE);
            if (bytesRead == -1) {
                // socket has been closed
                throw new IOException("Socket has been closed");
            }		        
            while (bytesRead > 0) {
                currBytesRead += bytesRead;
                headerMarker = findHeaderSeparator(buf, currBytesRead);
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
                
                // reset the input stream to the new sequence input stream
                setInputStream(inputStream);
            }                    	
        
            // create a buffered reader from the local byte array so that we can parse the headers
            InputStream headerInputStream = new ByteArrayInputStream(buf);
            BufferedReader inBufStream = new BufferedReader(new InputStreamReader(headerInputStream));
			String recvLine = inBufStream.readLine();
			
			// scan for the next non-empty line in the header stream
			while (recvLine.isEmpty()) {
				recvLine = inBufStream.readLine();
			}
				
			if ( !recvLine.isEmpty() ) {
				if ( recvLine.contains("200 OK")) {
					Integer contentLength = 0;

					// read the headers
					while (!(recvLine = inBufStream.readLine()).isEmpty()) {
						String[] tokens = recvLine.split(" ");
						if ( tokens.length > 1 && tokens[0].startsWith("Content-Length:")) {
							contentLength = Integer.parseInt(tokens[1]);
						}
					}

					storeToFile( filepath, contentLength );
				}
			}
		} catch(Exception e) { 
			error = true; 
		}
		return error;
	}

    public byte[] readFileIntoBuffer(String filepath){
		File file = new File(filepath);
		byte[] result = new byte[(int)file.length()];
		try {
			InputStream input = null;
			try {
				int totalBytesRead = 0;
				input = new BufferedInputStream(new FileInputStream(file));
				while(totalBytesRead < result.length){
					int bytesRemaining = result.length - totalBytesRead;
					int bytesRead = input.read(result, totalBytesRead, bytesRemaining); 
					if (bytesRead > 0){
						totalBytesRead += bytesRead;
					}
				}
			}
			finally {
				input.close();
			}
		}
		catch (IOException ex) {
		}
		
		return result;
	}
	
    //
	// read the specified number of bytes from the input stream and store them to
	// the specified file
	//
	public String storeToFile( String filepath, Integer contentLength )
	{
		String responseCode = "200 OK";
		
		BufferedInputStream inbuf = new BufferedInputStream(mInStream);
		
		// read from the input stream and store into a local buffer
		byte[] inputData = new byte[(int)contentLength];    	  
		try {
			int totalBytesRead = 0;
		    while(totalBytesRead < inputData.length) {
		        int bytesRemaining = inputData.length - totalBytesRead;
		        int bytesRead = inbuf.read(inputData, totalBytesRead, bytesRemaining); 
		        if (bytesRead > 0) {
		        	totalBytesRead = totalBytesRead + bytesRead;
		        }
		    }
		}
		catch (IOException ex) {
			responseCode = "500 Internal Error";
			//log(ex);
		}
  
		// write the contents of the local buffer to the specified file
		try {
			OutputStream output = null;
			try {
				File destFile = new File(mBaseDirectory + "/" + filepath);
				output = new BufferedOutputStream(new FileOutputStream(destFile));
				output.write(inputData);
			}
			finally {
				output.close();
			}
		}
		catch(IOException ex){
			responseCode = "500 Internal Error";
			//log(ex);
		}
	  
		return responseCode;
	}  	  

	//
	// findHeaderSeparator() - function is called to find the offset within the specified buffer
	//                         just beyond the headers.
	//
	public int findHeaderSeparator(final byte[] buf, int rlen) {
		// first look for a carriage return/line feed (\r\n\r\n)
	    int splitbyte = 0;
	    while (splitbyte + 3 < rlen) {
	        if (buf[splitbyte] == '\r' && buf[splitbyte + 1] == '\n' && buf[splitbyte + 2] == '\r' && buf[splitbyte + 3] == '\n') {
	            return splitbyte + 4;
	        }
	        splitbyte++;
	    }
	    
	    // also look for just a double carriage return (\n\n)...
	    splitbyte = 0;
	    while (splitbyte + 1 < rlen) {
	        if (buf[splitbyte] == '\n' && buf[splitbyte + 1] == '\n') {
	            return splitbyte + 2;
	        }
	        splitbyte++;
	    }
	    return 0;
	}

	private static byte[] createChecksum(String filename) throws Exception {
       InputStream fis =  new FileInputStream(filename);

       byte[] buffer = new byte[1024];
       MessageDigest complete = MessageDigest.getInstance("MD5");
       int numRead;

       do {
           numRead = fis.read(buffer);
           if (numRead > 0) {
               complete.update(buffer, 0, numRead);
           }
       } while (numRead != -1);

       fis.close();
       return complete.digest();
	}

	public static String getMD5Checksum(String filename) throws Exception {
       byte[] b = createChecksum(filename);
       String result = "";

       for (int i=0; i < b.length; i++) {
           result += Integer.toString( ( b[i] & 0xff ) + 0x100, 16).substring( 1 );
       }
       return result;
	}
	
}
