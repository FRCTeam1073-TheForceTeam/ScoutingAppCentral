'''
Created on Feb 7, 2013

@author: ksthilaire
'''

from web import form
from myform import pureform as pureform

# Form definition and callback class for the application configuration settings
cfg_this_comp_label = "Competition:"
cfg_this_event_code_label = "Competition Event Code:"
cfg_attr_defs_label = "Attributes Definitions File:"
cfg_my_team_label = "My Team Number:"
cfg_other_comp_label = "Other Competitions:"
cfg_scouting_db_name_label = "Scouting Database Name:"
cfg_debrief_db_name_label = "Debrief Database Name:"
cfg_issues_db_name_label = "Issues Database Name:"
cfg_issues_db_master_label = "Issues Database Master:"
cfg_users_db_name_label = "Users Database Name:"


cfg_issues_db_master_options = ['Yes', 'No']

cfgform = pureform( 
    form.Textbox(cfg_my_team_label, size=60),
    form.Textbox(cfg_this_comp_label, size=60),
    form.Textbox(cfg_this_event_code_label, size=60),
    form.Textbox(cfg_other_comp_label, size=60),
    form.Textbox(cfg_attr_defs_label, size=60),
    form.Textbox(cfg_scouting_db_name_label, size=60),
    form.Textbox(cfg_issues_db_name_label, size=60),
    form.Dropdown(cfg_issues_db_master_label, cfg_issues_db_master_options),
    form.Textbox(cfg_debrief_db_name_label, size=60),
    form.Textbox(cfg_users_db_name_label, size=60))

def get_form(global_config):
    global_config['logger'].debug( 'GET Set Configuration Form' )
    
    form = cfgform()
    form[cfg_my_team_label].value = global_config['my_team']
    form[cfg_this_comp_label].value = global_config['this_competition']
    form[cfg_this_event_code_label].value = global_config['event_code']
    form[cfg_other_comp_label].value = global_config['other_competitions']
    form[cfg_attr_defs_label].value = global_config['attr_definitions']
    form[cfg_scouting_db_name_label].value = global_config['db_name']
    form[cfg_issues_db_name_label].value = global_config['issues_db_name']
    form[cfg_issues_db_master_label].value = global_config['issues_db_master']
    form[cfg_debrief_db_name_label].value = global_config['debriefs_db_name']
    form[cfg_users_db_name_label].value = global_config['users_db_name']
        
    return form

def process_form(global_config, form):
    global_config['logger'].debug( 'Process Set Configuration Form' )

    global_config['my_team'] = form[cfg_my_team_label].value
    global_config['this_competition'] = form[cfg_this_comp_label].value
    global_config['event_code'] = form[cfg_this_event_code_label].value
    global_config['other_competitions'] = form[cfg_other_comp_label].value
    global_config['attr_definitions'] = form[cfg_attr_defs_label].value
    
    global_config['db_name'] = form[cfg_scouting_db_name_label].value
    global_config['issues_db_name'] = form[cfg_issues_db_name_label].value
    global_config['issues_db_master'] = form[cfg_issues_db_master_label].value
    global_config['debriefs_db_name'] = form[cfg_debrief_db_name_label].value
    global_config['users_db_name'] = form[cfg_users_db_name_label].value
    
    write_config(global_config, './config/ScoutingAppConfig.txt')
    
def write_config(config_dict, config_filename):
    cfg_file = open(config_filename, 'w+')
    for key, value in config_dict.iteritems():
        if key != 'logger':
            if value != None and value != 'None':
                line = '%s=%s\n' % (key,value)
                cfg_file.write(line)
    cfg_file.close()

