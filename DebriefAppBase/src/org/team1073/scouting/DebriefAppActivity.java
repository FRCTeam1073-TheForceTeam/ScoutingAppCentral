package org.team1073.scouting;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.StringTokenizer;

import android.app.AlertDialog;
import android.app.Dialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.View.OnKeyListener;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Toast;

import org.team1073.utils.BluetoothSyncTask;
import org.team1073.utils.HttpSyncTask;
import org.team1073.utils.SlackIntfTask;
import org.team1073.utils.ActivityBase;

import com.google.gson.Gson;

/* Following is how to send an email to a list of addresses from the tablet application       		
String emailList[] = { "foo@email.com", "6031234567@vtext.com" };
String emailSubject = "Hello from Saggy the tablet!";
String emailText = "This is a test message, sending an email to a distribution list from a tablet application.";

Intent emailIntent = new Intent(android.content.Intent.ACTION_SEND);
emailIntent.setType("plain/text");
emailIntent.putExtra(android.content.Intent.EXTRA_EMAIL, emailList);
//emailIntent.putExtra(android.content.Intent.EXTRA_CC, emailCCList);
//emailIntent.putExtra(android.content.Intent.EXTRA_BCC, emailBCCList);
emailIntent.putExtra(android.content.Intent.EXTRA_SUBJECT, emailSubject);
emailIntent.putExtra(android.content.Intent.EXTRA_TEXT, emailText);

startActivity(emailIntent);
*/




public class DebriefAppActivity extends ActivityBase {
	private String device_name="unknown";
	private String device_id="un";
	private String competition_season="2017";
	private String competition_name="Test";
	private String competition_directory= competition_name + competition_season;
	private String host_addr = "";
	private String pri_host_addr = "";
	private String alt_host_addr = "";
	private String host_addr_select = "Primary";
	private String sync_method = "Bluetooth";
	private String sync_control = "Upload_Only";
	private Boolean sync_text_files = true;
	private Boolean sync_media_files = false;
	private Boolean unsavedChanges = false;
	private MatchSchedule matchSchedule = null;
	private String allianceColor = "";
	private String alliancePosition = "";
	
    final String tmpFile = "ScoutingData.tmp";

    //// UIGEN:LIST_DECLARE_BEGIN - insert generated code for email list declarations
    
    //// UIGEN:LIST_DECLARE_END
    
    private String[] Master_list;
    private String[] Cc_list;
    
    /*private void StartFileSyncTask( String sync_control, String path) {
    	String[] paths = path.split("");
    	StartFileSyncTask( sync_control, paths);
    }*/
    private void StartFileSyncTask( String sync_control, String... path) {
		// Create an asynchronous task to transfer the files to/from the server
		// Use either the Bluetooth or HTTP service based on the device configuration
		if (sync_method.equalsIgnoreCase("Bluetooth")) {
    		new BluetoothSyncTask(DebriefAppActivity.this, device_name, sync_control).execute(path);
		} else {
    		new HttpSyncTask(DebriefAppActivity.this, device_name, host_addr, sync_control).execute(path);
		}
    }

	private void DownloadCompetitionConfiguration( ) {
		StartFileSyncTask( "Download_Updates", "ScoutingConfig/");
	}
	
	private void DownloadCompetitionData(String path) {
		String download_control = "Retrieve_Current_Data";
		StartFileSyncTask( download_control, competition_directory + "/" + path +"/");
	}

	private void DownloadMatchSchedule() {
		String download_control = "Retrieve_Files";
		StartFileSyncTask( download_control, competition_directory + "/EventData/matchschedule.json");
	}

	private void LoadCompetitionConfiguration( boolean showDialog ) {

    	try {
    		// This code block will attempt to read the device configuration
    		// file containing the device name, id, and other configuration 
    		// parameters. If the file is there, the information is read and
    		// stored for later access by the application itself
    		File directory = Environment.getExternalStorageDirectory();
			File myDir = new File(directory + "/ScoutingConfig");
			File myFile = new File(myDir, "CompetitionConfig.txt");
	        FileReader myReader = new FileReader(myFile);
			BufferedReader reader = new BufferedReader(myReader);
			String line;
			while ((line = reader.readLine()) != null) {
				StringTokenizer tokenizer = new StringTokenizer(line, "=\t\n\r\f");
				String token = tokenizer.nextToken();
				
                if ( token.equalsIgnoreCase("Competition")) {
                	competition_name = tokenizer.nextToken();
    				competition_directory = competition_name + competition_season;
                }
                if ( token.equalsIgnoreCase("Season")) {
                	competition_season = tokenizer.nextToken();
    				competition_directory = competition_name + competition_season;
                }
                	
			}
			
           	// augment the application title with the competition name
        	String app_title_base = getString(R.string.app_label) + " - ";
        	DebriefAppActivity.this.setTitle(app_title_base + competition_directory);
    		
			reader.close();
    	} catch (Exception e) {
    		showDialog = true;
    	}
    	
    	if ( showDialog == true ) {
    		// The configuration file is not there, so create a pop up dialog
    		// to prompt the user for the necessary device configuration information
    		// needed to continue with the application.
	        Dialog dialog = new Dialog(DebriefAppActivity.this);
	        dialog.setContentView(R.layout.competitiondialog);
	        dialog.setTitle("Please Enter Competition Information");
	        dialog.setCancelable(true);
	        Button button = (Button) dialog.findViewById(R.id.CompOkButton);
	        final EditText CompetitionNameEntry = (EditText) dialog.findViewById(R.id.CompetitionNameEntry);     
	        final EditText CompetitionSeasonEntry = (EditText) dialog.findViewById(R.id.CompetitionSeasonEntry);     

	        CompetitionNameEntry.setText(competition_name);
	        CompetitionSeasonEntry.setText(competition_season);
	        
	        button.setOnClickListener(new OnClickListener() {
	        @Override
	            public void onClick(View v) {
					try {

			    		File directory = Environment.getExternalStorageDirectory();
						File myDir = new File(directory + "/ScoutingConfig");
						myDir.mkdirs();
						File myFile = new File(myDir, "CompetitionConfig.txt");	
				        FileWriter myWriter = new FileWriter(myFile);
						BufferedWriter writer = new BufferedWriter(myWriter);
				        
	                    StringBuffer buffer = new StringBuffer();
	                    String eol = System.getProperty("line.separator");
	                    
	                    if ( !CompetitionSeasonEntry.getText().toString().isEmpty() ) {
	                    	competition_season = CompetitionSeasonEntry.getText().toString();
	                        buffer.append("Season=" + competition_season + eol);
	                    }
	                    if ( !CompetitionNameEntry.getText().toString().isEmpty() ) {
	                    	competition_name = CompetitionNameEntry.getText().toString();
	                        buffer.append("Competition=" + competition_name + eol);
	                    }
	                    competition_directory = competition_name + competition_season;
	                    
						// write the formatted buffer to the file
						writer.write(buffer.toString());
						writer.close();
					} catch (Exception e) {
				        Toast.makeText(DebriefAppActivity.this, e.toString(), Toast.LENGTH_SHORT).show();
					}
	                finish();
	            }
	        });
	        //now that the dialog is set up, it's time to show it    
	        dialog.show();
    	}
	}

