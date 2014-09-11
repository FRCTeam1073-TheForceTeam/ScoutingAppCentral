package org.team1073.scouting;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.StringTokenizer;

import android.app.Activity;
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




public class ScoutingAppActivity extends Activity {
	private String device_name="unknown";
	private String device_id="un";
	private String competition_directory="Test2014";
	private String host_addr = "";
	private String sync_method = "Bluetooth";
	private String sync_control = "Upload_Only";
	private Boolean sync_text_files = true;
	private Boolean sync_media_files = false;
	private Boolean unsavedChanges = false;
	
    final String tmpFile = "ScoutingData.tmp";

	private void DownloadCompetitionConfiguration( ) {
		// create an asynchronous task to transfer the scouting data and media files
		// to the server. If no host IP address has been specified, use bluetooth,
		// otherwise use http.
		String download_control = "Download_Updates";
		if (sync_method.equalsIgnoreCase("Bluetooth")) {
    		new BluetoothSyncTask(ScoutingAppActivity.this, device_name, download_control).execute(
    				"/ScoutingConfig/");
		} else {
    		new HttpSyncTask(ScoutingAppActivity.this, device_name, host_addr, download_control).execute(
    				"/ScoutingConfig/");
		}
    
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
                	competition_directory = tokenizer.nextToken();
                	
                	// augment the application title with the competition name
                	String app_title_base = getString(R.string.app_label) + " - ";
                	ScoutingAppActivity.this.setTitle(app_title_base + competition_directory);
                }
			}
    	} catch (Exception e) {
    		showDialog = true;
    	}
    	
    	if ( showDialog == true ) {
    		// The configuration file is not there, so create a pop up dialog
    		// to prompt the user for the necessary device configuration information
    		// needed to continue with the application.
	        Dialog dialog = new Dialog(ScoutingAppActivity.this);
	        dialog.setContentView(R.layout.competitiondialog);
	        dialog.setTitle("Please Enter Competition Information");
	        dialog.setCancelable(true);
	        Button button = (Button) dialog.findViewById(R.id.CompOkButton);
	        final EditText CompetitionNameEntry = (EditText) dialog.findViewById(R.id.CompetitionNameEntry);     

	        CompetitionNameEntry.setText(competition_directory);
	        
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
	                    
	                    if ( !CompetitionNameEntry.getText().toString().isEmpty() )
	                        buffer.append("Competition=" + CompetitionNameEntry.getText().toString() + eol);
	                    
						// write the formatted buffer to the file
						writer.write(buffer.toString());
						writer.close();
					} catch (Exception e) {
				        Toast.makeText(ScoutingAppActivity.this, e.toString(), Toast.LENGTH_SHORT).show();
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
	            } else if ( token.equalsIgnoreCase("HostAddr")) {
	            	host_addr = tokenizer.nextToken();
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
    	} catch (Exception e) {
    		showDialog = true;
    	}
    	
    	if ( showDialog == true ) {
    		// The configuration file is not there, so create a pop up dialog
    		// to prompt the user for the necessary device configuration information
    		// needed to continue with the application.
	        Dialog dialog = new Dialog(ScoutingAppActivity.this);
	        dialog.setContentView(R.layout.devicedialog);
	        dialog.setTitle("Please Enter Device Information");
	        dialog.setCancelable(true);
	        Button button = (Button) dialog.findViewById(R.id.DeviceOkButton);
	        final EditText DeviceNameEntry = (EditText) dialog.findViewById(R.id.DeviceNameEntry);
	        final EditText DeviceIdEntry = (EditText) dialog.findViewById(R.id.DeviceIdEntry);     
	        final EditText HostAddrEntry = (EditText) dialog.findViewById(R.id.HostAddrEntry);     
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
	        HostAddrEntry.setText(host_addr);
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
	                    if ( !HostAddrEntry.getText().toString().isEmpty() )
	                        buffer.append("HostAddr=" + HostAddrEntry.getText().toString() + eol);
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
				        Toast.makeText(ScoutingAppActivity.this, e.toString(), Toast.LENGTH_SHORT).show();
					}
	                finish();
	            }
	        });
	        //now that the dialog is set up, it's time to show it    
	        dialog.show();
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

	
	// helper function to process key actions for an EditText field
	private boolean onKey(View v, int keyCode, KeyEvent event, EditText entry) {
		unsavedChanges = true;
		// If the event is a key-down event on the "enter" button
   		if ((event.getAction() == KeyEvent.ACTION_DOWN) &&
   			(keyCode == KeyEvent.KEYCODE_ENTER)) {
   				// For now, we'll just make a toast with the entered data
   				Toast.makeText(ScoutingAppActivity.this, entry.getText(), Toast.LENGTH_SHORT).show();
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
	        Toast.makeText(ScoutingAppActivity.this, e.toString(), Toast.LENGTH_SHORT).show();
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
    private Button videoButton;
    private Button cameraButton;      
    private Button syncButton;

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
		
		//// UIGEN:SAVE_BEGIN - insert generated code for save handler here                   
		//// UIGEN:SAVE_END
		
		//// UICUSTOM:SAVE_BEGIN - insert custom code for save handler here                   
		//// UICUSTOM:SAVE_END
		
        // make sure that the filename doesn't already exist, so we don't 
        // overwrite an existing file.
        if ( doesFileExist(filename) && promptForOverwrite ) {
            new AlertDialog.Builder(ScoutingAppActivity.this)
            .setTitle("File Already Exists: " + filename)
            .setMessage("Overwrite File?")
            .setNegativeButton("No", new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface dialog, int whichButton) {
                    Toast.makeText(ScoutingAppActivity.this, "Save Cancelled", Toast.LENGTH_LONG).show();
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
	            	
		            //// UIGEN:RELOAD_BEGIN - insert generated code for reload handler here
		            //// UIGEN:RELOAD_END
	            	
		            //// UICUSTOM:RELOAD_BEGIN - insert custom code for reload handler here
		            //// UICUSTOM:RELOAD_END
	            		            	
				} else {
				}
			}
		} catch (Exception e) {
            Toast.makeText(ScoutingAppActivity.this, e.toString(), Toast.LENGTH_LONG).show();
            return false;
		}
		return true;
    }

	public void discardScoutingData()
	{
        TeamEntry.setText("");
        NotesEntry.setText("");
        
        //// UIGEN:DISCARD_BEGIN - insert generated code for discard handler here                
        //// UIGEN:DISCARD_END
        
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
        AlertDialog.Builder builder = new AlertDialog.Builder(ScoutingAppActivity.this);
        builder.setTitle("Exiting Scouting Application");
        builder.setMessage("Do you really want to exit?.").setCancelable(
                false).setPositiveButton("Quit", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                    	discardScoutingData();
                        ScoutingAppActivity.this.finish();
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
		    default:
		      break;
	    }
	    return true;
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

        // declare field variables for everything we care about on the user interface
        SaveButton = (Button) findViewById(R.id.SaveButton);
        ReloadButton = (Button) findViewById(R.id.ReloadButton);
        ScouterEntry = (EditText) findViewById(R.id.ScouterEntry);
        TeamEntry = (EditText) findViewById(R.id.TeamEntry);
        NotesEntry = (EditText) findViewById(R.id.NotesEntry);
        videoButton = (Button) findViewById(R.id.VideoButton);
        cameraButton = (Button) findViewById(R.id.CameraButton);      
        syncButton = (Button) findViewById(R.id.SyncButton);

        //// UIGEN:VAR_INIT_BEGIN - insert generated code for field variables initialization      
        //// UIGEN:VAR_INIT_END
        
        //// UICUSTOM:VAR_INIT_BEGIN - insert custom code for field variables initialization      
        //// UICUSTOM:VAR_INIT_END
        
    	// Processes the button click for the camera button
        cameraButton.setOnClickListener(new OnClickListener(){
        	public void onClick(View v){
        		if ( !TeamEntry.getText().toString().isEmpty() ) {
            		recordMedia(TeamEntry.getText().toString(), MediaStore.ACTION_IMAGE_CAPTURE);
        		} else {
                    new AlertDialog.Builder(ScoutingAppActivity.this)
                    .setTitle("Error!")
                    .setMessage("Team Not Specified")
                    .setNeutralButton("OK", null)
                    .show();                			
        		}
        	}
        });
        
    	// Processes the button click for the video button        
        videoButton.setOnClickListener(new OnClickListener(){
        	public void onClick(View v){
        		if ( !TeamEntry.getText().toString().isEmpty() ) {
            		recordMedia(TeamEntry.getText().toString(), MediaStore.ACTION_VIDEO_CAPTURE);
        		} else {
                    new AlertDialog.Builder(ScoutingAppActivity.this)
                    .setTitle("Error!")
                    .setMessage("Team Not Specified")
                    .setNeutralButton("OK", null)
                    .show();                			
        		}
        	}
        });

        // Processes the click event for the Sync button
        syncButton.setOnClickListener(new OnClickListener(){
        	public void onClick(View v){
        		String[] directoriesToSync = null;
        		
        		if (sync_text_files && sync_media_files) {
        			directoriesToSync = new String[2];
        			directoriesToSync[0] = competition_directory + "/ScoutingData/";
        			directoriesToSync[1] = competition_directory + "/ScoutingPictures/";
        		} else if ( sync_text_files ) {
        			directoriesToSync = new String[1];
        			directoriesToSync[0] = competition_directory + "/ScoutingData/";
	    		} else if ( sync_media_files ) {
	    			directoriesToSync = new String[1];
	    			directoriesToSync[0] = competition_directory + "/ScoutingPictures/";
	    		}
        		
        		if ( directoriesToSync != null ) {
	        		// create an asynchronous task to transfer the scouting data and media files
	        		// to the server. If no host IP address has been specified, use bluetooth,
	        		// otherwise use http.
	        		if (sync_method.equalsIgnoreCase("Bluetooth")) {
		        		new BluetoothSyncTask(ScoutingAppActivity.this, device_name, sync_control).execute( directoriesToSync );
		        		//		competition_directory + "/ScoutingData/", competition_directory + "/ScoutingPictures/");
	        		} else {
		        		new HttpSyncTask(ScoutingAppActivity.this, device_name, host_addr, sync_control).execute( directoriesToSync );
		        		//		competition_directory + "/ScoutingData/", competition_directory + "/ScoutingPictures/");
	        		}
        		} else {
        			Toast.makeText(ScoutingAppActivity.this, "No Folders Selected To Sync", Toast.LENGTH_LONG).show();        			
        		}
        	} 
        });

        // Processes the data entry for the Scouter field
	    ScouterEntry.setOnKeyListener(new OnKeyListener() {
            public boolean onKey(View v, int keyCode, KeyEvent event) {
            	return ScoutingAppActivity.this.onKey( v, keyCode, event, ScouterEntry);
            }
        });
        
        // Processes the data entry for the Team field
	    TeamEntry.setOnKeyListener(new OnKeyListener() {
            public boolean onKey(View v, int keyCode, KeyEvent event) {
            	return ScoutingAppActivity.this.onKey( v, keyCode, event, TeamEntry);
            }
        });
                        
	    NotesEntry.setOnKeyListener(new OnKeyListener() {
	    	public boolean onKey(View v, int keyCode, KeyEvent event) {
	    		return ScoutingAppActivity.this.onKey( v, keyCode, event, NotesEntry);
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
                        new AlertDialog.Builder(ScoutingAppActivity.this)
                        .setTitle("Error!")
                        .setMessage("Please Enter Scouter's Name")
                        .setNeutralButton("OK", null)
                        .show();                			    				
        				throw new Exception( "No Scouter Specified!" );
        			}	
        			
        			if ( TeamEntry.getText().toString().isEmpty() ) {
                        new AlertDialog.Builder(ScoutingAppActivity.this)
                        .setTitle("Error!")
                        .setMessage("Please Enter A Team Number")
                        .setNeutralButton("OK", null)
                        .show();
                        return;
        			}
        			                   
                    // build up the desired filename based on field entries
        		    //// UIGEN:BUILD_FILENAME_BEGIN - insert generated code for the buildFilename() call
                    final String filename = buildFilename( TeamEntry, "Base", "" );
        		    //// UIGEN:BUILD_FILENAME_END
                    saveScoutingData( filename, true );
                    unsavedChanges = false;
        			Toast.makeText(ScoutingAppActivity.this, "Scouting Data Saved To File: " + filename, Toast.LENGTH_LONG).show();

        		} catch (Exception e) {
                    Toast.makeText(ScoutingAppActivity.this, e.toString(), Toast.LENGTH_SHORT).show();
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
                    final String filename = buildFilename( TeamEntry, "Base", "" );
        		    //// UIGEN:BUILD_FILENAME_END
                    StringBuffer buffer = new StringBuffer();
        			
        			if ( !reloadScoutingData( filename, buffer ) ) {
        				throw new Exception( "Error Reading Scouting Data From: " + filename );
        			}
        			
        			unsavedChanges = false;
        			
        			// And, write the full buffer representing the raw file that has been reloaded
        			// to the text view object on the user interface
                    new AlertDialog.Builder(ScoutingAppActivity.this)
                    .setTitle("Reload: " + filename)
                    .setMessage(buffer.toString())
                    .setNeutralButton("OK", null)
                    .show();                			
                    // Perform action on clicks
                    Toast.makeText(ScoutingAppActivity.this, "Scouting Data Reloaded From: " + filename, Toast.LENGTH_LONG).show();

        		} catch (Exception e) {
                    Toast.makeText(ScoutingAppActivity.this, e.toString(), Toast.LENGTH_LONG).show();
        		}
            }
            public void onClick(View v) {
                // Perform action on clicks
                try {                	
        			if ( TeamEntry.getText().toString().isEmpty() ) {
                        new AlertDialog.Builder(ScoutingAppActivity.this)
                        .setTitle("Error!")
                        .setMessage("Please Enter A Team Number")
                        .setNeutralButton("OK", null)
                        .show();
                        return;
        			}
        			
                    if ( unsavedChanges == true ) {

                		new AlertDialog.Builder(ScoutingAppActivity.this)
	                    .setTitle("Reloading Scouting Data")
	                    .setMessage("Do You Really Want To Do This?")
	                    .setNegativeButton("No", new DialogInterface.OnClickListener() {
	                        public void onClick(DialogInterface dialog, int whichButton) {
	                        	Toast.makeText(ScoutingAppActivity.this, "Reload Cancelled", Toast.LENGTH_LONG).show();
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
	                Toast.makeText(ScoutingAppActivity.this, e.toString(), Toast.LENGTH_LONG).show();
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
                    new AlertDialog.Builder(ScoutingAppActivity.this)
                    .setTitle("Discarding Unsaved Scouting Data")
                    .setMessage("Do You Really Want To Do This?")
                    .setNegativeButton("No", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int whichButton) {
                            Toast.makeText(ScoutingAppActivity.this, "Discard Cancelled", Toast.LENGTH_LONG).show();
                        }
                    })
                    .setNeutralButton("Yes", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int whichButton) {
                        	discardScoutingData();
                        	unsavedChanges = false;
                            Toast.makeText(ScoutingAppActivity.this, "Scouting Data Discarded!", Toast.LENGTH_LONG).show();	
                        }
                    })
                    .setPositiveButton("Save", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int whichButton) {
                		    //// UIGEN:BUILD_FILENAME_BEGIN - insert generated code for the buildFilename() call
                            final String filename = buildFilename( TeamEntry, "Base", "" );
                		    //// UIGEN:BUILD_FILENAME_END
                            saveScoutingData( filename, true );
                        	discardScoutingData();
                            unsavedChanges = false;
                			Toast.makeText(ScoutingAppActivity.this, "Scouting Data Saved To File: " + filename, Toast.LENGTH_LONG).show();
                        }
                    })
                   .show();                      
                } else {
                	discardScoutingData();
                	unsavedChanges = false;
                    Toast.makeText(ScoutingAppActivity.this, "Scouting Data Cleared!", Toast.LENGTH_LONG).show();	
                }                
            }
        });
        
        //// UIGEN:HANDLERS_BEGIN - insert generated code for input handlers
        //// UIGEN:HANDLERS_END

        //// UICUSTOM:HANDLERS_BEGIN - insert custom code for input handlers
        //// UICUSTOM:HANDLERS_END

    }
}


