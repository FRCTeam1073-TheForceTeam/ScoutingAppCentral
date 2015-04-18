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
attr_modify_season_label = "Season:"
attr_modify_comp_label = "Competition:"
attr_modify_team_number_label = "Team Number:"
attr_modify_attribute_name_label = "Attribute Name:"
attr_modify_old_value_label = "Old Attribute Value:"
attr_modify_new_value_label = "New Attribute Value:"

attr_modify_form = pureform( 
    form.Textbox(attr_modify_season_label),
    form.Textbox(attr_modify_comp_label),
    form.Textbox(attr_modify_team_number_label),
    form.Textbox(attr_modify_attribute_name_label, size=60),
    form.Textbox(attr_modify_old_value_label, size=60),
    form.Textbox(attr_modify_new_value_label, size=60))

def get_form(global_config):
    global_config['logger'].debug( 'GET Attribute Modify Form' )
    
    form = attr_modify_form()
    
    form[attr_modify_season_label].value = global_config['this_season']
    form[attr_modify_comp_label].value = global_config['this_competition']
        
    return form

def process_form(global_config, form):
    global_config['logger'].debug( 'Process Attribute Modify Form' )

    season = form[attr_modify_season_label].value
    comp = form[attr_modify_comp_label].value
    team = form[attr_modify_team_number_label].value
    attr_name = form[attr_modify_attribute_name_label].value
    old_value = form[attr_modify_old_value_label].value
    new_value = form[attr_modify_new_value_label].value
    
    # Initialize the database session connection
    db_name  = global_config['db_name'] + global_config['this_season']
    session  = DbSession.open_db_session(db_name)
    
    if global_config['attr_definitions'] != None:
        attrdef_filename = './config/' + global_config['attr_definitions']
        if os.path.exists(attrdef_filename):
            attr_definitions = AttributeDefinitions.AttrDefinitions()
            attr_definitions.parse(attrdef_filename)
            attr_def = attr_definitions.get_definition(attr_name)

            try:
                DataModel.modifyAttributeValue(session, team, comp+season, attr_name, old_value, new_value, attr_def)
                result = 'Attribute %s Modified From %s to %s For Team %s' % (attr_name,old_value,new_value,team)
                session.commit()
            except ValueError as reason:   
                result = 'Error Modifying Scouting Addribute %s For Team %s: %s' % (attr_name,team,reason)
    
    return result
    
