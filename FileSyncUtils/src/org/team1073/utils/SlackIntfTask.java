package org.team1073.utils;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

import org.json.JSONObject;

import android.os.AsyncTask;

public class SlackIntfTask extends AsyncTask<String, String, Integer> {

	private String webHookUrl;
	
	public SlackIntfTask( ActivityBase activity, String webHookUrl ) {
		this.webHookUrl = webHookUrl;
	}
	
	@Override
	protected Integer doInBackground(String... params) {
		
        publishProgress( "Posting Message To Slack Channel" );
		int count = params.length;
        for (int i = 0; i < count; i++) {
        
	        JSONObject payload = new JSONObject();
        	try {
		        payload.put("text",params[i]);
        	} catch(Exception e) {
        		publishProgress( "Error Formatting Slack Message" );
        	}
	        
			try {
				URL url = new URL(webHookUrl);
				HttpURLConnection connection = (HttpURLConnection) url.openConnection();
				connection.setDoOutput(true);
				connection.setDoInput(true);
				connection.setRequestMethod("POST");
				connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
				OutputStream outstream = connection.getOutputStream();
				outstream.write(payload.toString().getBytes("UTF-8"));
				outstream.flush();
	
				int responseCode = connection.getResponseCode();
				if (responseCode >= 200 && responseCode <= 202)
					publishProgress( "Error Response From Slack Channel" );
				outstream.close();
	
			} catch(Exception e) { 
				publishProgress( "Error Posting Message To Slack Channel" );
			}			
        }	
		return null;
	}

}
