
import copy

# task group definitions
taskgroups = ( 
                'Feed',
                'Shoot',
                'Fuel',
                'Spirit',
                'Safety',
                'Auto',
                'Dashboard',
                'Scout',
                'Change',
                'Climb',
                'Gear',
                'Chassis',
                'Bumpers',
                'Driveteam',
                'Can',
                'Inspection',
                'Bling',
                'Vision'
                )


# issue categories
categories = (1,2,3)

def load_taskgroups(filename):
    global taskgroups
    
    return taskgroups

def load_categories(filename):
    global categories
    
    return categories

def get_debrief_app_control_defs(taskgroups):
    
    # base attribute definition for the taskgroup checkbox controls on the debrief layout
    base_attr_def = {
            'Control': 'Checkbox', 
            'Sheet': 'Debrief', 
            'Sub_Category': '', 
            'Weight': '0.0', 
            'Options': 'Lines=%d:Items=%d', 
            'Map_Values': '', 
            'Include_In_Report': '', 
            'Database_Store': 'No', 
            'Display_Numeric': 'No', 
            'Statistic_Type': 'None', 
            'Type': 'Map_Integer', 
            'Name': 'Issue%d_Taskgroup'
    }
    
    map_values = ''
    for taskgroup in taskgroups:
        map_values += '%s=1:' % taskgroup
    map_values = map_values.rstrip(':')
    
    items_per_line = 4
    lines = len(taskgroups) / items_per_line
    if len(taskgroups) % items_per_line:
        lines += 1
        
    debrief_control_defs = {}
    for category in categories:
        control_def = copy.deepcopy(base_attr_def)
        control_def['Name'] = control_def['Name'] % category
        control_def['Options'] = control_def['Options'] % (lines,items_per_line)
        control_def['Map_Values'] = map_values
        control_def['Order'] = '%d.0' % category
        control_def['Column_Order'] = '%d' % category
        
        debrief_control_defs[control_def['Name']] = control_def

    return debrief_control_defs

def gen_list_declaration_snippet( item ):
    format_str = '    private String[] %s_list;\n' % item
    return format_str

def gen_list_alloc_snippet( item ):
    format_str = '        %s_list = new String[1];\n' % item
    return format_str

def gen_load_taskgroups_snippet( item ):
    format_str = '                    } else if ( token.equalsIgnoreCase("%s_email_list")) {\n                        %s_list = tokenizer.nextToken().split(";");\n' % (item,item)
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
    format_str  = '            if (Issue%d_Taskgroup%sCheckBox.isChecked()) {\n' % (category,item)
    format_str += '                if (groupChecked == true)\n'
    #format_str += '                    notifyGroups += ":";\n'
    format_str += '                    notifyGroups += ", ";\n'
    format_str += '                groupChecked = true;\n'
    format_str += '                notifyGroups += Issue%d_Taskgroup%sCheckBox.getText().toString();\n' % (category,item)
    format_str += '                addArrayToSet(%s_list, notifySet);\n' % item
    format_str += '            }\n'
    return format_str