	private void LoadDeviceConfiguration( boolean showDialog ) {

    	try {
    		// This code block will attempt to read the device configuration
    		// file containing the device name, id, and other configuration 
    		// parameters. If the file is there, the information is read and
    		// stored for later access by the application itself
    		File directory = Environment.getExternalStorageDirectory();
			File myDir = new File(directory + "/ScoutingConfig");
			File myFile = new File(myDir, "ScoutingConfig.txt");
	        FileReader myReader = new FileReader(myFile);
			BufferedReader reader = new BufferedReader(myReader);
			String line;
			while ((line = reader.readLine()) != null) {
				StringTokenizer tokenizer = new StringTokenizer(line, "=\t\n\r\f");
				String token = tokenizer.nextToken();
				
                if ( token.equalsIgnoreCase("DeviceName") ) {
                	device_name = tokenizer.nextToken();
                } else if ( token.equalsIgnoreCase("DeviceId")) {
                    device_id = tokenizer.nextToken();
	            } else if ( token.equalsIgnoreCase("PriHostAddr")) {
	            	pri_host_addr = tokenizer.nextToken();
	            } else if ( token.equalsIgnoreCase("AltHostAddr")) {
	            	alt_host_addr = tokenizer.nextToken();
	            } else if ( token.equalsIgnoreCase("HostAddrSelect")) {
	            	host_addr_select = tokenizer.nextToken();
	            } else if ( token.equalsIgnoreCase("SyncMethod")) {
	            	sync_method = tokenizer.nextToken();
	            } else if ( token.equalsIgnoreCase("SyncControl")) {
	            	sync_control = tokenizer.nextToken();
	            } else if ( token.equalsIgnoreCase("SyncTextFiles")) {
	            	if ( tokenizer.nextToken().equalsIgnoreCase("Yes"))
	            		sync_text_files = true;
	            	else
	            		sync_text_files = false;
	            } else if ( token.equalsIgnoreCase("SyncMediaFiles")) {
	            	if ( tokenizer.nextToken().equalsIgnoreCase("Yes"))
	            		sync_media_files = true;
	            	else
	            		sync_media_files = false;
	            }
			}
			
			// Set the host address (primary or alternate) now that the configuration
			// is loaded, with primary as the default
			if ( host_addr_select.equalsIgnoreCase("Primary")) {
				host_addr = pri_host_addr;
			} else {
				host_addr = alt_host_addr;
			}
			
			reader.close();
			
    	} catch (Exception e) {
    		showDialog = true;
    	}
    	
    	if ( showDialog == true ) {
    		// The configuration file is not there, so create a pop up dialog
    		// to prompt the user for the necessary device configuration information
    		// needed to continue with the application.
	        Dialog dialog = new Dialog(DebriefAppActivity.this);
	        dialog.setContentView(R.layout.devicedialog);
	        dialog.setTitle("Please Enter Device Information");
	        dialog.setCancelable(true);
	        Button button = (Button) dialog.findViewById(R.id.DeviceOkButton);
	        final EditText DeviceNameEntry = (EditText) dialog.findViewById(R.id.DeviceNameEntry);
	        final EditText DeviceIdEntry = (EditText) dialog.findViewById(R.id.DeviceIdEntry);     
	        final EditText PriHostAddrEntry = (EditText) dialog.findViewById(R.id.PriHostAddrEntry);     
	        final EditText AltHostAddrEntry = (EditText) dialog.findViewById(R.id.AltHostAddrEntry);     
	        final RadioGroup HostAddrSelectRadioGroup = (RadioGroup) dialog.findViewById(R.id.HostAddrSelectRadioGroup);
	        final RadioButton HostAddrSelect_Primary_RadioButton = (RadioButton) dialog.findViewById(R.id.HostAddrSelect_Primary_RadioButton);
	        final RadioButton HostAddrSelect_Alt_RadioButton = (RadioButton) dialog.findViewById(R.id.HostAddrSelect_Alt_RadioButton);	        
	        final RadioGroup SyncMethodRadioGroup = (RadioGroup) dialog.findViewById(R.id.SyncMethodRadioGroup);
	        final RadioButton SyncMethod_Bluetooth_RadioButton = (RadioButton) dialog.findViewById(R.id.SyncMethod_Bluetooth_RadioButton);
	        final RadioButton SyncMethod_Wifi_3g_RadioButton = (RadioButton) dialog.findViewById(R.id.SyncMethod_Wifi_3g_RadioButton);
	        final RadioGroup SyncControlRadioGroup = (RadioGroup) dialog.findViewById(R.id.SyncControlRadioGroup);
	        final RadioButton SyncControl_Upload_Only_RadioButton = (RadioButton) dialog.findViewById(R.id.SyncControl_Upload_Only_RadioButton);
	        final RadioButton SyncControl_Upload_Download_RadioButton = (RadioButton) dialog.findViewById(R.id.SyncControl_Upload_Download_RadioButton);
	        final CheckBox TextFileTypeCheckBox_Checkbox = (CheckBox) dialog.findViewById(R.id.TextFileTypeCheckBox);
	        final CheckBox MediaFileTypeCheckBox_Checkbox = (CheckBox) dialog.findViewById(R.id.MediaFileTypeCheckBox);

	        DeviceNameEntry.setText(device_name);
	        DeviceIdEntry.setText(device_id);
	        
	        PriHostAddrEntry.setText(pri_host_addr);
	        AltHostAddrEntry.setText(alt_host_addr);
	        if (host_addr_select.equalsIgnoreCase("Primary"))
	        	HostAddrSelectRadioGroup.check(R.id.HostAddrSelect_Primary_RadioButton);
	        else
	        	HostAddrSelectRadioGroup.check(R.id.HostAddrSelect_Alt_RadioButton);
	        
	        if (sync_method.equalsIgnoreCase("Bluetooth"))
	        	SyncMethodRadioGroup.check(R.id.SyncMethod_Bluetooth_RadioButton);
            else if (sync_method.equalsIgnoreCase("Wifi_3G"))
	        	SyncMethodRadioGroup.check(R.id.SyncMethod_Wifi_3g_RadioButton);
	        if (sync_control.equalsIgnoreCase("Upload_Only"))
	        	SyncControlRadioGroup.check(R.id.SyncControl_Upload_Only_RadioButton);
            else if (sync_control.equalsIgnoreCase("Upload_Download"))
	        	SyncControlRadioGroup.check(R.id.SyncControl_Upload_Download_RadioButton);
	        TextFileTypeCheckBox_Checkbox.setChecked(sync_text_files);
	        MediaFileTypeCheckBox_Checkbox.setChecked(sync_media_files);
	        
	        button.setOnClickListener(new OnClickListener() {
	        @Override
	            public void onClick(View v) {
					try {

			    		File directory = Environment.getExternalStorageDirectory();
						File myDir = new File(directory + "/ScoutingConfig");
						myDir.mkdirs();
						File myFile = new File(myDir, "ScoutingConfig.txt");	
				        FileWriter myWriter = new FileWriter(myFile);
						BufferedWriter writer = new BufferedWriter(myWriter);
				        
	                    StringBuffer buffer = new StringBuffer();
	                    String eol = System.getProperty("line.separator");
	                    
	                    if ( !DeviceNameEntry.getText().toString().isEmpty() )
	                        buffer.append("DeviceName=" + DeviceNameEntry.getText().toString() + eol);
	                    if ( !DeviceIdEntry.getText().toString().isEmpty() )
	                        buffer.append("DeviceId=" + DeviceIdEntry.getText().toString() + eol);
	                    
	                    if ( !PriHostAddrEntry.getText().toString().isEmpty() )
	                        buffer.append("PriHostAddr=" + PriHostAddrEntry.getText().toString() + eol);
	                    if ( !AltHostAddrEntry.getText().toString().isEmpty() )
	                        buffer.append("AltHostAddr=" + AltHostAddrEntry.getText().toString() + eol);
	                    if (HostAddrSelect_Primary_RadioButton.isChecked())
	                        buffer.append("HostAddrSelect=" + HostAddrSelect_Primary_RadioButton.getText().toString() + eol);
	                    else if (HostAddrSelect_Alt_RadioButton.isChecked())
	                        buffer.append("HostAddrSelect=" + HostAddrSelect_Alt_RadioButton.getText().toString() + eol);
	                    	
	                    if (SyncMethod_Bluetooth_RadioButton.isChecked())
	                        buffer.append("SyncMethod=" + SyncMethod_Bluetooth_RadioButton.getText().toString() + eol);
	                    else if (SyncMethod_Wifi_3g_RadioButton.isChecked())
	                        buffer.append("SyncMethod=" + SyncMethod_Wifi_3g_RadioButton.getText().toString() + eol);
	                    
	                    if (SyncMethod_Bluetooth_RadioButton.isChecked())
	                        buffer.append("SyncMethod=" + SyncMethod_Bluetooth_RadioButton.getText().toString() + eol);
	                    else if (SyncMethod_Wifi_3g_RadioButton.isChecked())
	                        buffer.append("SyncMethod=" + SyncMethod_Wifi_3g_RadioButton.getText().toString() + eol);
	                    if (SyncControl_Upload_Only_RadioButton.isChecked())
	                        buffer.append("SyncControl=" + SyncControl_Upload_Only_RadioButton.getText().toString() + eol);
	                    else if (SyncControl_Upload_Download_RadioButton.isChecked())
	                        buffer.append("SyncControl=" + SyncControl_Upload_Download_RadioButton.getText().toString() + eol);
	                    if (TextFileTypeCheckBox_Checkbox.isChecked())
	                        buffer.append("SyncTextFiles=Yes" + eol);
	                    else
	                        buffer.append("SyncTextFiles=No" + eol);
	                    if (MediaFileTypeCheckBox_Checkbox.isChecked())
	                        buffer.append("SyncMediaFiles=Yes" + eol);
	                    else
	                        buffer.append("SyncMediaFiles=No" + eol);
	                    
						// write the formatted buffer to the file
						writer.write(buffer.toString());
						writer.close();
					} catch (Exception e) {
				        Toast.makeText(DebriefAppActivity.this, e.toString(), Toast.LENGTH_SHORT).show();
					}
	                finish();
	            }
	        });
	        //now that the dialog is set up, it's time to show it    
	        dialog.show();
    	}
	}

