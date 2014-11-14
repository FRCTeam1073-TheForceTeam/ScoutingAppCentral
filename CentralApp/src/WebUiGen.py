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

# Form definition and callback class for the user interface code generator
base_root_dir_label = "Base Project Root:"
base_dir_label = "Base Project Directory:"
base_project_label = "Base Project Name:"
dest_root_dir_label = "Destination Project Root:"
dest_dir_label = "Destination Project Directory:"
dest_project_label = "Destination Project Name:"
app_name_label = "Application Name:"
app_title_label = "Application Title:"
sheet_type_label = "Sheet Type:"
attr_defs_label = "Attributes Definition File:"
gen_action_label = 'Generate:'
myform = pureform( 
    form.Textbox(base_root_dir_label, size=60),
    form.Textbox(base_dir_label, size=60),
    form.Textbox(base_project_label, size=60),
    form.Textbox(dest_root_dir_label, size=60),
    form.Textbox(dest_dir_label, size=60),
    form.Textbox(dest_project_label, size=60),
    form.Textbox(app_name_label, size=60),
    form.Textbox(app_title_label, size=60),
    form.Dropdown(sheet_type_label, ['Pit', 'Match', 'Issue', 'Debrief', 'Demo']), 
    form.Textbox(attr_defs_label,form.notnull,form.regexp('[\w_-]+\.xlsx', 'Must be .xlsx file'),size=60),
    form.Dropdown(gen_action_label, ['Complete App', 'UI Components', 'Base App']))

def get_form(global_config):
    global_config['logger'].debug( 'GET UI Generator' )
        
    form = myform()
    return form

def process_form(global_config, form):
    global_config['logger'].debug( 'Process UI Generator Form' )
    
    # form.d.boe and form['boe'].value are equivalent ways of
    # extracting the validated arguments from the form.
    base_root_dir = form[base_root_dir_label].value
    base_project_path = os.path.join(base_root_dir, form[base_dir_label].value)
    base_projectname = form[base_project_label].value
    dest_root_dir = form[dest_root_dir_label].value
    dest_project_dir = form[dest_dir_label].value
    dest_project_path = os.path.join(dest_root_dir, dest_project_dir)
    dest_projectname = form[dest_project_label].value
    dest_activity_prefix = form[sheet_type_label].value
    dest_app_label = form[app_name_label].value
    dest_app_name = form[app_title_label].value
    attr_defs_file = './config/' + form[attr_defs_label].value
    
    generated_code_fragments = UiGenerator.gen_ui(attr_defs_file, \
                                                  dest_activity_prefix, \
                                                  create_fragment_file=True)
    
    AppGenerator.prepare_destination_project( base_project_path, base_projectname, dest_project_path, dest_projectname, \
                         dest_activity_prefix, dest_app_name, dest_app_label )

    AppGenerator.update_generated_xml_code(dest_project_path, generated_code_fragments)

    AppGenerator.update_generated_java_code(base_projectname, dest_project_path, dest_activity_prefix, generated_code_fragments)

    #FileUtils.make_zipfile( dest_project_path + '.zip', dest_project_path )
    
    return "User Interface Generated!\n\tSource Directory: %s\n\tDestination Directory: %s\n\tSheet Type: %s\n\tAttribute Definitions File: %s\n\tGenerate Action: %s" % \
        (form[base_dir_label].value, \
         form[dest_dir_label].value, \
         form[sheet_type_label].value, \
         form[attr_defs_label].value, \
         form[gen_action_label].value)    
