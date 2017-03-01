package org.team1073.utils;

import android.app.Activity;
import android.widget.Toast;

public class ActivityBase extends Activity{
	
	private String last_connected_server = "";	

	// accessor/mutator methods for the private last_connected_server attribute
	public String getLastConnectedServer() {
		return last_connected_server;
	}
	public String setLastConnectedServer(String serverName) {
		return last_connected_server = serverName;
	}
	
	public void SaveDeviceConfiguration() {
        Toast.makeText(ActivityBase.this, "ActivityBase", Toast.LENGTH_SHORT).show();
	}
}
