'''
Created on Dec 26, 2016

@author: Ken
'''

from UiGeneratorControl import UiGenControl

def GetMatchGroupControlDefs(current_definition):
    attr_defs = {
        'Comp_Round': {
            'Control': 'Radio', 
            'Sheet': 'Match', 
            'Sub_Category': 'Admin', 
            'Weight': '0.0', 
            'Options': 'NoDiscard:NoReload', 
            'Map_Values': 'Qual=Qm:Quarters=Qf:Semis=Sf:Finals=F', 
            'Include_In_Report': '', 
            'Database_Store': 'No', 
            'Display_Numeric': 'No', 
            'Statistic_Type': 'None', 
            'Type': 'Map_Integer', 
            'Name': 'Comp_Round'
        },
        'Alliance': {
            'Control': 'Radio', 
            'Sheet': 'Match', 
            'Sub_Category': 'Admin', 
            'Weight': '0.0', 
            'Options': 'NoDiscard:NoReload', 
            'Map_Values': 'Blue=1:Red=1', 
            'Include_In_Report': '', 
            'Database_Store': 'No', 
            'Display_Numeric': 'No', 
            'Statistic_Type': 'None', 
            'Type': 'Map_Integer', 
            'Name': 'Alliance'
        },
        'Position': {
            'Control': 'Radio', 
            'Sheet': 'Match', 
            'Sub_Category': 'Admin', 
            'Weight': '0.0', 
            'Options': 'NoDiscard:NoReload', 
            'Map_Values': '1=1:2=2:3=3', 
            'Include_In_Report': '', 
            'Database_Store': 'No', 
            'Display_Numeric': 'No', 
            'Statistic_Type': 'None', 
            'Type': 'Map_Integer', 
            'Name': 'Position'
        }
    }

    # get the current position of the passed in definition. We will
    # insert the new definitions above the passed in definition
    current_order = current_definition['Order']    
    attr_defs['Comp_Round']['Order'] = current_order
    attr_defs['Comp_Round']['Column_Order'] = current_order
    current_order += 1
    attr_defs['Alliance']['Order'] = current_order
    attr_defs['Alliance']['Column_Order'] = current_order
    current_order += 1
    attr_defs['Position']['Order'] = current_order
    attr_defs['Position']['Column_Order'] = current_order
    current_order += 1
        
    # reset the order of the current definition just beyond the
    # new definitions
    current_definition['Order'] = current_order
    current_definition['Column_Order'] = current_order
    return attr_defs
    