	public void SaveDeviceConfiguration() {
		try {

    		File directory = Environment.getExternalStorageDirectory();
			File myDir = new File(directory + "/ScoutingConfig");
			myDir.mkdirs();
			File myFile = new File(myDir, "ScoutingConfig.txt");	
	        FileWriter myWriter = new FileWriter(myFile);
			BufferedWriter writer = new BufferedWriter(myWriter);
	        
            StringBuffer buffer = new StringBuffer();
            String eol = System.getProperty("line.separator");
            if ( !device_name.isEmpty() )
            	buffer.append("DeviceName=" + device_name + eol);
            if ( !device_id.isEmpty() )
                buffer.append("DeviceId=" + device_id + eol);
            if ( !host_addr.isEmpty() )
                buffer.append("HostAddr=" + host_addr + eol);
            if ( !sync_method.isEmpty() )
            	buffer.append("SyncMethod=" + sync_method + eol);
            if ( !sync_control.isEmpty() )
                buffer.append("SyncControl=" + sync_control + eol);
             if ( !getLastConnectedServer().isEmpty() )
                buffer.append("LastConnectedServer=" + getLastConnectedServer() + eol);
            if (sync_text_files == true)
                buffer.append("SyncTextFiles=Yes" + eol);
            else
                buffer.append("SyncTextFiles=No" + eol);
            if (sync_media_files)
                buffer.append("SyncMediaFiles=Yes" + eol);
            else
                buffer.append("SyncMediaFiles=No" + eol);
            
			// write the formatted buffer to the file
			writer.write(buffer.toString());
			writer.close();
		} catch (Exception e) {
	        Toast.makeText(DebriefAppActivity.this, e.toString(), Toast.LENGTH_SHORT).show();
		}
	}
	
	private void LoadTaskGroupLists() {
		
	    //// UIGEN:LIST_ALLOC_BEGIN - insert generated code for email list declarations
	    //// UIGEN:LIST_ALLOC_END

		Master_list = new String[1];
	    Cc_list = new String[1];
		
    	try {
    		// This code block will attempt to read the device configuration
    		// file containing the device name, id, and other configuration 
    		// parameters. If the file is there, the information is read and
    		// stored for later access by the application itself
    		File directory = Environment.getExternalStorageDirectory();
    		
    		// TODO: Move the competition configuration from the base directory to the directory
    		//       for each competition. When this is complete, then restore the commented out
    		//       line.
			//File myDir = new File(directory + "/" + competition_directory + "/ScoutingConfig");
			File myDir = new File(directory + "/" + "/ScoutingConfig");
			File myFile = new File(myDir, "TaskGroupEmailLists.txt");
	        FileReader myReader = new FileReader(myFile);
			BufferedReader reader = new BufferedReader(myReader);
			String line;
			while ((line = reader.readLine()) != null) {
				StringTokenizer tokenizer = new StringTokenizer(line, "=\t\n\r\f");
				String token = tokenizer.nextToken();
				
				try {
	                if ( token.equalsIgnoreCase("Cc_email_list") ) {
	                	Cc_list = tokenizer.nextToken().split(";");
	                //// UIGEN:LIST_LOAD_BEGIN - insert fragments to load email lists from file contents
	                	
	                //// UIGEN:LIST_LOAD_END
	                } else if ( token.equalsIgnoreCase("Master_email_list")) {
	                    Master_list = tokenizer.nextToken().split(";");
	                }
				} catch (Exception e) {
				}
			}
			
    		Toast.makeText(DebriefAppActivity.this, "Taskgroup List Loaded", Toast.LENGTH_LONG).show();
    		
    	} catch (Exception e) {
    	}
    	
	}

	
	// Helper function to build up the filename based on the team and match number. 
	// We may ultimately want to add some other attribute (like date/time,
	// or a sequence number) to the filenames to help keep the file names unique
	private String buildFilename(EditText teamEntry, String type, String otherKey){
				
		String filename = "Team" + teamEntry.getText().toString() +
				"_" + type + otherKey + "_" + 
				device_id + ".txt";
		
        return filename;
	}
	
    // helper function to process click actions for Checkbox fields
    public void onCheckboxClicked(View view) {
    	unsavedChanges = true;
    }
    
    private String buildIssueFilename(EditText entry, String type){
		String filename="";
		if ( entry.getText().toString().isEmpty() ) {
			Integer count=1;
			boolean found=false;
			filename="";
			while ( !found ) {
				filename = type + "_" + count.toString() + "_" + device_id + ".txt";
				if ( !doesFileExist(filename) )
					found = true;
				else
					count++;
			}
		} else {
			filename = type + "_" + entry.getText().toString() + "_" + device_id + ".txt";
		}
		
        return filename;
	}

	private String buildDebriefFilename(String type, String label, String otherKey){

		String filename = type + "_" + label + otherKey + "_" +
				device_id + ".txt";
		
        return filename;
	}

/*
	private String buildDebriefFilename(String type, String label, String otherKey){

		Integer count=1;
		boolean found=false;
		String filename="";
		while ( !found ) {
			String count_str = String.format("%03d", count);
			filename = type + "_" + label + otherKey + "_" + count_str + "_" +
					   device_id + ".txt";
			if ( !doesFileExist(filename) )
				found = true;
			else
				count++;
		}
		
		
        return filename;
	}
*/
	
	// helper function to process key actions for an EditText field
	private boolean onKey(View v, int keyCode, KeyEvent event, EditText entry) {
		unsavedChanges = true;
		// If the event is a key-down event on the "enter" button
   		if ((event.getAction() == KeyEvent.ACTION_DOWN) &&
   			(keyCode == KeyEvent.KEYCODE_ENTER)) {
   				// For now, we'll just make a toast with the entered data
   				Toast.makeText(DebriefAppActivity.this, entry.getText(), Toast.LENGTH_SHORT).show();
   				return true;
   		}
   		return false;
   	}
	
	// Helper function to search a comma separated string for the specified value string
	private boolean parseFieldForValue( String fieldStr, String valueStr ) {
	     StringTokenizer tokenizer = new StringTokenizer(fieldStr, ",");
	     while (tokenizer.hasMoreTokens()) {
	     	if (tokenizer.nextToken().equalsIgnoreCase(valueStr))
	     		return true;
	     }
	     return false;
	}

	private boolean doesPictureFileExist( String filename ) {
		if ( openPictureFileForInput(filename) != null ) {
			return true;
      } else
      	return false;
	}

	private BufferedReader openPictureFileForInput( String filename ) {
  		
		try {
  			File directory = Environment.getExternalStorageDirectory();
			File myDir = new File(directory + "/" + competition_directory + "/ScoutingPictures");
			File myFile = new File(myDir, filename);
	        FileReader myReader = new FileReader(myFile);
			BufferedReader reader = new BufferedReader(myReader);
			
			return reader;
		} catch (Exception e) {
			return null;
		}    	
	}
		
	private boolean doesFileExist( String filename ) {
		
		if ( openFileForInput(filename) != null ) {
			return true;
        } else
        	return false;
	}

    private BufferedReader openFileForInput( String filename ) {
    		
    	try {
    		File directory = Environment.getExternalStorageDirectory();
			File myDir = new File(directory + "/" + competition_directory + "/ScoutingData");
			File myFile = new File(myDir, filename);
	        FileReader myReader = new FileReader(myFile);
			BufferedReader reader = new BufferedReader(myReader);
			
        	return reader;
    	} catch (Exception e) {
    		return null;
		}    	
    }
	    
    private void writeOutputFile(String filename, String formattedBuffer)
    {
    	// Write out the file
		try {
		    // Open up the file for writing
			File directory = Environment.getExternalStorageDirectory();
			File myDir = new File(directory + "/" + competition_directory + "/ScoutingData");
			myDir.mkdirs();
			File myFile = new File(myDir, filename);
	        FileWriter myWriter = new FileWriter(myFile);
			BufferedWriter writer = new BufferedWriter(myWriter);
	        
			// write the formatted buffer to the file
			writer.write(formattedBuffer);

			// And, close the file
			writer.close();
		} catch (Exception e) {
	        Toast.makeText(DebriefAppActivity.this, e.toString(), Toast.LENGTH_SHORT).show();
		}
    }
    
    private void deleteScoutingData( String filename ) {
    		File directory = Environment.getExternalStorageDirectory();
			File myDir = new File(directory + "/" + competition_directory + "/ScoutingData");
			File myFile = new File(myDir, filename);
			myFile.delete();			
    }
	    
    // Camera stuff
	private static int TAKE_PICTURE = 1;
	private Uri outputFileUri;
	
	public void recordMedia(String teamName, String media) {
		Integer count = 1;
		Intent intent = new Intent(media);
		File directory = Environment.getExternalStorageDirectory();
		File myDir = new File(directory + "/" + competition_directory + "/ScoutingPictures");
		myDir.mkdirs();
		
		boolean found=false;
		String type = ".jpg";
		if ( media.contains("IMAGE_CAPTURE") )
			type = ".jpg";
		else if ( media.contains("VIDEO_CAPTURE") )
			type = ".mp4";
		else {
			Toast.makeText(this, "Invalid Request!", Toast.LENGTH_SHORT).show();
			return;
		}
		
		String filename="";
		while ( !found ) {
			filename = "Team" + teamName + "_" + count.toString() + "_" + device_id + type;
			if ( !doesPictureFileExist(filename) )
				found = true;
			else
				count++;
		}
		
		File myFile = new File(myDir, filename);
		outputFileUri = Uri.fromFile(myFile);
		intent.putExtra(MediaStore.EXTRA_OUTPUT, outputFileUri);
		startActivityForResult(intent, TAKE_PICTURE);
	}
	@Override
	protected void onActivityResult(int requestCode, int resultCode, Intent data){
 
		if (requestCode == TAKE_PICTURE){
			Toast.makeText(this, "Media Captured!", Toast.LENGTH_SHORT).show();
		}
 
	}
		
