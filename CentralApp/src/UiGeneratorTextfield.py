'''
Created on Feb 4, 2012

@author: Ken
'''

from UiGeneratorControl import UiGenControl

class TextFieldUiGenControl( UiGenControl ):
    attr_def = None

    def __init__(self, attr_def):
        self.attr_def = attr_def
        self.config = { 'Lines':'1', 'Width':'Normal' }
        option_str = attr_def['Options']
        if option_str != '':
            options = option_str.split(':')
            for option in options:
                if option.find('=') != -1:
                    option_name, option_value = option.split('=')
                    self.config[option_name] = option_value

    def gen_xml_string(self, above_name):
        xml_str =  "    <!-- Begin NAME field text label and entry field -->\n"
        xml_str += "    <TextView\n"
        xml_str += "        android:id=\"@+id/NAMELabel\"\n"
        xml_str += "        android:layout_width=\"140dp\"\n"
        xml_str += "        android:layout_height=\"40dp\"\n"
        xml_str += "        android:layout_alignParentLeft=\"true\"\n"
        if above_name == 'NONE':
            xml_str += "        android:layout_alignParentTop=\"true\"\n"
        else:
            xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        xml_str += "        android:gravity=\"center_vertical|right\"\n"
        xml_str += "        android:textColor=\"@color/white\"\n"
        xml_str += "        android:text=\"NAME:\" />\n"
        xml_str += "\n"
        xml_str += "    <EditText\n"
        xml_str += "        android:id=\"@+id/NAMEEntry\"\n"

        if self.config['Width'] == 'Narrow':
            xml_str += "        android:layout_width=\"80dp\"\n"
        elif self.config['Width'] == 'Wide':
            xml_str += "        android:layout_width=\"460dp\"\n"
        else:
            xml_str += "        android:layout_width=\"200dp\"\n"
        
        lines = int(self.config['Lines'])
        height = 40*lines
        xml_str += "        android:layout_height=\"%ddp\"\n" % height
                
        if self.attr_def['Type'] == 'Integer':
            xml_str += "        android:numeric=\"integer\"\n"
        xml_str += "        android:textColor=\"@color/black\"\n"
        if above_name == 'NONE':
            xml_str += "        android:layout_alignParentTop=\"true\"\n"
        else:
            xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        xml_str += "        android:layout_toRightOf=\"@+id/NAMELabel\"\n"
        xml_str += "        android:background=\"@android:drawable/editbox_background\" />\n"
        xml_str += "    <!-- End NAME field text label and entry field -->\n\n"
        return xml_str

    def gen_java_declarations_string(self):
        java_str = "    private EditText NAMEEntry;\n"
        return java_str

    def gen_java_init_string(self):
        java_str = "        NAMEEntry = (EditText) findViewById(R.id.NAMEEntry);\n"
        return java_str

    def gen_java_button_handler(self):
        return ''

    def gen_java_discard_handler(self):
        java_str = "        NAMEEntry.setText(\"\");\n"
        return java_str
    
    def gen_java_save_handler(self):
        java_str = ''
        java_str += "\n        if ( !NAMEEntry.getText().toString().isEmpty() )\n"
        java_str += "            buffer.append(\"NAME:\" + NAMEEntry.getText().toString() + eol);\n"

        return java_str

    def gen_java_reload_handler(self):
        java_str = ''
        java_str += "                } else if ( token.equalsIgnoreCase(\"NAME\")) {\n"
        java_str += "                    NAMEEntry.setText(tokenizer.nextToken());\n"
        return java_str

