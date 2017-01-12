'''
Created on Feb 7, 2013

@author: ksthilaire
'''

import os
from web import form
from myform import pureform as pureform

import UiGenerator
import AppGenerator
import FileUtils

def get_form(global_config):
    global_config['logger'].debug( 'GET UI Generator' )
        
    form = myform()
    return form



# Form definition and callback class for the user interface code generator
base_dir_label = "Base Project Directory:"
base_root_dir_label = "Base Project Root:"
dest_root_dir_label = "Destination Project Root:"
dest_dir_label = "Destination Project Directory:"
base_project_label = "Base Project Name:"
team_label = "Team Number:"
custom_button_label = "Use Custom Buttons:"

dest_project_label = "Destination Project Name:"
app_name_label = "Application Name:"
app_title_label = "Application Title:"
sheet_type_label = "Sheet Type:"
attr_defs_label = "Attributes Definition File:"
gen_action_label = 'Generate:'

myform = pureform( 
    form.Textbox(base_root_dir_label, size=60),
    form.Textbox(dest_root_dir_label, size=60),
    form.File(attr_defs_label, accept=".xlsx"),
    form.Textbox(team_label, size=10),
    form.Checkbox(custom_button_label),
    form.Dropdown(sheet_type_label, ['Pit', 'Match', 'Issue', 'Debrief', 'Demo'])
    )

    #form.Textbox(attr_defs_label,form.notnull,form.regexp('[\w_-]+\.xlsx', 'Must be .xlsx file'),size=60),
    #form.Dropdown(gen_action_label, ['Complete App', 'UI Components', 'Base App']))

def process_form(global_config, form):
    global_config['logger'].debug( 'Process UI Generator Form' )
    
    season = global_config['this_season']
    team = form[team_label].value
    sheet_type = form[sheet_type_label].value
    
    # form.d.boe and form['boe'].value are equivalent ways of
    # extracting the validated arguments from the form.
    base_root_dir = form[base_root_dir_label].value
    dest_root_dir = form[dest_root_dir_label].value
    attr_defs_file = './config/' + form[attr_defs_label].value
    use_custom_buttons = form.value.has_key(custom_button_label)
    
    try:
        if sheet_type in ('Pit','Match'):
            base_projectname = 'ScoutingApp'
        elif sheet_type in ('Debrief'):
            base_projectname = 'DebriefApp'
        else:
            err_str = 'Unsupported Sheet Type: %s' % (sheet_type)
            raise Exception(err_str)

    
        base_dir_label = '%sBase' % base_projectname
        base_project_path = os.path.join(base_root_dir, base_dir_label)
        dest_projectname = '%s%s' % (sheet_type,base_projectname)  
        dest_app_label = '%s %s Scouting Application' % (season,sheet_type)
        dest_app_name = '%s Scouter' % (sheet_type)
        dest_project_dir = '%s%s-%s' % (season,dest_projectname,team)
        
        dest_project_path = os.path.join(dest_root_dir, dest_project_dir)
            
        generated_code_fragments = UiGenerator.gen_ui(global_config,
                                                      attr_defs_file, \
                                                      sheet_type, \
                                                      create_fragment_file=True,
                                                      use_custom_buttons=use_custom_buttons)
        
        AppGenerator.prepare_destination_project( base_project_path, base_projectname, dest_project_path, dest_projectname, \
                             sheet_type, dest_app_name, dest_app_label )
    
        AppGenerator.update_generated_xml_code(dest_project_path, generated_code_fragments, use_custom_buttons)
    
        AppGenerator.update_generated_java_code(base_projectname, dest_project_path, sheet_type, generated_code_fragments)
    
        #FileUtils.make_zipfile( dest_project_path + '.zip', dest_project_path )
        
        return "User Interface Generated!\n\tSource Directory: %s\n\tDestination Directory: %s\n\tSheet Type: %s\n\tAttribute Definitions File: %s" % \
            (base_root_dir, \
             dest_project_path, \
             sheet_type, \
             form[attr_defs_label].value)    
    except Exception, err_str:
        return str(err_str)
 
