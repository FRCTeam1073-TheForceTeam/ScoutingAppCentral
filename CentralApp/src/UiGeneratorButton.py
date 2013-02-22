'''
Created on Feb 19, 2012

@author: Ken
'''

from UiGeneratorControl import UiGenControl

class ButtonUiGenControl( UiGenControl ):
    attr_def = None
    config = { 'Label':None, 'Align':None }

    def __init__(self, attr_def):
        self.attr_def = attr_def
        option_str = attr_def['Options']
        options = option_str.split(':')
        for option in options:
            option_name, option_value = option.split('=')
            self.config[option_name] = option_value

    def gen_xml_string(self, above_name):
    
        xml_str =  "    <!-- Begin NAME button -->\n"

        xml_str += "    <Button\n"
        xml_str += "        android:id=\"@+id/NAMELabel\"\n"
        xml_str += "        android:layout_width=\"wrap_content\"\n"
        xml_str += "        android:layout_height=\"wrap_content\"\n"
        if self.config['Align'] == 'Left':
            xml_str += "        android:layout_alignParentLeft=\"true\"\n"
        elif self.config['Align'] == 'Center':
            xml_str += "        android:layout_centerInParent=\"true\"\n"
        else:
            xml_str += "        android:layout_alignParentRight=\"true\"\n"
            
        xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        
        if self.config['Label'] != None:
            xml_str += "        android:text=\"" + self.config['Label'] + "\" />\n"
        else:
            xml_str += "        android:text=\"NAME\" />\n"
            
        xml_str += "    <!-- End NAME line separator -->\n\n"
        return xml_str

    def gen_java_declarations_string(self):
        java_str  = "    private Button NAMEButton;\n"
        return java_str

    def gen_java_init_string(self):
        java_str  = "        NAMEButton = (Button) findViewById(R.id.NAMELabel);\n"
        return java_str

    def gen_java_button_handler(self):
        java_str = ''
        java_str += '        // Processes the button click for the NAME button\n'
        java_str += '        NAMEButton.setOnClickListener(new OnClickListener(){\n'
        java_str += '            public void onClick(View v){\n'
        java_str += '                Toast.makeText(ScoutingAppActivity.this, "NAME Button Pressed", Toast.LENGTH_LONG).show();\n'
        java_str += '            }\n'
        java_str += '        });\n'
        return java_str

    def gen_java_discard_handler(self):
        return ''

    def gen_java_save_handler(self):
        return ''

    def gen_java_reload_handler(self):
        return ''
    
