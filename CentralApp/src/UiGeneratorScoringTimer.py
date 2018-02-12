'''
Created on February 10, 2018

@author: Ken
'''

from optparse import OptionParser
import AttributeDefinitions
from UiGeneratorControl import UiGenControl

class ScoringTimerUiGenControl( UiGenControl ):
    attr_def = None
    num_levels = None
    values = None
    config = {}

    def __init__(self, attr_def):
        self.attr_def = attr_def
        self.values = []
        self.config = { 'Type':'Seconds', 'Timer':'135' }
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
            raise Exception( 'Scoring Timer Is NOT Fully Specified!')

    def get_last_label(self):
        if self.num_levels > 0:
            index = self.num_levels - 1
            last_label = self.attr_def['Name'] + '_' + self.values[index][0] + '_Start'
        return last_label
            
    def gen_xml_string(self, above_name):
        xml_str = "    <!-- Begin NAME field text label and entry field -->\n"
        xml_str += "    <TextView\n"
        xml_str += "        android:id=\"@+id/NAMELabel\"\n"
        xml_str += "        android:layout_width=\"140dp\"\n"
        xml_str += "        android:layout_height=\"40dp\"\n"
        xml_str += "        android:layout_alignParentLeft=\"true\"\n"
        xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        xml_str += "        android:gravity=\"center_vertical|right\"\n"
        xml_str += "        android:textColor=\"@color/white\"\n"
        xml_str += "        android:text=\"NAME:\" />\n\n"
    
        xml_str += "    <!--  Scoring Timer -->\n"
    
        above_start_label = 'ABOVELabel'
        above_stop_label  = 'ABOVELabel'
        above_clear_label  = 'ABOVELabel'
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
            xml_str += "        android:layout_below=\"@+id/" + above_start_label + "\"\n"
            if first_level == True:
                left_level_label = level_label
                xml_str += "        android:layout_marginLeft=\"120dp\"\n"
                xml_str += "        android:layout_marginTop=\"20dp\"\n"
            else:
                xml_str += "        android:layout_alignLeft=\"@+id/" + left_level_label + "\"\n"
            xml_str += "        android:text=\"" + level[0] + ":\" />\n\n"
            
            # The Start button
            start_label = 'NAME_' + level[0] + '_Start'
            xml_str += "    <Button\n"
            xml_str += "        android:id=\"@+id/" + start_label + "\"\n"
            xml_str += "        android:layout_width=\"wrap_content\"\n"

            if self.custom_buttons:
                xml_str += "        android:layout_height=\"47dp\"\n"
                xml_str += "        android:background=\"@layout/custom_button\"\n"
            else:
                xml_str += "        android:layout_height=\"wrap_content\"\n"

            if first_level == True:
                left_label = start_label
                xml_str += "        android:layout_marginLeft=\"200dp\"\n"
                xml_str += "        android:layout_marginTop=\"20dp\"\n"
            else:
                xml_str += "        android:layout_alignLeft=\"@+id/" + left_label + "\"\n"
            xml_str += "        android:layout_below=\"@+id/" + above_start_label + "\"\n"
            xml_str += "        android:text=\"Start\" />\n\n"

            # The Stop button
            stop_label = 'NAME_' + level[0] + '_Stop'
            xml_str += "    <Button\n"
            xml_str += "        android:id=\"@+id/" + stop_label + "\"\n"
            xml_str += "        android:layout_width=\"wrap_content\"\n"

            if self.custom_buttons:
                xml_str += "        android:layout_height=\"47dp\"\n"
                xml_str += "        android:background=\"@layout/custom_button\"\n"
            else:
                xml_str += "        android:layout_height=\"wrap_content\"\n"

            if first_level == True:
                xml_str += "        android:layout_marginTop=\"20dp\"\n"
            xml_str += "        android:layout_toRightOf=\"@+id/" + start_label + "\"\n"
            xml_str += "        android:layout_below=\"@+id/" + above_stop_label + "\"\n"
            xml_str += "        android:text=\"Stop\" />\n\n"

            # The Clear button
            clear_label = 'NAME_' + level[0] + '_Clear'
            xml_str += "    <Button\n"
            xml_str += "        android:id=\"@+id/" + clear_label + "\"\n"
            xml_str += "        android:layout_width=\"wrap_content\"\n"

            if self.custom_buttons:
                xml_str += "        android:layout_height=\"47dp\"\n"
                xml_str += "        android:background=\"@layout/custom_button\"\n"
            else:
                xml_str += "        android:layout_height=\"wrap_content\"\n"

            if first_level == True:
                xml_str += "        android:layout_marginTop=\"20dp\"\n"
            xml_str += "        android:layout_toRightOf=\"@+id/" + stop_label + "\"\n"
            xml_str += "        android:layout_below=\"@+id/" + above_clear_label + "\"\n"
            xml_str += "        android:text=\"Clear\" />\n\n"

            xml_str += "    <TextView\n"
            xml_str += "        android:id=\"@+id/NAME_" + level[0] + "_Tag\"\n"
            xml_str += "        android:layout_width=\"wrap_content\"\n"
            xml_str += "        android:layout_height=\"wrap_content\"\n"
            xml_str += "        android:gravity=\"center_vertical|right\"\n"
            xml_str += "        android:layout_toRightOf=\"@+id/" + clear_label + "\"\n"
            if first_level == True:
                #xml_str += "        android:layout_alignRight=\"@+id/" + clear_label + "\"\n"
                xml_str += "        android:layout_below=\"@+id/NAMELabel\"\n"
            else:
                xml_str += "        android:layout_below=\"@+id/" + above_clear_label + "\"\n"
                xml_str += "        android:layout_marginTop=\"15dp\"\n"
            xml_str += "        android:layout_marginLeft=\"20dp\"\n"
            xml_str += "        android:textColor=\"@color/white\"\n"
            xml_str += "        android:text=\"Seconds\" />\n\n"

            # The Score field
            score_label = 'NAME_' + level[0]
            xml_str += "    <EditText\n"
            xml_str += "        android:id=\"@+id/" + score_label + "\"\n"
            xml_str += "        android:layout_width=\"wrap_content\"\n"
            xml_str += "        android:layout_height=\"wrap_content\"\n"
            #if first_level == True:
            #    xml_str += "        android:layout_marginTop=\"20dp\"\n"
            xml_str += "        android:layout_toRightOf=\"@+id/NAME_" + level[0] + "_Tag\"\n"
            #xml_str += "        android:layout_below=\"@+id/" + above_score_label + "\"\n"
            xml_str += "        android:layout_alignBottom=\"@+id/" + clear_label + "\"\n"
            xml_str += "        android:layout_marginLeft=\"20dp\"\n"
            xml_str += "        android:inputType=\"number\" />\n\n"

            above_start_label = start_label
            above_stop_label  = stop_label
            above_clear_label  = clear_label
            above_score_label = score_label
            first_level = False
    
        # determine where the totals field should go based on the number of levels there
        # are in the scoring matrix
        if self.num_levels > 2:
            offset = self.num_levels - 2
        elif self.num_levels > 0:
            offset = self.num_levels - 1
        else:
            offset = 0
        label = self.values[offset][0]

        ''' Remove totals

        xml_str += "    <TextView\n"
        xml_str += "        android:id=\"@+id/NAME_TotalLabel\"\n"
        xml_str += "        android:layout_width=\"wrap_content\"\n"
        xml_str += "        android:layout_height=\"wrap_content\"\n"
        xml_str += "        android:layout_alignBaseline=\"@+id/NAME_" + label + "\"\n"
        xml_str += "        android:layout_alignBottom=\"@+id/NAME_" + label + "\"\n"
        xml_str += "        android:layout_toRightOf=\"@+id/NAME_" + self.config['Type'] + "Tag\"\n"
        xml_str += "        android:layout_marginLeft=\"20dp\"\n"
        xml_str += "        android:textColor=\"@color/white\"\n"
        xml_str += "        android:text=\"Score\" />\n\n"
         
        xml_str += "    <EditText\n"
        xml_str += "        android:id=\"@+id/NAME\"\n"
        xml_str += "        android:layout_width=\"wrap_content\"\n"
        xml_str += "        android:layout_height=\"wrap_content\"\n"
        xml_str += "        android:layout_alignBaseline=\"@+id/NAME_TotalLabel\"\n"
        xml_str += "        android:layout_alignBottom=\"@+id/NAME_TotalLabel\"\n"
        xml_str += "        android:layout_toRightOf=\"@+id/NAME_TotalLabel\"\n"
        xml_str += "        android:inputType=\"number\" />\n\n"
        '''
        xml_str += "    <!-- Last label on control: " + self.get_last_label() + " -->\n"
        xml_str += "    <!-- End NAME field text label and entry field -->\n\n"
        return xml_str

    def gen_java_declarations_string(self):
        java_str = ''
        for level in self.values:
            java_str += "    private EditText NAME_" + level[0] + ";\n"
            java_str += "    private Button NAME_" + level[0] + "_Stop;\n"
            java_str += "    private Button NAME_" + level[0] + "_Start;\n"
            java_str += "    private Button NAME_" + level[0] + "_Clear;\n"
            java_str += "    private CountDownTimer NAME_" + level[0] + "_Timer;\n"
            java_str += "    private long NAME_" + level[0] + "_Seconds_Left;\n"
        ''' Remove totals
        java_str += "    private EditText NAME;\n"    
        '''
        return java_str
    
    def gen_java_init_string(self):
        java_str = ''
        for level in self.values:
            ''' Remove totals'
            java_str += "        NAME = (EditText) findViewById(R.id.NAME);\n"
            '''
            java_str += "        NAME_" + level[0] + " = (EditText) findViewById(R.id.NAME_" + level[0] + ");\n"
            java_str += "        NAME_" + level[0] + ".setClickable(false);\n"
            java_str += "        NAME_" + level[0] + ".setText(\"\");\n"
            java_str += "        NAME_" + level[0] + "_Stop = (Button) findViewById(R.id.NAME_" + level[0] + "_Stop);\n"
            java_str += "        NAME_" + level[0] + "_Start = (Button) findViewById(R.id.NAME_" + level[0] + "_Start);\n"
            java_str += "        NAME_" + level[0] + "_Clear = (Button) findViewById(R.id.NAME_" + level[0] + "_Clear);\n"
        return java_str

    def gen_java_button_handler(self):
        java_str = ''
        second_pass_values = self.values
        timer_value = str((int(self.config['Timer']))*1000)
        for level in self.values:
            java_str += "        NAME_" + level[0] + "_Stop.setOnClickListener(new OnClickListener(){\n"
            java_str += "            public void onClick(View v){\n"
            java_str += "                if ( NAME_" + level[0] + "_Timer != null )\n"
            java_str += "                    NAME_" + level[0] + "_Timer.cancel();\n"
            java_str += "            }\n"
            java_str += "        });\n\n"

            java_str += "        NAME_" + level[0] + "_Start.setOnClickListener(new OnClickListener(){\n"
            java_str += "            String value = \"\";\n"
            java_str += "            int value2 = 0;\n\n"
            java_str += "            public void onClick(View v){\n"
            java_str += "                unsavedChanges = true;\n"
            java_str += "\n"
            java_str += "                NAME_" + level[0] + ".requestFocus();\n"
            java_str += "                NAME_" + level[0] + ".clearFocus();\n"
            java_str += "\n"
            java_str += "                if ( NAME_" + level[0] + "_Timer != null ) {\n"
            java_str += "                    NAME_" + level[0] + "_Timer.resume();\n"
            java_str += "                } else {\n"
            java_str += "                    NAME_" + level[0] + ".setText(\"\");\n"
            java_str += "                    NAME_" + level[0] + "_Seconds_Left = 0;\n"
            java_str += "\n"
            java_str += "                    NAME_" + level[0] + "_Timer = new CountDownTimer(" + timer_value + ", 50) {\n"
            java_str += "\n"
            java_str += "                        public void onTick(long millisUntilFinished) {\n"
            java_str += "\n"
            java_str += "                            long secondsLeft = millisUntilFinished/1000;\n"
            java_str += "\n"
            java_str += "                            NAME_" + level[0] + ".requestFocus();\n"
            java_str += "                            NAME_" + level[0] + ".clearFocus();\n"
            java_str += "\n"
            java_str += "                            if ( NAME_" + level[0] + "_Seconds_Left != secondsLeft ) {\n"
            java_str += "                                NAME_" + level[0] + "_Seconds_Left = secondsLeft;\n"
            java_str += "\n"
            java_str += "                                value2 = 1;\n"
            java_str += "                                if (!NAME_" + level[0] + ".getText().toString().isEmpty()) {\n"
            java_str += "                                    value = NAME_" + level[0] + ".getText().toString();\n"
            java_str += "                                    value2 = Integer.parseInt(value)+1;\n"
            java_str += "                                }\n"            
            java_str += "                                NAME_" + level[0] + ".setText(Integer.toString(value2));\n"
            ''' Remove totals
            java_str += "\n"
            java_str += "                        if (!NAME.getText().toString().isEmpty()) {\n"
            java_str += "                            value = NAME.getText().toString();\n"
            java_str += "                            value2 = Integer.parseInt(value)+1;\n"
            java_str += "                        } else {\n"
            java_str += "                            value2 = 1;\n"
            java_str += "                        }\n"
            java_str += "                        NAME.setText(Integer.toString(value2));\n"
            '''
            java_str += "                            }\n"            
            java_str += "                        }\n"
            java_str += "\n"
            java_str += "                        public void onFinish() {\n"
            java_str += "                        }\n"
            java_str += "                    }.start();\n"
            java_str += "                }\n"
            java_str += "            }\n"
            java_str += "        });\n\n"
            
            java_str += "        NAME_" + level[0] + "_Clear.setOnClickListener(new OnClickListener(){\n"
            java_str += "            public void onClick(View v){\n"
            java_str += "                if ( NAME_" + level[0] + "_Timer != null ){\n"
            java_str += "                    NAME_" + level[0] + "_Timer.cancel();\n"
            java_str += "                    NAME_" + level[0] + "_Timer = null;\n"
            java_str += "                }\n"
            java_str += "                NAME_" + level[0] + ".setText(\"\");\n"
            ''' Remove totals
            java_str += "                NAME.setText(\"\");\n"
            '''
            java_str += "            }\n"
            java_str += "        });\n\n"


        return java_str    
    
    def gen_java_discard_handler(self):
        java_str = ''
        for level in self.values:
            java_str += "        NAME_" + level[0] + ".setText(\"0\");\n"
        ''' Remove totals
        java_str += "        NAME.setText(\"\");\n"
        '''          
        return java_str
    
    def gen_java_save_handler(self):
        java_str = ''
        ''' Remove totals
        java_str += "        if ( !NAME.getText().toString().isEmpty() )\n"
        java_str += "            buffer.append(\"NAME:\" + NAME.getText().toString() + eol);\n"
        '''
        for level in self.values:
            java_str += "        if ( !NAME_" + level[0] + ".getText().toString().isEmpty() )\n"
            java_str += "            buffer.append(\"NAME_" + level[0] + ":\" + NAME_" + level[0] + ".getText().toString() + eol);\n"
        return java_str
    
    def gen_java_reload_handler(self):
        java_str = ''
        ''' Remove totals
        java_str += "                } else if ( token.equalsIgnoreCase(\"NAME\")) {\n"
        java_str += "                    NAME.setText(tokenizer.nextToken());\n"
        '''
        for level in self.values:
            java_str += "                } else if ( token.equalsIgnoreCase(\"NAME_" + level[0] + "\")) {\n"
            java_str += "                    NAME_" + level[0] + ".setText(tokenizer.nextToken());\n"
        return java_str

