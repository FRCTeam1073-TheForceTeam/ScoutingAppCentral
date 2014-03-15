'''
Created on Mar 9, 2014

@author: ken_sthilaire
'''
from web import form
from myform import pureform as pureform
import os
import AttributeDefinitions
import DbSession
import DataModel

# Form definition and callback class for the application configuration settings
attr_modify_comp_label = "Competition:"
attr_modify_team_number_label = "Team Number:"
attr_modify_attribute_name_label = "Attribute Name:"
attr_modify_old_value_label = "Old Attribute Value:"
attr_modify_new_value_label = "New Attribute Value:"

attr_modify_form = pureform( 
    form.Textbox(attr_modify_comp_label),
    form.Textbox(attr_modify_team_number_label),
    form.Textbox(attr_modify_attribute_name_label, size=60),
    form.Textbox(attr_modify_old_value_label, size=60),
    form.Textbox(attr_modify_new_value_label, size=60))

def get_form(global_config):
    global_config['logger'].debug( 'GET Attribute Modify Form' )
    
    form = attr_modify_form()
        
    return form

def process_form(global_config, form):
    global_config['logger'].debug( 'Process Attribute Modify Form' )

    comp = form[attr_modify_comp_label].value
    team = form[attr_modify_team_number_label].value
    attr_name = form[attr_modify_attribute_name_label].value
    old_value = form[attr_modify_old_value_label].value
    new_value = form[attr_modify_new_value_label].value
    
    # Initialize the database session connection
    db_name  = global_config['db_name']
    session  = DbSession.open_db_session(db_name)
    
    if global_config['attr_definitions'] != None:
        attrdef_filename = './config/' + global_config['attr_definitions']
        if os.path.exists(attrdef_filename):
            attr_definitions = AttributeDefinitions.AttrDefinitions()
            attr_definitions.parse(attrdef_filename)
            attr_def = attr_definitions.get_definition(attr_name)

            DataModel.modifyAttributeValue(session, team, comp, attr_name, old_value, new_value, attr_def)
            session.commit()
    