    private Button SaveButton;
    private Button ReloadButton;
    private EditText ScouterEntry;
    private EditText TeamEntry;
    private EditText NotesEntry;
    private Button PitSyncButton;
    private Button CloudSyncButton;

    private EditText MatchEntry;
    private Button Issue1_NotifyButton;
    private EditText Issue1_SummaryEntry;
    private RadioGroup Issue1_PriorityRadioGroup;
    private RadioButton Issue1_PriorityPriority_1RadioButton;
    private RadioButton Issue1_PriorityPriority_2RadioButton;
    private RadioButton Issue1_PriorityPriority_3RadioButton;
    private EditText Issue1_DescriptionEntry;
    private Button Issue2_NotifyButton;
    private EditText Issue2_SummaryEntry;
    private RadioGroup Issue2_PriorityRadioGroup;
    private RadioButton Issue2_PriorityPriority_1RadioButton;
    private RadioButton Issue2_PriorityPriority_2RadioButton;
    private RadioButton Issue2_PriorityPriority_3RadioButton;
    private EditText Issue2_DescriptionEntry;
    private Button Issue3_NotifyButton;
    private EditText Issue3_SummaryEntry;
    private RadioGroup Issue3_PriorityRadioGroup;
    private RadioButton Issue3_PriorityPriority_1RadioButton;
    private RadioButton Issue3_PriorityPriority_2RadioButton;
    private RadioButton Issue3_PriorityPriority_3RadioButton;
    private EditText Issue3_DescriptionEntry;
    private EditText Match_SummaryEntry;

    //// UIGEN:ISSUE1_CHECKBOX_DECLARE_BEGIN - insert generated code for taskgroup checkbox variables declarations
    //// UIGEN:ISSUE1_CHECKBOX_DECLARE_END
    
    //// UIGEN:ISSUE2_CHECKBOX_DECLARE_BEGIN - insert generated code for taskgroup checkbox variables declarations
    //// UIGEN:ISSUE2_CHECKBOX_DECLARE_END
    
    //// UIGEN:ISSUE3_CHECKBOX_DECLARE_BEGIN - insert generated code for taskgroup checkbox variables declarations
    //// UIGEN:ISSUE3_CHECKBOX_DECLARE_END
    
    
    //// UIGEN:VAR_DECLARE_BEGIN - insert generated code for field variables declarations
    //// UIGEN:VAR_DECLARE_END
    
    //// UICUSTOM:VAR_DECLARE_BEGIN - insert custom code for field variables declarations
    //// UICUSTOM:VAR_DECLARE_END

