'''
Created on Feb 4, 2012

@author: Ken
'''

from UiGeneratorControl import UiGenControl

class CheckboxUiGenControl( UiGenControl ):
    attr_def = None

    def __init__(self, attr_def):
        self.attr_def = attr_def

    def gen_xml_string(self, above_name):
    
        xml_str =  "    <!-- Begin NAME field text label and checkbox group -->\n"
        xml_str += "    <TextView\n"
        xml_str += "        android:id=\"@+id/NAMELabel\"\n"
        xml_str += "        android:layout_width=\"120dp\"\n"
        xml_str += "        android:layout_height=\"40dp\"\n"
        xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        xml_str += "        android:gravity=\"center_vertical|right\"\n"
        xml_str += "        android:text=\"NAME:\" />\n"
        xml_str += "\n"
        map_values = self.attr_def['Map_Values']
        tokens = map_values.split(':')
        field_to_left = 'NAMELabel'
        for token in tokens:        
            xml_str += "        <CheckBox\n"
            xml_str += "            android:id=\"@+id/NAMEBUTTONCheckBox\"\n"
            xml_str += "            android:layout_width=\"wrap_content\"\n"
            xml_str += "            android:layout_height=\"wrap_content\"\n"
            xml_str += "            android:layout_toRightOf=\"@+id/" + field_to_left + "\"\n"
            xml_str += "            android:layout_alignTop=\"@+id/"  + field_to_left + "\"\n"
            xml_str += "            android:text=\"BUTTON\" />\n"
            xml_str += "\n"
            name, token_val = token.split('=')
            xml_str = xml_str.replace('BUTTON',name)
            field_to_left = 'NAME' + name + 'CheckBox' 
    
        xml_str += "    <!-- End NAME field text label and checkbox group -->\n\n"
        return xml_str

    def gen_java_declarations_string(self):
        java_str  = ''
        map_values = self.attr_def['Map_Values']
        tokens = map_values.split(':')
        for token in tokens:        
            java_str += "    private CheckBox NAMEBUTTONCheckBox;\n"
            name, token_val = token.split('=')
            java_str = java_str.replace('BUTTON',name) 
        return java_str

    def gen_java_init_string(self):
        java_str  = ''
        map_values = self.attr_def['Map_Values']
        tokens = map_values.split(':')
        for token in tokens:
            java_str += "        NAMEBUTTONCheckBox = (CheckBox) findViewById(R.id.NAMEBUTTONCheckBox);\n"
            name, token_val = token.split('=')
            java_str = java_str.replace('BUTTON',name) 
        return java_str

    def gen_java_button_handler(self):
        # there are no button handlers for the checkbox control
        return ''

    def gen_java_discard_handler(self):
        java_str  = ''
        map_values = self.attr_def['Map_Values']
        tokens = map_values.split(':')
        for token in tokens:
            java_str += "        NAMEBUTTONCheckBox.setChecked(false);\n"
            name, token_val = token.split('=')
            java_str = java_str.replace('BUTTON',name) 
         
        return java_str

    def gen_java_save_handler(self):
        java_str = "\n        String NAMESelection = \"NAME:\";\n"
        java_str += "        boolean NAMEIsChecked = false;\n"
        map_values = self.attr_def['Map_Values']
        tokens = map_values.split(':')
        first = True
        for token in tokens:
            if (first == True):
                first = False
                java_str += "        if (NAMEBUTTONCheckBox.isChecked()) {\n"
                java_str += "            NAMEIsChecked = true;\n"
                java_str += "            buffer.append(NAMESelection + NAMEBUTTONCheckBox.getText().toString());\n"
                java_str += "        }\n"
            else:
                java_str += "        if (NAMEBUTTONCheckBox.isChecked()) {\n"
                java_str += "            if (!NAMEIsChecked) {\n"
                java_str += "                NAMEIsChecked = true;\n"
                java_str += "                buffer.append(NAMESelection + NAMEBUTTONCheckBox.getText().toString());\n"
                java_str += "            } else {\n"
                java_str += "                buffer.append(\",\" + NAMEBUTTONCheckBox.getText().toString());\n"
                java_str += "            }\n"
                java_str += "        }\n"
    
            name, token_val = token.split('=')
            java_str = java_str.replace('BUTTON',name)
        java_str += "        if ( NAMEIsChecked )\n"        
        java_str += "            buffer.append(eol);\n"        
    
        return java_str

    def gen_java_reload_handler(self):
        java_str = "                } else if ( token.equalsIgnoreCase(\"NAME\")) {\n"
        java_str += "                    String valueStr = tokenizer.nextToken();\n"
        map_values = self.attr_def['Map_Values']
        tokens = map_values.split(':')
        for token in tokens:
            java_str += "                    if ( parseFieldForValue( valueStr, \"BUTTON\") )\n"
            java_str += "                        NAMEBUTTONCheckBox.setChecked(true);\n"
            java_str += "                    else\n"
            java_str += "                        NAMEBUTTONCheckBox.setChecked(false);\n"
            name, token_val = token.split('=')
            java_str = java_str.replace('BUTTON',name) 
        return java_str
    
