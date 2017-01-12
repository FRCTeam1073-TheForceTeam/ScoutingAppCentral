
# task group definitions
taskgroups = ( 
               'Launcher', 
               'Collector',
               'Defense_Manip',
               'Chassis',
               'Inspection',
               'Camera',
               'Autonomous',
               'Dashboard',
               'Drive_Team',
               'Scouting',
               'Spirit',
               'Awards',
               'Safety'
             )

# issue categories
categories = (1,2,3)

def gen_list_declaration_snippet( item ):
    format_str = '    private String[] %s_list;\n' % item
    return format_str

def gen_load_taskgroups_snippet( item ):
    format_str = '                } else if ( token.equalsIgnoreCase("%s_email_list")) {\n                    %s_list = tokenizer.nextToken().split(";");\n' % (item,item)
    return format_str

def gen_checkbox_declaration_snippet( category, item ):
    format_str = '    private CheckBox Issue%d_Taskgroup%sCheckBox;\n' % (category,item)
    return format_str

def gen_save_handler_snippet( category, item ):
    format_str  = '        if (Issue%d_Taskgroup%sCheckBox.isChecked()) {\n' % (category,item)
    format_str += '            if (!Issue%d_TaskgroupIsChecked) {\n' % (category)
    format_str += '                Issue%d_TaskgroupIsChecked = true;\n' % (category)
    format_str += '                buffer.append(Issue%d_TaskgroupSelection + Issue%d_Taskgroup%sCheckBox.getText().toString());\n' % (category,category,item)
    format_str += '            } else {\n'
    format_str += '                buffer.append("," + Issue%d_Taskgroup%sCheckBox.getText().toString());\n' % (category,item)
    format_str += '            }\n'
    format_str += '        }\n'
    return format_str

def gen_reload_handler_snippet( category, item ):
    format_str  = '                    if ( parseFieldForValue( valueStr, "%s") )\n' % item
    format_str += '                        Issue%d_Taskgroup%sCheckBox.setChecked(true);\n' % (category, item)
    format_str += '                    else\n'
    format_str += '                        Issue%d_Taskgroup%sCheckBox.setChecked(false);\n' % (category, item)
    return format_str

def gen_discard_handler_snippet( category, item ):
    format_str  = '        Issue%d_Taskgroup%sCheckBox.setChecked(false);\n' % (category,item)
    return format_str

def gen_checkbox_init_snippet( category, item ):
    format_str = '        Issue%d_Taskgroup%sCheckBox = (CheckBox) findViewById(R.id.Issue%d_Taskgroup%sCheckBox);\n' % (category,item,category,item)
    return format_str

def gen_is_checked_snippet( category, item):
    format_str  = '        if (Issue%d_Taskgroup%sCheckBox.isChecked()) {\n' % (category,item)
    format_str += '            if (groupChecked == true)\n'
    format_str += '                notifyGroups += ":";\n'
    format_str += '            groupChecked = true;\n'
    format_str += '            notifyGroups += Issue%d_Taskgroup%sCheckBox.getText().toString();\n' % (category,item)
    format_str += '            addArrayToSet(%s_list, notifySet);\n' % item
    format_str += '        }\n'
    return format_str


