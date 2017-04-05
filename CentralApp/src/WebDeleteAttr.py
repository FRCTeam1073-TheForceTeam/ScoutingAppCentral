'''
Created on Apr 14, 2015

@author: ken_sthilaire
'''
from web import form
from myform import pureform as pureform
import os
import AttributeDefinitions
import DbSession
import DataModel
import ProcessFiles
import WebCommonUtils

# Form definition and callback class for the application configuration settings
attr_delete_season_label = "Season:"
attr_delete_comp_label = "Competition:"
attr_delete_team_number_label = "Team Number:"
attr_delete_attribute_name_label = "Attribute Name:"
attr_delete_old_value_label = "Attribute Value:"
attr_delete_file_label = "Scouting Data File:"
attr_remove_file_processed_label = "Remove From Processed Files:"

yes_no_options = ['No', 'Yes']

attr_delete_form = pureform( 
    form.Textbox(attr_delete_season_label),
    form.Textbox(attr_delete_comp_label),
    form.Textbox(attr_delete_team_number_label),
    form.Textbox(attr_delete_attribute_name_label, size=60),
    form.Textbox(attr_delete_old_value_label, size=60) )

file_delete_form = pureform( 
    form.Textbox(attr_delete_season_label),
    form.Textbox(attr_delete_comp_label),
    form.Textbox(attr_delete_file_label, size=60),
    form.Dropdown(attr_remove_file_processed_label, yes_no_options ) )

def get_delete_attr_form(global_config):
    global_config['logger'].debug( 'GET Attribute Delete Form' )
    
    form = attr_delete_form()
        
    form[attr_delete_season_label].value = global_config['this_season']
    form[attr_delete_comp_label].value = global_config['this_competition']
        
    return form

def process_delete_attr_form(global_config, form):
    global_config['logger'].debug( 'Process Attribute Delete Form' )

    season = form[attr_delete_season_label].value
    comp = form[attr_delete_comp_label].value
    team = form[attr_delete_team_number_label].value
    attr_name = form[attr_delete_attribute_name_label].value
    old_value = form[attr_delete_old_value_label].value
    
    # Initialize the database session connection
    db_name  = global_config['db_name'] + global_config['this_season']
    session  = DbSession.open_db_session(db_name)
    
    attrdef_filename = WebCommonUtils.get_attrdef_filename(short_comp=comp)
    if attrdef_filename is not None:
        attr_definitions = AttributeDefinitions.AttrDefinitions(global_config)
        attr_definitions.parse(attrdef_filename)
        attr_def = attr_definitions.get_definition(attr_name)

        try:
            DataModel.deleteAttributeValue(session, team, comp+season, attr_name, old_value, attr_def)
            result = 'Scouting Data Attribute Value %s Successfully Removed From %s' % (old_value,attr_name)
            session.commit()
        except ValueError as reason:   
            result = 'Error Removing Scouting Data Attribute Value %s From %s: %s' % (old_value,attr_name,reason)
                
    session.remove()
    return result

def get_delete_file_form(global_config):
    global_config['logger'].debug( 'GET Attribute Delete Form' )
    
    form = file_delete_form()
        
    form[attr_delete_season_label].value = global_config['this_season']
    form[attr_delete_comp_label].value = global_config['this_competition']
    form[attr_remove_file_processed_label].value = 'No'        
    return form

def process_delete_file_form(global_config, form):
    global_config['logger'].debug( 'Process Attribute Delete Form' )

    data_filename = form[attr_delete_file_label].value
    if form[attr_remove_file_processed_label].value == 'Yes':
        remove_from_processed_files = True
    else:
        remove_from_processed_files = False
    
    # Initialize the database session connection
    db_name  = global_config['db_name'] + global_config['this_season']
    session  = DbSession.open_db_session(db_name)
    
    attrdef_filename = WebCommonUtils.get_attrdef_filename(short_comp=global_config['this_competition'])
    if attrdef_filename is not None:
        attr_definitions = AttributeDefinitions.AttrDefinitions(global_config)
        attr_definitions.parse(attrdef_filename)

        try:
            ProcessFiles.remove_file_data(global_config, session, attr_definitions, \
                                          data_filename, remove_from_processed_files)
            result = 'Scouting Data File %s Attributes Successfully Removed' % (data_filename)
            session.commit()
        except ValueError as reason:   
            result = 'Error Removing Scouting Data File %s: %s' % (data_filename, reason)
    
    session.remove()
    return result
