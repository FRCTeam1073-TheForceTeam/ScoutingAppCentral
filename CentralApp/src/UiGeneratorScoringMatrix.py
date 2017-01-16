'''
Created on January 19, 2013

@author: Ken
'''

from optparse import OptionParser
import AttributeDefinitions
from UiGeneratorControl import UiGenControl

class ScoringMatrixUiGenControl( UiGenControl ):
    attr_def = None
    num_levels = None
    values = None
    config = {}

    def __init__(self, attr_def):
        self.attr_def = attr_def
        self.values = []
        self.config = { 'Type':'Score', 'Misses':'No' }
        option_str = attr_def['Options']
        options = option_str.split(':')
        for option in options:
            option_name, option_value = option.split('=')
            self.config[option_name] = option_value

        map_values_str = attr_def['Map_Values']
        map_values = map_values_str.split(':')
        for map_value in map_values:
            name, value = map_value.split('=')
            self.values.append( (name,value) )

        self.num_levels = len(self.values)
        if self.num_levels == 0:
            raise Exception( 'Scoring Matrix Is NOT Fully Specified!')

    def get_last_label(self):
        if self.num_levels > 0:
            index = self.num_levels - 1
            last_label = self.attr_def['Name'] + '_' + self.values[index][0] + '_Minus'
        return last_label
            
    def gen_xml_string(self, above_name):
        xml_str = "    <!-- Begin NAME field text label and entry field -->\n"
        xml_str += "    <TextView\n"
        xml_str += "        android:id=\"@+id/NAMELabel\"\n"
        xml_str += "        android:layout_width=\"120dp\"\n"
        xml_str += "        android:layout_height=\"40dp\"\n"
        xml_str += "        android:layout_alignParentLeft=\"true\"\n"
        xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        xml_str += "        android:gravity=\"center_vertical|right\"\n"
        xml_str += "        android:textColor=\"@color/white\"\n"
        xml_str += "        android:text=\"NAME:\" />\n\n"
    
        xml_str += "    <!--  Scoring Matrix -->\n"
    
        above_minus_label = 'ABOVELabel'
        above_plus_label  = 'ABOVELabel'
        above_score_label = 'ABOVELabel'
        above_miss_label  = 'ABOVELabel'
        first_level = True
        left_label = ''
        left_level_label = ''
        for level in self.values:
            # The label for this level
            level_label = 'NAME_' + level[0] + '_Label'
            xml_str += "    <TextView\n"
            xml_str += "        android:id=\"@+id/" + level_label + "\"\n"
            xml_str += "        android:layout_width=\"80dp\"\n"
            xml_str += "        android:layout_height=\"50dp\"\n"
            xml_str += "        android:gravity=\"center_vertical|right\"\n"
            xml_str += "        android:textColor=\"@color/white\"\n"
            xml_str += "        android:layout_below=\"@+id/" + above_minus_label + "\"\n"
            if first_level == True:
                left_level_label = level_label
                xml_str += "        android:layout_marginLeft=\"120dp\"\n"
                xml_str += "        android:layout_marginTop=\"20dp\"\n"
            else:
                xml_str += "        android:layout_alignLeft=\"@+id/" + left_level_label + "\"\n"
            xml_str += "        android:text=\"" + level[0] + ":\" />\n\n"
            
            # The Minus button
            minus_label = 'NAME_' + level[0] + '_Minus'
            xml_str += "    <Button\n"
            xml_str += "        android:id=\"@+id/" + minus_label + "\"\n"
            xml_str += "        android:layout_width=\"wrap_content\"\n"

            if self.custom_buttons:
                xml_str += "        android:layout_height=\"47dp\"\n"
                xml_str += "        android:background=\"@layout/custom_button\"\n"
            else:
                xml_str += "        android:layout_height=\"wrap_content\"\n"

            if first_level == True:
                left_label = minus_label
                #xml_str += "        android:layout_marginLeft=\"130dp\"\n"
                xml_str += "        android:layout_marginLeft=\"200dp\"\n"
                xml_str += "        android:layout_marginTop=\"20dp\"\n"
            else:
                xml_str += "        android:layout_alignLeft=\"@+id/" + left_label + "\"\n"
            xml_str += "        android:layout_below=\"@+id/" + above_minus_label + "\"\n"
            xml_str += "        android:text=\"-\" />\n\n"

            # The Plus button
            plus_label = 'NAME_' + level[0] + '_Plus'
            xml_str += "    <Button\n"
            xml_str += "        android:id=\"@+id/" + plus_label + "\"\n"
            xml_str += "        android:layout_width=\"wrap_content\"\n"

            if self.custom_buttons:
                xml_str += "        android:layout_height=\"47dp\"\n"
                xml_str += "        android:background=\"@layout/custom_button\"\n"
            else:
                xml_str += "        android:layout_height=\"wrap_content\"\n"

            if first_level == True:
                xml_str += "        android:layout_marginTop=\"20dp\"\n"
            xml_str += "        android:layout_toRightOf=\"@+id/" + minus_label + "\"\n"
            xml_str += "        android:layout_below=\"@+id/" + above_plus_label + "\"\n"
            xml_str += "        android:text=\"+\" />\n\n"

            # The Score field
            score_label = 'NAME_' + level[0]
            xml_str += "    <EditText\n"
            xml_str += "        android:id=\"@+id/" + score_label + "\"\n"
            xml_str += "        android:layout_width=\"wrap_content\"\n"
            xml_str += "        android:layout_height=\"wrap_content\"\n"
            #if first_level == True:
            #    xml_str += "        android:layout_marginTop=\"20dp\"\n"
            xml_str += "        android:layout_toRightOf=\"@+id/" + plus_label + "\"\n"
            #xml_str += "        android:layout_below=\"@+id/" + above_score_label + "\"\n"
            xml_str += "        android:layout_alignBottom=\"@+id/" + plus_label + "\"\n"
            xml_str += "        android:layout_marginLeft=\"20dp\"\n"
            xml_str += "        android:inputType=\"number\" />\n\n"

            # The Misses field
            if self.config['Misses'] == 'Yes':
                miss_label = 'NAME_' + level[0] + '_Miss'
                xml_str += "    <Button\n"
                xml_str += "        android:id=\"@+id/" + miss_label + "\"\n"
                xml_str += "        android:layout_width=\"wrap_content\"\n"
                xml_str += "        android:layout_height=\"wrap_content\"\n"
                xml_str += "        android:layout_below=\"@+id/" + above_miss_label + "\"\n"
                xml_str += "        android:layout_toRightOf=\"@+id/" + score_label + "\"\n"
                if first_level == True:
                    xml_str += "        android:layout_marginTop=\"20dp\"\n"
                xml_str += "        android:layout_marginLeft=\"20dp\"\n"
                xml_str += "        android:text=\"X\" />\n\n"
         
                misses_label = 'NAME_' + level[0] + '_Misses'
                xml_str += "    <EditText\n"
                xml_str += "        android:id=\"@+id/" + misses_label + "\"\n"
                xml_str += "        android:layout_width=\"wrap_content\"\n"
                xml_str += "        android:layout_height=\"wrap_content\"\n"
                xml_str += "        android:layout_alignBottom=\"@+id/" + score_label + "\"\n"
                xml_str += "        android:layout_toRightOf=\"@+id/" + miss_label + "\"\n"
                xml_str += "        android:layout_marginLeft=\"20dp\"\n"
                xml_str += "        android:inputType=\"number\" />\n\n"

                above_miss_label = miss_label
         
            above_minus_label = minus_label
            above_plus_label  = plus_label
            above_score_label = score_label
            first_level = False
    
        if self.config['Misses'] == 'Yes':
            xml_str += "    <TextView\n"
            xml_str += "        android:id=\"@+id/NAME_Misses\"\n"
            xml_str += "        android:layout_width=\"wrap_content\"\n"
            xml_str += "        android:layout_height=\"wrap_content\"\n"
            xml_str += "        android:layout_alignRight=\"@+id/" + misses_label + "\"\n"
            xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
            xml_str += "        android:textColor=\"@color/white\"\n"
            xml_str += "        android:text=\"Misses\" />\n\n"
         
        xml_str += "    <TextView\n"
        xml_str += "        android:id=\"@+id/NAME_" + self.config['Type'] + "Tag\"\n"
        xml_str += "        android:layout_width=\"wrap_content\"\n"
        xml_str += "        android:layout_height=\"wrap_content\"\n"
        xml_str += "        android:layout_alignRight=\"@+id/" + score_label + "\"\n"
        xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        xml_str += "        android:textColor=\"@color/white\"\n"
        xml_str += "        android:text=\"" + self.config['Type'] + "\" />\n\n"

        # determine where the totals field should go based on the number of levels there
        # are in the scoring matrix
        if self.num_levels > 2:
            offset = self.num_levels - 2
        elif self.num_levels > 0:
            offset = self.num_levels - 1
        else:
            offset = 0
        label = self.values[offset][0]

        if self.config['Misses'] == 'Yes':
            xml_str += "    <TextView\n"
            xml_str += "        android:id=\"@+id/NAME_TotalLabel\"\n"
            xml_str += "        android:layout_width=\"wrap_content\"\n"
            xml_str += "        android:layout_height=\"wrap_content\"\n"
            xml_str += "        android:layout_alignBaseline=\"@+id/NAME_" + label + "_Misses\"\n"
            xml_str += "        android:layout_alignBottom=\"@+id/NAME_" + label + "_Misses\"\n"
            xml_str += "        android:layout_toRightOf=\"@+id/NAME_Misses\"\n"
            xml_str += "        android:layout_marginLeft=\"20dp\"\n"
            xml_str += "        android:textColor=\"@color/white\"\n"
            xml_str += "        android:text=\"Total\" />\n\n"
        else:
            xml_str += "    <TextView\n"
            xml_str += "        android:id=\"@+id/NAME_TotalLabel\"\n"
            xml_str += "        android:layout_width=\"wrap_content\"\n"
            xml_str += "        android:layout_height=\"wrap_content\"\n"
            xml_str += "        android:layout_alignBaseline=\"@+id/NAME_" + label + "\"\n"
            xml_str += "        android:layout_alignBottom=\"@+id/NAME_" + label + "\"\n"
            xml_str += "        android:layout_toRightOf=\"@+id/NAME_" + self.config['Type'] + "Tag\"\n"
            xml_str += "        android:layout_marginLeft=\"20dp\"\n"
            xml_str += "        android:textColor=\"@color/white\"\n"
            xml_str += "        android:text=\"Total\" />\n\n"
         
        xml_str += "    <EditText\n"
        xml_str += "        android:id=\"@+id/NAME\"\n"
        xml_str += "        android:layout_width=\"wrap_content\"\n"
        xml_str += "        android:layout_height=\"wrap_content\"\n"
        xml_str += "        android:layout_alignBaseline=\"@+id/NAME_TotalLabel\"\n"
        xml_str += "        android:layout_alignBottom=\"@+id/NAME_TotalLabel\"\n"
        xml_str += "        android:layout_toRightOf=\"@+id/NAME_TotalLabel\"\n"
        xml_str += "        android:inputType=\"number\" />\n\n"
        xml_str += "    <!-- Last label on control: " + self.get_last_label() + " -->\n"
        xml_str += "    <!-- End NAME field text label and entry field -->\n\n"
        return xml_str

    def gen_java_declarations_string(self):
        java_str = ''
        for level in self.values:
            java_str += "    private EditText NAME_" + level[0] + ";\n"
            java_str += "    private Button NAME_" + level[0] + "_Plus;\n"
            java_str += "    private Button NAME_" + level[0] + "_Minus;\n"
            if self.config['Misses'] == 'Yes':
                java_str += "    private EditText NAME_" + level[0] + "_Misses;\n"
                java_str += "    private Button NAME_" + level[0] + "_Miss;\n"
        java_str += "    private EditText NAME;\n"    
        return java_str
    
    def gen_java_init_string(self):
        java_str = ''
        for level in self.values:
            java_str += "        NAME = (EditText) findViewById(R.id.NAME);\n"
            java_str += "        NAME_" + level[0] + " = (EditText) findViewById(R.id.NAME_" + level[0] + ");\n"
            java_str += "        NAME_" + level[0] + ".setClickable(false);\n"
            java_str += "        NAME_" + level[0] + ".setText(\"0\");\n"
            java_str += "        NAME_" + level[0] + "_Plus = (Button) findViewById(R.id.NAME_" + level[0] + "_Plus);\n"
            java_str += "        NAME_" + level[0] + "_Minus = (Button) findViewById(R.id.NAME_" + level[0] + "_Minus);\n"
            if self.config['Misses'] == 'Yes':
                java_str += "        NAME_" + level[0] + "_Misses = (EditText) findViewById(R.id.NAME_" + level[0] + "_Misses);\n"
                java_str += "        NAME_" + level[0] + "_Misses.setClickable(false);\n"
                java_str += "        NAME_" + level[0] + "_Misses.setText(\"0\");\n"
                java_str += "        NAME_" + level[0] + "_Miss = (Button) findViewById(R.id.NAME_" + level[0] + "_Miss);\n"
        return java_str

    def gen_java_button_handler(self):
        java_str = ''
        second_pass_values = self.values
        for level in self.values:
            java_str += "        NAME_" + level[0] + "_Plus.setOnClickListener(new OnClickListener(){\n"
            java_str += "            String value = \"\";\n"
            java_str += "            int value2 = 0;\n\n"
            java_str += "            public void onClick(View v){\n"
            java_str += "                unsavedChanges = true;\n"
            java_str += "                if (!NAME_" + level[0] + ".getText().toString().isEmpty())\n"
            java_str += "                    value = NAME_" + level[0] + ".getText().toString();\n"
            java_str += "                value2 = Integer.parseInt(value);\n"
            if self.config.has_key('Max'):
                java_str += "                if ( value2 < " + self.config['Max'] + " ) {\n"
                java_str += "                    value2++;\n"
                java_str += "                }\n"
            else:    
                java_str += "                value2++;\n"
            java_str += "                NAME.requestFocus();\n"
            java_str += "                NAME.clearFocus();\n"
            java_str += "                NAME_" + level[0] + ".setText(Integer.toString(value2));\n"
            java_str += "                NAME.setText(Integer.toString(\n"
            for second_pass in second_pass_values:
                if second_pass[1].upper() == 'CUSTOM':
                    java_str += "                        (NAME_CustomScore(Integer.parseInt(NAME_" + second_pass[0] + ".getText().toString())))+\n"
                else:
                    java_str += "                        (Integer.parseInt(NAME_" + second_pass[0] + ".getText().toString())*" + second_pass[1] + ")+\n"
            java_str += "                        0));\n"
            java_str += "            }\n"
            java_str += "        });\n\n"

            java_str += "        NAME_" + level[0] + "_Minus.setOnClickListener(new OnClickListener(){\n"
            java_str += "            String value = \"\";\n"
            java_str += "            int value2 = 0;\n\n"
            java_str += "            public void onClick(View v){\n"
            java_str += "                unsavedChanges = true;\n"
            java_str += "                if (!NAME_" + level[0] + ".getText().toString().isEmpty())\n"
            java_str += "                    value = NAME_" + level[0] + ".getText().toString();\n"
            java_str += "                 value2 = Integer.parseInt(value);\n"
            java_str += "                value2--;\n"
            java_str += "                NAME.requestFocus();\n"
            java_str += "                NAME.clearFocus();\n"
            java_str += "                if(value2 >= 0){\n"
            java_str += "                    NAME_" + level[0] + ".setText(Integer.toString(value2));\n"
            java_str += "                    NAME.setText(Integer.toString(\n"
            for second_pass in second_pass_values:
                if second_pass[1].upper() == 'CUSTOM':
                    java_str += "                        (NAME_CustomScore(Integer.parseInt(NAME_" + second_pass[0] + ".getText().toString())))+\n"
                else:
                    java_str += "                        (Integer.parseInt(NAME_" + second_pass[0] + ".getText().toString())*" + second_pass[1] + ")+\n"
            java_str += "                        0));\n"
            java_str += "                }\n"
            java_str += "                else\n"
            java_str += "                    return;\n"
            java_str += "            }\n"
            java_str += "        });\n\n"

            if self.config['Misses'] == 'Yes':
                java_str += "        NAME_" + level[0] + "_Miss.setOnClickListener(new OnClickListener(){\n"
                java_str += "            String value = \"\";\n"
                java_str += "            int value2 = 0;\n\n"
                java_str += "            public void onClick(View v){\n"
                java_str += "                unsavedChanges = true;\n"
                java_str += "                if (!NAME_" + level[0] + "_Misses.getText().toString().isEmpty())\n"
                java_str += "                    value = NAME_" + level[0] + "_Misses.getText().toString();\n"
                java_str += "                value2 = Integer.parseInt(value);\n"
                java_str += "                value2++;\n"
                java_str += "                NAME.requestFocus();\n"
                java_str += "                NAME.clearFocus();\n"
                java_str += "                NAME_" + level[0] + "_Misses.setText(Integer.toString(value2));\n"
                java_str += "            }\n"
                java_str += "        });\n\n"
        return java_str    
    
    def gen_java_discard_handler(self):
        java_str = ''
        for level in self.values:
            java_str += "        NAME_" + level[0] + ".setText(\"0\");\n"
            if self.config['Misses'] == 'Yes':
                java_str += "        NAME_" + level[0] + "_Misses.setText(\"0\");\n"            
        java_str += "        NAME.setText(\"\");\n"            
        return java_str
    
    def gen_java_save_handler(self):
        java_str = ''
        java_str += "        if ( !NAME.getText().toString().isEmpty() )\n"
        java_str += "            buffer.append(\"NAME:\" + NAME.getText().toString() + eol);\n"
        for level in self.values:
            java_str += "        if ( !NAME_" + level[0] + ".getText().toString().isEmpty() )\n"
            java_str += "            buffer.append(\"NAME_" + level[0] + ":\" + NAME_" + level[0] + ".getText().toString() + eol);\n"
            if self.config['Misses'] == 'Yes':
                java_str += "        if ( !NAME_" + level[0] + "_Misses.getText().toString().isEmpty() )\n"
                java_str += "            buffer.append(\"NAME_" + level[0] + "_Misses:\" + NAME_" + level[0] + "_Misses.getText().toString() + eol);\n"
        return java_str
    
    def gen_java_reload_handler(self):
        java_str = ''
        java_str += "                } else if ( token.equalsIgnoreCase(\"NAME\")) {\n"
        java_str += "                    NAME.setText(tokenizer.nextToken());\n"
        for level in self.values:
            java_str += "                } else if ( token.equalsIgnoreCase(\"NAME_" + level[0] + "\")) {\n"
            java_str += "                    NAME_" + level[0] + ".setText(tokenizer.nextToken());\n"
            if self.config['Misses'] == 'Yes':
                java_str += "                } else if ( token.equalsIgnoreCase(\"NAME_" + level[0] + "_Misses\")) {\n"
                java_str += "                    NAME_" + level[0] + "_Misses.setText(tokenizer.nextToken());\n"
        return java_str