    public boolean saveScoutingData( final String filename, boolean promptForOverwrite ) {
        String eol = System.getProperty("line.separator");

        // Format the field data into a buffer, with one field on each line. 
        // The data is to be formatted as a name:value pair with the attribute 
        // name expressed by a character string with no whitespace. Compound 
        // names should be expressed with an underscore '_' between words
        final StringBuffer buffer = new StringBuffer();
        
        if ( !ScouterEntry.getText().toString().isEmpty() )
            buffer.append("Scouter:" + ScouterEntry.getText().toString() + eol);

        if ( !TeamEntry.getText().toString().isEmpty() )
            buffer.append("Team:" + TeamEntry.getText().toString() + eol);

        if ( !NotesEntry.getText().toString().isEmpty() )
            buffer.append("Notes:" + NotesEntry.getText().toString() + eol);

		// Add the current epoch timestamp as an attribute so that we can
        // determine if the specified file is later updated
        long currTime = System.currentTimeMillis()/1000;
		buffer.append("Timestamp:" + currTime + eol);
		
		// Add in the competition directory string as an attribute so that
		// we can process the data for multiple competitions without conflict
		buffer.append("Competition:" + competition_directory + eol);
		
        if ( !MatchEntry.getText().toString().isEmpty() )
            buffer.append("Match:" + MatchEntry.getText().toString() + eol);

        if ( !Issue1_SummaryEntry.getText().toString().isEmpty() )
            buffer.append("Issue1_Summary:" + Issue1_SummaryEntry.getText().toString() + eol);

        String Issue1_TaskgroupSelection = "Issue1_Taskgroup:";
        boolean Issue1_TaskgroupIsChecked = false;
        
		//// UIGEN:ISSUE1_SAVE_BEGIN - insert generated code for save handler here                   
		//// UIGEN:ISSUE1_SAVE_END        

        if ( Issue1_TaskgroupIsChecked )
            buffer.append(eol);

        String Issue1_PrioritySelection = "Issue1_Priority:";
        if (Issue1_PriorityPriority_1RadioButton.isChecked())
            buffer.append(Issue1_PrioritySelection + Issue1_PriorityPriority_1RadioButton.getText().toString() + eol);
        else if (Issue1_PriorityPriority_2RadioButton.isChecked())
            buffer.append(Issue1_PrioritySelection + Issue1_PriorityPriority_2RadioButton.getText().toString() + eol);
        else if (Issue1_PriorityPriority_3RadioButton.isChecked())
            buffer.append(Issue1_PrioritySelection + Issue1_PriorityPriority_3RadioButton.getText().toString() + eol);

        if ( !Issue1_DescriptionEntry.getText().toString().isEmpty() )
            buffer.append("Issue1_Description:" + Issue1_DescriptionEntry.getText().toString() + eol);

        if ( !Issue2_SummaryEntry.getText().toString().isEmpty() )
            buffer.append("Issue2_Summary:" + Issue2_SummaryEntry.getText().toString() + eol);

        String Issue2_TaskgroupSelection = "Issue2_Taskgroup:";
        boolean Issue2_TaskgroupIsChecked = false;
        
		//// UIGEN:ISSUE2_SAVE_BEGIN - insert generated code for save handler here                   
		//// UIGEN:ISSUE2_SAVE_END        

        if ( Issue2_TaskgroupIsChecked )
            buffer.append(eol);

        String Issue2_PrioritySelection = "Issue2_Priority:";
        if (Issue2_PriorityPriority_1RadioButton.isChecked())
            buffer.append(Issue2_PrioritySelection + Issue2_PriorityPriority_1RadioButton.getText().toString() + eol);
        else if (Issue2_PriorityPriority_2RadioButton.isChecked())
            buffer.append(Issue2_PrioritySelection + Issue2_PriorityPriority_2RadioButton.getText().toString() + eol);
        else if (Issue2_PriorityPriority_3RadioButton.isChecked())
            buffer.append(Issue2_PrioritySelection + Issue2_PriorityPriority_3RadioButton.getText().toString() + eol);

        if ( !Issue2_DescriptionEntry.getText().toString().isEmpty() )
            buffer.append("Issue2_Description:" + Issue2_DescriptionEntry.getText().toString() + eol);

        if ( !Issue3_SummaryEntry.getText().toString().isEmpty() )
            buffer.append("Issue3_Summary:" + Issue3_SummaryEntry.getText().toString() + eol);

        String Issue3_TaskgroupSelection = "Issue3_Taskgroup:";
        boolean Issue3_TaskgroupIsChecked = false;
        
		//// UIGEN:ISSUE3_SAVE_BEGIN - insert generated code for save handler here
   		//// UIGEN:ISSUE3_SAVE_END        

        if ( Issue3_TaskgroupIsChecked )
            buffer.append(eol);

        String Issue3_PrioritySelection = "Issue3_Priority:";
        if (Issue3_PriorityPriority_1RadioButton.isChecked())
            buffer.append(Issue3_PrioritySelection + Issue3_PriorityPriority_1RadioButton.getText().toString() + eol);
        else if (Issue3_PriorityPriority_2RadioButton.isChecked())
            buffer.append(Issue3_PrioritySelection + Issue3_PriorityPriority_2RadioButton.getText().toString() + eol);
        else if (Issue3_PriorityPriority_3RadioButton.isChecked())
            buffer.append(Issue3_PrioritySelection + Issue3_PriorityPriority_3RadioButton.getText().toString() + eol);

        if ( !Issue3_DescriptionEntry.getText().toString().isEmpty() )
            buffer.append("Issue3_Description:" + Issue3_DescriptionEntry.getText().toString() + eol);

        if ( !Match_SummaryEntry.getText().toString().isEmpty() )
            buffer.append("Match_Summary:" + Match_SummaryEntry.getText().toString() + eol);
		
		//// UICUSTOM:SAVE_BEGIN - insert custom code for save handler here                   
		//// UICUSTOM:SAVE_END
		
        // make sure that the filename doesn't already exist, so we don't 
        // overwrite an existing file.
        if ( doesFileExist(filename) && promptForOverwrite ) {
            new AlertDialog.Builder(DebriefAppActivity.this)
            .setTitle("File Already Exists: " + filename)
            .setMessage("Overwrite File?")
            .setNegativeButton("No", new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface dialog, int whichButton) {
                    Toast.makeText(DebriefAppActivity.this, "Save Cancelled", Toast.LENGTH_LONG).show();
                }
            })
            .setPositiveButton("Yes", new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface dialog, int whichButton) {
                	writeOutputFile(filename, buffer.toString());
                }
            })
            .show();                      
        } else {
        	writeOutputFile(filename, buffer.toString());
        }
        
        return true;
    }
    
    public boolean reloadScoutingData( final String filename, StringBuffer buffer )      
    {
		String eol = System.getProperty("line.separator");
		String line;

		try {
	        // Open up the file and read the file line by line
	        BufferedReader input = openFileForInput( filename );
	        if ( input == null )
	        	return false;
	
			while ((line = input.readLine()) != null) {
				buffer.append(line + eol);
				
				// following is a crude file line parser that will re-apply the
				// configuration to the user interface objects as the stored file
				// data is reloaded
				StringTokenizer tokenizer = new StringTokenizer(line, ":\t\n\r\f");
				String token = tokenizer.nextToken();
				
	            if ( token.equalsIgnoreCase("Scouter") ) {
	                ScouterEntry.setText(tokenizer.nextToken());
	            } else if ( token.equalsIgnoreCase("Team")) {
	                TeamEntry.setText(tokenizer.nextToken());
	            } else if ( token.equalsIgnoreCase("Notes")) {
	                NotesEntry.setText(tokenizer.nextToken());
	            } else if ( token.equalsIgnoreCase("Timestamp")) {
	            	// ignore because there is no UI field for this token
	            } else if ( token.equalsIgnoreCase("Competition")) {
	            	// ignore because there is no UI field for this token
	            	
                } else if ( token.equalsIgnoreCase("Match")) {
                    MatchEntry.setText(tokenizer.nextToken());
                } else if ( token.equalsIgnoreCase("Issue1_Summary")) {
                    Issue1_SummaryEntry.setText(tokenizer.nextToken());
                } else if ( token.equalsIgnoreCase("Issue1_Taskgroup")) {
                    String valueStr = tokenizer.nextToken();
                    
		            //// UIGEN:ISSUE1_RELOAD_BEGIN - insert generated code for reload handler here
		            //// UIGEN:ISSUE1_RELOAD_END
                    
                } else if ( token.equalsIgnoreCase("Issue1_Priority")) {
                    String valueStr = tokenizer.nextToken();
                    if ( valueStr.equalsIgnoreCase("Priority_1") )
                        Issue1_PriorityRadioGroup.check(R.id.Issue1_PriorityPriority_1RadioButton);
                    else if ( valueStr.equalsIgnoreCase("Priority_2") )
                        Issue1_PriorityRadioGroup.check(R.id.Issue1_PriorityPriority_2RadioButton);
                    else if ( valueStr.equalsIgnoreCase("Priority_3") )
                        Issue1_PriorityRadioGroup.check(R.id.Issue1_PriorityPriority_3RadioButton);
                } else if ( token.equalsIgnoreCase("Issue1_Description")) {
                    Issue1_DescriptionEntry.setText(tokenizer.nextToken());
                } else if ( token.equalsIgnoreCase("Issue2_Summary")) {
                    Issue2_SummaryEntry.setText(tokenizer.nextToken());
                } else if ( token.equalsIgnoreCase("Issue2_Taskgroup")) {
                    String valueStr = tokenizer.nextToken();
                    
		            //// UIGEN:ISSUE2_RELOAD_BEGIN - insert generated code for reload handler here
		            //// UIGEN:ISSUE2_RELOAD_END

                } else if ( token.equalsIgnoreCase("Issue2_Priority")) {
                    String valueStr = tokenizer.nextToken();
                    if ( valueStr.equalsIgnoreCase("Priority_1") )
                        Issue2_PriorityRadioGroup.check(R.id.Issue2_PriorityPriority_1RadioButton);
                    else if ( valueStr.equalsIgnoreCase("Priority_2") )
                        Issue2_PriorityRadioGroup.check(R.id.Issue2_PriorityPriority_2RadioButton);
                    else if ( valueStr.equalsIgnoreCase("Priority_3") )
                        Issue2_PriorityRadioGroup.check(R.id.Issue2_PriorityPriority_3RadioButton);
                } else if ( token.equalsIgnoreCase("Issue2_Description")) {
                    Issue2_DescriptionEntry.setText(tokenizer.nextToken());
                } else if ( token.equalsIgnoreCase("Issue3_Summary")) {
                    Issue3_SummaryEntry.setText(tokenizer.nextToken());
                } else if ( token.equalsIgnoreCase("Issue3_Taskgroup")) {
                    String valueStr = tokenizer.nextToken();
                    
		            //// UIGEN:ISSUE3_RELOAD_BEGIN - insert generated code for reload handler here
		            //// UIGEN:ISSUE3_RELOAD_END
                    
                } else if ( token.equalsIgnoreCase("Issue3_Priority")) {
                    String valueStr = tokenizer.nextToken();
                    if ( valueStr.equalsIgnoreCase("Priority_1") )
                        Issue3_PriorityRadioGroup.check(R.id.Issue3_PriorityPriority_1RadioButton);
                    else if ( valueStr.equalsIgnoreCase("Priority_2") )
                        Issue3_PriorityRadioGroup.check(R.id.Issue3_PriorityPriority_2RadioButton);
                    else if ( valueStr.equalsIgnoreCase("Priority_3") )
                        Issue3_PriorityRadioGroup.check(R.id.Issue3_PriorityPriority_3RadioButton);
                } else if ( token.equalsIgnoreCase("Issue3_Description")) {
                    Issue3_DescriptionEntry.setText(tokenizer.nextToken());
                } else if ( token.equalsIgnoreCase("Match_Summary")) {
                    Match_SummaryEntry.setText(tokenizer.nextToken());
	            	
		            //// UICUSTOM:RELOAD_BEGIN - insert custom code for reload handler here
		            //// UICUSTOM:RELOAD_END
	            		            	
				}
			}
		} catch (Exception e) {
            Toast.makeText(DebriefAppActivity.this, e.toString(), Toast.LENGTH_LONG).show();
            return false;
		}
		return true;
    }

	public void discardScoutingData()
	{
        //TeamEntry.setText("");
        NotesEntry.setText("");
        
        MatchEntry.setText("");
        Issue1_SummaryEntry.setText("");
        
        //// UIGEN:ISSUE1_DISCARD_BEGIN - insert generated code for discard handler here                
        //// UIGEN:ISSUE1_DISCARD_END
        
        Issue1_PriorityRadioGroup.clearCheck();
        Issue1_DescriptionEntry.setText("");
        Issue2_SummaryEntry.setText("");
        
        //// UIGEN:ISSUE2_DISCARD_BEGIN - insert generated code for discard handler here                
        //// UIGEN:ISSUE2_DISCARD_END

        Issue2_PriorityRadioGroup.clearCheck();
        Issue2_DescriptionEntry.setText("");
        Issue3_SummaryEntry.setText("");
        
        //// UIGEN:ISSUE3_DISCARD_BEGIN - insert generated code for discard handler here                
        //// UIGEN:ISSUE3_DISCARD_END
        
        Issue3_PriorityRadioGroup.clearCheck();
        Issue3_DescriptionEntry.setText("");
        Match_SummaryEntry.setText("");
        
        //// UICUSTOM:DISCARD_BEGIN - insert custom code for discard handler here                
        //// UICUSTOM:DISCARD_END
        
        deleteScoutingData( tmpFile );
	}

	
	@Override
	public void onPause() {
	    super.onPause();  // Always call the superclass method first	    
	    saveScoutingData( tmpFile, false );
	}

	@Override
	public void onResume() {
	    super.onResume();  // Always call the superclass method first

        StringBuffer buffer = new StringBuffer();
		reloadScoutingData( tmpFile, buffer );
		deleteScoutingData( tmpFile );
	}
	
	@Override
    public void onBackPressed() {
        AlertDialog.Builder builder = new AlertDialog.Builder(DebriefAppActivity.this);
        builder.setTitle("Exiting Scouting Application");
        builder.setMessage("Do you really want to exit?.").setCancelable(
                false).setPositiveButton("Quit", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                    	discardScoutingData();
                        DebriefAppActivity.this.finish();
                    }
                }).setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                    }
                });
        AlertDialog alert = builder.create();
        alert.show();
    }

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
	    MenuInflater inflater = getMenuInflater();
	    inflater.inflate(R.menu.mainmenu, menu);
	    return true;
	}
	
	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
	    switch (item.getItemId()) {
	    case R.id.EditSettings:
	        LoadDeviceConfiguration(true);
	    	break;
	    case R.id.EditCompetitionSettings:
	        LoadCompetitionConfiguration(true);
	    	break;
	    case R.id.LoadCompetitionSettings:
	        DownloadCompetitionConfiguration();
	    	break;
	    case R.id.RetrieveEventData:
	        DownloadCompetitionData("EventData");
	    	break;
	    case R.id.RetrieveTeamData:
	        DownloadCompetitionData("EventData/Teamdata");
	    	break;
	    case R.id.RetrieveMatchSchedule:
	    	DownloadMatchSchedule();
	    	break;
	    case R.id.LoadMatchSchedule:
	    	LoadMatchSchedule();
	    	break;
		default:
		    break;
	    }
	    return true;
	}

	// Helper function to wrap the cloud and pit sync operations
	private void SyncFiles( String syncControl ) {
		String[] directoriesToSync = null;
		
		if (sync_text_files && sync_media_files) {
			directoriesToSync = new String[3];
			directoriesToSync[0] = competition_directory + "/ScoutingData/";
			directoriesToSync[1] = competition_directory + "/ScoutingPictures/";
			directoriesToSync[2] = competition_directory + "/ScoutingPictures/Thumbnails/";
		} else if ( sync_text_files ) {
			directoriesToSync = new String[1];
			directoriesToSync[0] = competition_directory + "/ScoutingData/";
		} else if ( sync_media_files ) {
			directoriesToSync = new String[2];
			directoriesToSync[0] = competition_directory + "/ScoutingPictures/";
			directoriesToSync[1] = competition_directory + "/ScoutingPictures/Thumbnails/";
		}
		
		if ( directoriesToSync != null ) {
			if (syncControl.equalsIgnoreCase("Bluetooth")) {
	    		new BluetoothSyncTask(DebriefAppActivity.this, device_name, sync_control).execute(directoriesToSync);
			} else {
	    		new HttpSyncTask(DebriefAppActivity.this, device_name, host_addr, sync_control).execute(directoriesToSync);
			}
		} else {
			Toast.makeText(DebriefAppActivity.this, "No Folders Selected To Sync", Toast.LENGTH_LONG).show();        			
		}
	} 

	/** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);


        // Look for a device configuration file and prompt the user for settings if
        // there isn't a file there.
        LoadDeviceConfiguration(false);
        LoadCompetitionConfiguration(false);

        // Load the task group email lists from the config file
        LoadTaskGroupLists();
        
        // once the device configuration is loaded, here's where we could modify the
        // background or other styling effects
        //getWindow().getDecorView().setBackgroundColor(Color.RED);
        
        // declare field variables for everything we care about on the user interface
        SaveButton = (Button) findViewById(R.id.SaveButton);
        ReloadButton = (Button) findViewById(R.id.ReloadButton);
        ScouterEntry = (EditText) findViewById(R.id.ScouterEntry);
        TeamEntry = (EditText) findViewById(R.id.TeamEntry);
        NotesEntry = (EditText) findViewById(R.id.NotesEntry);
        PitSyncButton = (Button) findViewById(R.id.PitSyncButton);
        CloudSyncButton = (Button) findViewById(R.id.CloudSyncButton);

        MatchEntry = (EditText) findViewById(R.id.MatchEntry);
        Issue1_NotifyButton = (Button) findViewById(R.id.Issue1_NotifyLabel);
        Issue1_SummaryEntry = (EditText) findViewById(R.id.Issue1_SummaryEntry);
        
        //// UIGEN:ISSUE1_CHECKBOX_INIT_BEGIN - insert generated code for checkbox variable init here                
        //// UIGEN:ISSUE1_CHECKBOX_INIT_END
        
        Issue1_PriorityRadioGroup = (RadioGroup) findViewById(R.id.Issue1_PriorityRadioGroup);
        Issue1_PriorityPriority_1RadioButton = (RadioButton) findViewById(R.id.Issue1_PriorityPriority_1RadioButton);
        Issue1_PriorityPriority_2RadioButton = (RadioButton) findViewById(R.id.Issue1_PriorityPriority_2RadioButton);
        Issue1_PriorityPriority_3RadioButton = (RadioButton) findViewById(R.id.Issue1_PriorityPriority_3RadioButton);
        Issue1_DescriptionEntry = (EditText) findViewById(R.id.Issue1_DescriptionEntry);
        Issue2_NotifyButton = (Button) findViewById(R.id.Issue2_NotifyLabel);
        Issue2_SummaryEntry = (EditText) findViewById(R.id.Issue2_SummaryEntry);

        //// UIGEN:ISSUE2_CHECKBOX_INIT_BEGIN - insert generated code for checkbox variable init here                
        //// UIGEN:ISSUE2_CHECKBOX_INIT_END

        Issue2_PriorityRadioGroup = (RadioGroup) findViewById(R.id.Issue2_PriorityRadioGroup);
        Issue2_PriorityPriority_1RadioButton = (RadioButton) findViewById(R.id.Issue2_PriorityPriority_1RadioButton);
        Issue2_PriorityPriority_2RadioButton = (RadioButton) findViewById(R.id.Issue2_PriorityPriority_2RadioButton);
        Issue2_PriorityPriority_3RadioButton = (RadioButton) findViewById(R.id.Issue2_PriorityPriority_3RadioButton);
        Issue2_DescriptionEntry = (EditText) findViewById(R.id.Issue2_DescriptionEntry);
        Issue3_NotifyButton = (Button) findViewById(R.id.Issue3_NotifyLabel);
        Issue3_SummaryEntry = (EditText) findViewById(R.id.Issue3_SummaryEntry);
        
        //// UIGEN:ISSUE3_CHECKBOX_INIT_BEGIN - insert generated code for checkbox variable init here                
        //// UIGEN:ISSUE3_CHECKBOX_INIT_END

        Issue3_PriorityRadioGroup = (RadioGroup) findViewById(R.id.Issue3_PriorityRadioGroup);
        Issue3_PriorityPriority_1RadioButton = (RadioButton) findViewById(R.id.Issue3_PriorityPriority_1RadioButton);
        Issue3_PriorityPriority_2RadioButton = (RadioButton) findViewById(R.id.Issue3_PriorityPriority_2RadioButton);
        Issue3_PriorityPriority_3RadioButton = (RadioButton) findViewById(R.id.Issue3_PriorityPriority_3RadioButton);
        Issue3_DescriptionEntry = (EditText) findViewById(R.id.Issue3_DescriptionEntry);
        Match_SummaryEntry = (EditText) findViewById(R.id.Match_SummaryEntry);
 
        //// UIGEN:VAR_INIT_BEGIN - insert generated code for field variables initialization      
        //// UIGEN:VAR_INIT_END
        
        //// UICUSTOM:VAR_INIT_BEGIN - insert custom code for field variables initialization      
        //// UICUSTOM:VAR_INIT_END
                
    	// Processes the button click for the PitSync button        
        PitSyncButton.setOnClickListener(new OnClickListener(){
        	public void onClick(View v){
        		String syncControl = "Bluetooth";
        		SyncFiles(syncControl);
        	}
        });
	 	
        // Processes the click event for the CloudSync button
        CloudSyncButton.setOnClickListener(new OnClickListener(){
        	public void onClick(View v){
        		String syncControl = "Http";
        		SyncFiles(syncControl);	
        	}
        });

        // Processes the data entry for the Scouter field
	    ScouterEntry.setOnKeyListener(new OnKeyListener() {
            public boolean onKey(View v, int keyCode, KeyEvent event) {
            	return DebriefAppActivity.this.onKey( v, keyCode, event, ScouterEntry);
            }
        });
        
        // Processes the data entry for the Team field
	    TeamEntry.setOnKeyListener(new OnKeyListener() {
            public boolean onKey(View v, int keyCode, KeyEvent event) {
            	return DebriefAppActivity.this.onKey( v, keyCode, event, TeamEntry);
            }
        });
                        
	    NotesEntry.setOnKeyListener(new OnKeyListener() {
	    	public boolean onKey(View v, int keyCode, KeyEvent event) {
	    		return DebriefAppActivity.this.onKey( v, keyCode, event, NotesEntry);
	    	}
	    });

	    // Method to respond to button clicks for the save button. This
        // method will attempt to store the user entered settings to a file
        // whose name is derived from some of the settings
        SaveButton.setOnClickListener(new OnClickListener() {
            public void onClick(View v) {
            	// Perform action on clicks
        		try {

        			// make sure that a scouter, team and match has been 
        			// specified. we need these fields to build the filename
        			// and to ensure that we can associate a report to a person
        			if ( ScouterEntry.getText().toString().isEmpty() ) {
                        new AlertDialog.Builder(DebriefAppActivity.this)
                        .setTitle("Error!")
                        .setMessage("Please Enter Scouter's Name")
                        .setNeutralButton("OK", null)
                        .show();                			    				
        				throw new Exception( "No Scouter Specified!" );
        			}	
        			
        			if ( TeamEntry.getText().toString().isEmpty() ) {
                        new AlertDialog.Builder(DebriefAppActivity.this)
                        .setTitle("Error!")
                        .setMessage("Please Enter A Team Number")
                        .setNeutralButton("OK", null)
                        .show();
                        return;
        			}
        			                   
                    // build up the desired filename based on field entries
        		    //// UIGEN:BUILD_FILENAME_BEGIN - insert generated code for the buildFilename() call
                    final String filename = buildDebriefFilename( "Debrief", "Match", MatchEntry.getText().toString() );
        		    //// UIGEN:BUILD_FILENAME_END
                    saveScoutingData( filename, true );
                    unsavedChanges = false;
        			Toast.makeText(DebriefAppActivity.this, "Scouting Data Saved To File: " + filename, Toast.LENGTH_LONG).show();

        		} catch (Exception e) {
                    Toast.makeText(DebriefAppActivity.this, e.toString(), Toast.LENGTH_SHORT).show();
        		}
            }
        });

		// Method to respond to button clicks for the reload button. This
        // method will attempt to reload the configuration to the user interface
        // from a previously stored file
        ReloadButton.setOnClickListener(new OnClickListener() {
            public void reloadData() {
                try {
        			// build a filename based on the field entries
        		    //// UIGEN:BUILD_FILENAME_BEGIN - insert generated code for the buildFilename() call
                    final String filename = buildDebriefFilename( "Debrief", "Match", MatchEntry.getText().toString() );
        		    //// UIGEN:BUILD_FILENAME_END
                    StringBuffer buffer = new StringBuffer();
        			
        			if ( !reloadScoutingData( filename, buffer ) ) {
        				throw new Exception( "Error Reading Scouting Data From: " + filename );
        			}
        			
        			unsavedChanges = false;
        			
        			// And, write the full buffer representing the raw file that has been reloaded
        			// to the text view object on the user interface
                    new AlertDialog.Builder(DebriefAppActivity.this)
                    .setTitle("Reload: " + filename)
                    .setMessage(buffer.toString())
                    .setNeutralButton("OK", null)
                    .show();                			
                    // Perform action on clicks
                    Toast.makeText(DebriefAppActivity.this, "Scouting Data Reloaded From: " + filename, Toast.LENGTH_LONG).show();

        		} catch (Exception e) {
                    Toast.makeText(DebriefAppActivity.this, e.toString(), Toast.LENGTH_LONG).show();
        		}
            }
            public void onClick(View v) {
                // Perform action on clicks
                try {                	
        			if ( ScouterEntry.getText().toString().isEmpty() ) {
                        new AlertDialog.Builder(DebriefAppActivity.this)
                        .setTitle("Error!")
                        .setMessage("Please Enter Scouter's Name")
                        .setNeutralButton("OK", null)
                        .show();                			    				
        				throw new Exception( "No Scouter Specified!" );
        			}
        			
        			if ( TeamEntry.getText().toString().isEmpty() ) {
                        new AlertDialog.Builder(DebriefAppActivity.this)
                        .setTitle("Error!")
                        .setMessage("Please Enter A Team Number")
                        .setNeutralButton("OK", null)
                        .show();
                        return;
        			}
        			
        			if ( MatchEntry.getText().toString().isEmpty() ) {
                        new AlertDialog.Builder(DebriefAppActivity.this)
                        .setTitle("Error!")
                        .setMessage("Please Enter A Match Number")
                        .setNeutralButton("OK", null)
                        .show();
                        return;
        			}
        			                   
                    if ( unsavedChanges == true ) {

                		new AlertDialog.Builder(DebriefAppActivity.this)
	                    .setTitle("Reloading Scouting Data")
	                    .setMessage("Do You Really Want To Do This?")
	                    .setNegativeButton("No", new DialogInterface.OnClickListener() {
	                        public void onClick(DialogInterface dialog, int whichButton) {
	                        	Toast.makeText(DebriefAppActivity.this, "Reload Cancelled", Toast.LENGTH_LONG).show();
	                        }
	                    })
	                    .setPositiveButton("Yes", new DialogInterface.OnClickListener() {
	                        public void onClick(DialogInterface dialog, int whichButton) {
	                        	reloadData();
	                        }
	                    })
	                    .show();                      
	                } else {
	                	reloadData();
	                }                
	    		} catch (Exception e) {
	                Toast.makeText(DebriefAppActivity.this, e.toString(), Toast.LENGTH_LONG).show();
	    		}
            }
        });
        
        // Method to respond to button clicks for the discard button. This
        // method will clear all settings that a user has entered on the 
		// user interface        
		final Button discardButton = (Button) findViewById(R.id.DiscardButton);
        discardButton.setOnClickListener(new OnClickListener() {
            public void onClick(View v) {
                // Perform action on clicks
                if ( unsavedChanges == true ) {
                    new AlertDialog.Builder(DebriefAppActivity.this)
                    .setTitle("Discarding Unsaved Scouting Data")
                    .setMessage("Do You Really Want To Do This?")
                    .setNegativeButton("No", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int whichButton) {
                            Toast.makeText(DebriefAppActivity.this, "Discard Cancelled", Toast.LENGTH_LONG).show();
                        }
                    })
                    .setNeutralButton("Yes", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int whichButton) {
                        	discardScoutingData();
                        	unsavedChanges = false;
                            Toast.makeText(DebriefAppActivity.this, "Scouting Data Discarded!", Toast.LENGTH_LONG).show();	
                        }
                    })
                    .setPositiveButton("Save", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int whichButton) {
                		    //// UIGEN:BUILD_FILENAME_BEGIN - insert generated code for the buildFilename() call
                            final String filename = buildDebriefFilename( "Debrief", "Match", MatchEntry.getText().toString() );
                		    //// UIGEN:BUILD_FILENAME_END
                            saveScoutingData( filename, true );
                        	discardScoutingData();
                            unsavedChanges = false;
                			Toast.makeText(DebriefAppActivity.this, "Scouting Data Saved To File: " + filename, Toast.LENGTH_LONG).show();
                        }
                    })
                   .show();                      
                } else {
                	discardScoutingData();
                	unsavedChanges = false;
                    Toast.makeText(DebriefAppActivity.this, "Scouting Data Cleared!", Toast.LENGTH_LONG).show();	
                }                
            }
        });
        
        //// UIGEN:HANDLERS_BEGIN - insert generated code for input handlers
        // Processes the button click for the Issue1_Notify button
        Issue1_NotifyButton.setOnClickListener(new OnClickListener(){
            public void onClick(View v){
                Issue1_NotifyButtonHandler();
            }
        });
        // Processes the button click for the Issue2_Notify button
        Issue2_NotifyButton.setOnClickListener(new OnClickListener(){
            public void onClick(View v){
                Issue2_NotifyButtonHandler();
            }
        });
        // Processes the button click for the Issue3_Notify button
        Issue3_NotifyButton.setOnClickListener(new OnClickListener(){
            public void onClick(View v){
                Issue3_NotifyButtonHandler();
            }
        });
        //// UIGEN:HANDLERS_END

        //// UICUSTOM:HANDLERS_BEGIN - insert custom code for input handlers
        //// UICUSTOM:HANDLERS_END

    }
    
    //// UIGEN:HELPER_FUNCTIONS_BEGIN - insert generated code for helper functions
    //// UIGEN:HELPER_FUNCTIONS_END

    private void addArrayToSet( String array[], Set<String> set ) {
    	List<String> list = Arrays.asList(array);
       	set.addAll(list);
    }
    
    private void SendTextNotifications( String list[], String subject, String body ) {

/*		this snippet of code needs to be completed, but this uses the internal
 * 		java mailer to send the mail rather than using an intent. the benefit to
 *      this approach would be that it will avoid requiring the user to hit send 
 *      twice to get the messages to go out.
    	try {   
            GMailSender sender = new GMailSender("username@gmail.com", "password");
            sender.sendMail(subject,   
                    body,   
                    "user@gmail.com",   
                    "user@yahoo.com");   
        } catch (Exception e) {   
            Log.e("SendMail", e.getMessage(), e);   
        } 
*/        

        Intent emailIntent = new Intent(android.content.Intent.ACTION_SEND);
        emailIntent.setType("plain/text");
        emailIntent.putExtra(android.content.Intent.EXTRA_EMAIL, list);
        emailIntent.putExtra(android.content.Intent.EXTRA_CC, Master_list);
        emailIntent.putExtra(android.content.Intent.EXTRA_SUBJECT, subject);
        emailIntent.putExtra(android.content.Intent.EXTRA_TEXT, body);
    	
        startActivity(emailIntent);

    }

    private void SendSlackNotification(String issue, String summary, String priority, String groups, String description ) {
    	
    	String matchStr = "*Match:* " + MatchEntry.getText().toString();
       	String priorityStr = "*Priority:* " + priority;
		String taskgroupStr = "*Taskgroups:* " + groups;
    	String summaryStr = "*Issue Summary:* " + summary;
    	String descriptionStr = "*Description:* " + description;

    	// format the Slack message as a single formatted text string
    	String slackMsg = matchStr + ", " + priorityStr + "\n";
    	slackMsg += summaryStr + "\n";
    	slackMsg += taskgroupStr + "\n";
    	slackMsg += "\n" + descriptionStr + "\n";
    	
    	// instantiate the Slack interface task passing in the webhook URL and the formatted message
    	String webHookUrl = "https://hooks.slack.com/services/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";
    	new SlackIntfTask(DebriefAppActivity.this, webHookUrl).execute(slackMsg);

        Toast.makeText(DebriefAppActivity.this, "Sending Issue " + issue + "Slack Notification", Toast.LENGTH_LONG).show();
    }
    
    private void Issue1_NotifyButtonHandler() {
		
    	Set<String> notifySet = new HashSet<String>();
		boolean groupChecked = false;
		String notifyGroups = "";
		
/* Uncomment for Email and Text Notifications
        String msgBody = Issue1_DescriptionEntry.getText().toString();
    	String subject;
    	if (Issue1_PriorityPriority_1RadioButton.isChecked())
    	    subject = "[XXX] ";
    	else if (Issue1_PriorityPriority_2RadioButton.isChecked())
    	    subject = "[XXX] ";
    	else if (Issue1_PriorityPriority_3RadioButton.isChecked())
    	    subject = "[XXX] ";
    	else
    		subject = "[XXX] ";
		subject += Issue1_SummaryEntry.getText().toString();
*/
		try {
	        //// UIGEN:ISSUE1_IS_CHECKED_BEGIN - insert generated code for checking status of taskgroup checkboxes
	        //// UIGEN:ISSUE1_IS_CHECKED_END
		} catch (Exception e) {
			
		}
		
/* Uncomment for Email and Text Notifications
        if ( notifyGroups.length() > 12 ) {
        	notifyGroups = notifyGroups.substring(0,12);
        	notifyGroups += "...";
        }
    	subject = subject.replace("XXX", notifyGroups);
		SendNotifications( notifySet.toArray(new String[notifySet.size()]), subject, msgBody);
*/

		// Slack Notifications
		String issue_num = "1";
    	String priority = "";
    	if (Issue1_PriorityPriority_1RadioButton.isChecked())
    		priority = "High";
    	else if (Issue1_PriorityPriority_2RadioButton.isChecked())
    		priority = "Medium";
    	else if (Issue1_PriorityPriority_3RadioButton.isChecked())
    		priority = "Low";
		String summary = Issue1_SummaryEntry.getText().toString();
		String description = Issue1_DescriptionEntry.getText().toString();
		        
		SendSlackNotification( issue_num, summary, priority, notifyGroups, description);

    }
    
    private void Issue2_NotifyButtonHandler() {
        
    	Set<String> notifySet = new HashSet<String>();
		boolean groupChecked = false;
		String notifyGroups = "";
		
/* Uncomment for Email and Text Notifications
        String msgBody = Issue2_DescriptionEntry.getText().toString();
    	String subject;
    	if (Issue2_PriorityPriority_1RadioButton.isChecked())
    	    subject = "[XXX] ";
    	else if (Issue2_PriorityPriority_2RadioButton.isChecked())
    	    subject = "[XXX] ";
    	else if (Issue2_PriorityPriority_3RadioButton.isChecked())
    	    subject = "[XXX] ";
    	else
    		subject = "[XXX] ";
		subject += Issue2_SummaryEntry.getText().toString();
*/
		try {
	        //// UIGEN:ISSUE2_IS_CHECKED_BEGIN - insert generated code for checking status of taskgroup checkboxes
	        //// UIGEN:ISSUE2_IS_CHECKED_END
		} catch (Exception e) {
			
		}
		
/* Uncomment for Email and Text Notifications		
        if ( notifyGroups.length() > 12 ) {
        	notifyGroups = notifyGroups.substring(0,12);
        	notifyGroups += "...";
        }
    	subject = subject.replace("XXX", notifyGroups);
		SendNotifications( notifySet.toArray(new String[notifySet.size()]), subject, msgBody);
*/

		// Slack Notifications
		String issue_num = "2";
    	String priority = "";
    	if (Issue2_PriorityPriority_1RadioButton.isChecked())
    		priority = "High";
    	else if (Issue2_PriorityPriority_2RadioButton.isChecked())
    		priority = "Medium";
    	else if (Issue2_PriorityPriority_3RadioButton.isChecked())
    		priority = "Low";
		String summary = Issue2_SummaryEntry.getText().toString();
		String description = Issue2_DescriptionEntry.getText().toString();
		        
		SendSlackNotification( issue_num, summary, priority, notifyGroups, description);

    }
    
    private void Issue3_NotifyButtonHandler() {
        
    	Set<String> notifySet = new HashSet<String>();
		boolean groupChecked = false;
		String notifyGroups = "";
		
/* Uncomment for Email and Text Notifications
        String msgBody = Issue3_DescriptionEntry.getText().toString();
    	String subject;
    	if (Issue3_PriorityPriority_1RadioButton.isChecked())
    	    subject = "[XXX] ";
    	else if (Issue3_PriorityPriority_2RadioButton.isChecked())
    	    subject = "[XXX] ";
    	else if (Issue3_PriorityPriority_3RadioButton.isChecked())
    	    subject = "[XXX] ";
    	else
    		subject = "[XXX] ";
		subject += Issue3_SummaryEntry.getText().toString();
*/
		try {
	        //// UIGEN:ISSUE3_IS_CHECKED_BEGIN - insert generated code for checking status of taskgroup checkboxes
	        //// UIGEN:ISSUE3_IS_CHECKED_END
		} catch (Exception e) {
			
		}
		
/* Uncomment for Email and Text Notifications		
        if ( notifyGroups.length() > 12 ) {
        	notifyGroups = notifyGroups.substring(0,12);
        	notifyGroups += "...";
        }
    	subject = subject.replace("XXX", notifyGroups);
		SendNotifications( notifySet.toArray(new String[notifySet.size()]), subject, msgBody);
*/

		// Slack Notifications
		String issue_num = "3";
    	String priority = "";
    	if (Issue3_PriorityPriority_1RadioButton.isChecked())
    		priority = "High";
    	else if (Issue3_PriorityPriority_2RadioButton.isChecked())
    		priority = "Medium";
    	else if (Issue3_PriorityPriority_3RadioButton.isChecked())
    		priority = "Low";
		String summary = Issue3_SummaryEntry.getText().toString();
		String description = Issue3_DescriptionEntry.getText().toString();
		        
		SendSlackNotification( issue_num, summary, priority, notifyGroups, description);

    }
    
    private void LoadMatchSchedule( ) {

    	try {
    			
    		Gson gson = new Gson();

    		// This code block will attempt to read the device configuration
    		// file containing the device name, id, and other configuration 
    		// parameters. If the file is there, the information is read and
    		// stored for later access by the application itself
    		File directory = Environment.getExternalStorageDirectory();
			File myDir = new File(directory + "/" + competition_directory + "/EventData/");
			File myFile = new File(myDir, "matchschedule.json");
	        FileReader myReader = new FileReader(myFile);
			BufferedReader reader = new BufferedReader(myReader);
			
			// Load the match results object from the json file
			matchSchedule = gson.fromJson(reader, MatchSchedule.class);
			
			reader.close();

			Toast.makeText(DebriefAppActivity.this, "Match Schedule Loaded", Toast.LENGTH_SHORT).show();

    	} catch (Exception e) {
			e.printStackTrace();
    	}
    	
	}
	
	private String[] FindMatchEntry( List<String[]>matches, String match_str ) {
		String[] matchEntry = null;
		int matchOffset = 1;
		Boolean found = false;
		
		for ( int i=0; i<matches.size() && !found; i++ ) {
			matchEntry = matches.get(i);
			if ( matchEntry[matchOffset].equals(match_str) ) {
				found = true;
			}
		}
		
		if ( !found )
			matchEntry = null;
		
		return matchEntry;
	}
	
	private String GetTeamFromMatchSchedule( String round, String alliance, String position_str, String match_str ) {
		int offset = 0;
		int position = Integer.parseInt(position_str);
		String team = "0";
		String[] matchEntry = null; 
		
		if ( alliance.equals("Red") ) {
			offset = 2;
		} else {
			offset = 5;
		}
		offset += (position-1);
		
		if ( matchSchedule != null) {
			if ( round.equals("Qual") ) {
				int match = Integer.parseInt(match_str);
				matchEntry = matchSchedule.qualification.get(match-1);
			} else if ( round.equals("Quarters") ) {
				matchEntry = FindMatchEntry( matchSchedule.quarter_finals, match_str );				
			} else if ( round.equals("Semis") ) {
				matchEntry = FindMatchEntry( matchSchedule.semi_finals, match_str );				
			} else if ( round.equals("Finals") ) {
				try {
					int match = Integer.parseInt(match_str);
					matchEntry = matchSchedule.finals.get(match-1);
				} catch (Exception e) {
					matchEntry = FindMatchEntry( matchSchedule.finals, match_str );
				}
			}
			
			if ( matchEntry != null ) {
				team = matchEntry[offset];
			}
			
		} else {
            new AlertDialog.Builder(DebriefAppActivity.this)
            .setTitle("No Match Schedule Loaded")
            .setMessage("Do You Want To Load The Match Schedule?")
            .setNegativeButton("No", new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface dialog, int whichButton) {
                    Toast.makeText(DebriefAppActivity.this, "Cannot Set Team From Schedule", Toast.LENGTH_LONG).show();
                }
            })
            .setPositiveButton("Yes", new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface dialog, int whichButton) {
                	LoadMatchSchedule();
                }
            })
            .show();                      
		}
		
		return team;
	}
    
}