class MatchGroupUiGenControl( UiGenControl ):
    attr_def = None

    def __init__(self, attr_def):
        self.attr_def = attr_def
        self.config = {}
        option_str = attr_def['Options']
        if option_str != '':
            options = option_str.split(':')
            for option in options:
                if option.find('=') != -1:
                    option_name, option_value = option.split('=')
                    self.config[option_name] = option_value
                else:
                    # option with no value is treated as a boolean, set to True
                    self.config[option] = True

    def gen_xml_string(self, above_name):
        xml_str = ''
    
        xml_str =  "    <!-- Begin NAME field match group -->\n"        
        xml_str += "    <TextView\n"
        xml_str += "        android:id=\"@+id/NAMELabel\"\n"
        xml_str += "        android:layout_width=\"120dp\"\n"
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
        xml_str += "        android:layout_width=\"80dp\"\n"
        xml_str += "        android:layout_height=\"40dp\"\n"
                
        if self.attr_def['Type'] == 'Integer':
            xml_str += "        android:numeric=\"integer\"\n"
        xml_str += "        android:textColor=\"@color/black\"\n"
        if above_name == 'NONE':
            xml_str += "        android:layout_alignParentTop=\"true\"\n"
        else:
            xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        xml_str += "        android:layout_toRightOf=\"@+id/NAMELabel\"\n"
        xml_str += "        android:background=\"@android:drawable/editbox_background\" />\n"

        xml_str += "    <Button\n"
        xml_str += "        android:id=\"@+id/NAMEPlusButton\"\n"
        xml_str += "        android:layout_width=\"wrap_content\"\n"

        if self.custom_buttons:
            xml_str += "        android:layout_height=\"47dp\"\n"
            xml_str += "        android:background=\"@layout/custom_button\"\n"
        else:
            xml_str += "        android:layout_height=\"wrap_content\"\n"

        xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        xml_str += "        android:layout_toRightOf=\"@+id/NAMEEntry\"\n"
        xml_str += "        android:text=\"@string/match_plus\"/>\n"

        xml_str += "    <Button\n"
        xml_str += "        android:id=\"@+id/NAMEMinusButton\"\n"
        xml_str += "        android:layout_width=\"wrap_content\"\n"

        if self.custom_buttons:
            xml_str += "        android:layout_height=\"47dp\"\n"
            xml_str += "        android:background=\"@layout/custom_button\"\n"
        else:
            xml_str += "        android:layout_height=\"wrap_content\"\n"

        xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        xml_str += "        android:layout_toRightOf=\"@+id/NAMEPlusButton\"\n"
        xml_str += "        android:text=\"@string/match_minus\" />\n"

        xml_str += "    <Button\n"
        xml_str += "        android:id=\"@+id/NAMESelectButton\"\n"
        xml_str += "        android:layout_width=\"wrap_content\"\n"

        if self.custom_buttons:
            xml_str += "        android:layout_height=\"47dp\"\n"
            xml_str += "        android:background=\"@layout/custom_button\"\n"
        else:
            xml_str += "        android:layout_height=\"wrap_content\"\n"

        xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        xml_str += "        android:layout_toRightOf=\"@+id/NAMEMinusButton\"\n"
        xml_str += "        android:text=\"@string/match_select\" />\n"

        # Add in the plus/minus buttons...        
        xml_str += "    <!-- End NAME field match group -->\n\n"
        
        return xml_str

    def gen_java_declarations_string(self):
        java_str = '    private EditText NAMEEntry;\n'
        java_str += '    private Button NAMEPlusButton;\n'
        java_str += '    private Button NAMEMinusButton;\n'
        java_str += '    private Button NAMESelectButton;\n'
        
        return java_str

    def gen_java_init_string(self):
        java_str = '        NAMEEntry = (EditText) findViewById(R.id.NAMEEntry);\n'
        java_str += '        NAMEPlusButton = (Button) findViewById(R.id.NAMEPlusButton);\n'
        java_str += '        NAMEMinusButton = (Button) findViewById(R.id.NAMEMinusButton);\n'
        java_str += '        NAMESelectButton = (Button) findViewById(R.id.NAMESelectButton);\n'

        return java_str

    def gen_java_button_handler(self):
        java_str = ''
        
        java_str += '        NAMEPlusButton.setOnClickListener(new OnClickListener(){\n'
        java_str += '            public void onClick(View v){\n'
        java_str += '                Integer value=1;\n'
        java_str += '                if ( !NAMEEntry.getText().toString().isEmpty() ) {\n'
        java_str += '                    value = Integer.parseInt(NAMEEntry.getText().toString());\n'
        java_str += '                    value += 1;\n'
        java_str += '                }\n'
        java_str += '                SetTeamFromFields( value );\n'
        java_str += '            }\n'
        java_str += '        });\n'
        java_str += '\n'
        java_str += '        NAMEMinusButton.setOnClickListener(new OnClickListener(){\n'
        java_str += '            public void onClick(View v){\n'
        java_str += '                Integer value=1;\n'
        java_str += '                if ( !NAMEEntry.getText().toString().isEmpty() ) {\n'
        java_str += '                    value = Integer.parseInt(NAMEEntry.getText().toString());\n'
        java_str += '                    if ( value > 1 )\n'
        java_str += '                        value -= 1;\n'
        java_str += '                }\n'
        java_str += '                SetTeamFromFields( value );\n'
        java_str += '            }\n'
        java_str += '        });\n'
        java_str += '\n'        
        java_str += '        NAMESelectButton.setOnClickListener(new OnClickListener(){\n'
        java_str += '            public void onClick(View v){\n'
        java_str += '                Integer value=1;\n'
        java_str += '                if ( !NAMEEntry.getText().toString().isEmpty() ) {\n'
        java_str += '                    value = Integer.parseInt(NAMEEntry.getText().toString());\n'
        java_str += '                    if ( value == 0 )\n'
        java_str += '                        value = 1;\n'
        java_str += '                }\n'
        java_str += '                SetTeamFromFields( value );\n'
        java_str += '            }\n'
        java_str += '        });\n'
        java_str += '\n'        
        java_str += '        NAMEEntry.setOnFocusChangeListener(new View.OnFocusChangeListener()\n'
        java_str += '        {\n'
        java_str += '            @Override\n'
        java_str += '            public void onFocusChange(View v, boolean hasFocus)\n'
        java_str += '            {\n'
        java_str += '                if (!hasFocus) {\n'
        java_str += '                    Integer value;\n'
        java_str += '                    if ( !NAMEEntry.getText().toString().isEmpty() ) {\n'
        java_str += '                        value = Integer.parseInt(NAMEEntry.getText().toString());\n'
        java_str += '                    } else {\n'
        java_str += '                        value = 1;\n'
        java_str += '                    }\n'
        java_str += '\n'
        java_str += '                    SetTeamFromFields( value );\n'
        java_str += '                }\n'
        java_str += '            }\n'
        java_str += '        });\n'
        java_str += '\n'        

        return java_str

    def gen_java_discard_handler(self):
        java_str = ''
        
        # no discard handlers for the match group control, we want to leave the match number
        
        return java_str

    def gen_java_save_handler(self):
        java_str = ''
        java_str += '\n        if ( !NAMEEntry.getText().toString().isEmpty() )\n'
        java_str += '            buffer.append(\"NAME:\" + NAMEEntry.getText().toString() + eol);\n'
        
        return java_str
    
    def gen_java_reload_handler(self):
        java_str = ''
        java_str += '                } else if ( token.equalsIgnoreCase(\"NAME\")) {\n'
        java_str += '                    NAMEEntry.setText(tokenizer.nextToken());\n'

        return java_str

    helper_func_str = '''
    private void SetTeamFromFields( Integer match ) {
        String compRound="";
        if (Comp_RoundQualRadioButton.isChecked())
            compRound = Comp_RoundQualRadioButton.getText().toString();
        else if (Comp_RoundQuartersRadioButton.isChecked())
            compRound = Comp_RoundQuartersRadioButton.getText().toString();
        else if (Comp_RoundSemisRadioButton.isChecked())
            compRound = Comp_RoundSemisRadioButton.getText().toString();
        else if (Comp_RoundFinalsRadioButton.isChecked())
            compRound = Comp_RoundFinalsRadioButton.getText().toString();
        else {
            new AlertDialog.Builder(MatchScoutingAppActivity.this)
            .setTitle("Error!")
            .setMessage("Competition Round Not Specified")
            .setNeutralButton("OK", null)
            .show();
            
            return;
        }

        String alliance="";
        if (AllianceBlueRadioButton.isChecked())
            alliance = AllianceBlueRadioButton.getText().toString();
        else if (AllianceRedRadioButton.isChecked())
            alliance = AllianceRedRadioButton.getText().toString();
        else {
            new AlertDialog.Builder(MatchScoutingAppActivity.this)
            .setTitle("Error!")
            .setMessage("Alliance Not Specified")
            .setNeutralButton("OK", null)
            .show();
            
            return;
        }

        String position="";
        if (Position1RadioButton.isChecked())
            position = Position1RadioButton.getText().toString();
        else if (Position2RadioButton.isChecked())
            position = Position2RadioButton.getText().toString();
        else if (Position3RadioButton.isChecked())
            position = Position3RadioButton.getText().toString();
        else {
            new AlertDialog.Builder(MatchScoutingAppActivity.this)
            .setTitle("Error!")
            .setMessage("Position Not Specified")
            .setNeutralButton("OK", null)
            .show();                            

            return;
        }
        
        String matchStr = match.toString();
        String teamStr = GetTeamFromMatchSchedule( compRound, alliance, position, matchStr );
        if ( !teamStr.equals("0") )
            TeamEntry.setText(teamStr);
        NAMEEntry.setText(matchStr);
    }
'''
    def gen_java_helper_functions(self):
        java_str = self.helper_func_str
        
        return java_str


