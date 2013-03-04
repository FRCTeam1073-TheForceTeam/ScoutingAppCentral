'''
Created on Feb 7, 2013

@author: ksthilaire
'''

from web import form

# Form definition and callback class for the application configuration settings
cfg_this_comp_label = "Competition:"
cfg_db_master_label = "Database Master:"
cfg_attr_defs_label = "Attributes Definitions File:"

cfg_db_master_options = ['Yes', 'No']

cfgform = form.Form( 
    form.Textbox(cfg_this_comp_label, size=60),
    form.Textbox(cfg_attr_defs_label, size=60),
    form.Dropdown(cfg_db_master_label, cfg_db_master_options))

def get_form(global_config):
    global_config['logger'].debug( 'GET Set Configuration Form' )
    
    form = cfgform()
    form[cfg_this_comp_label].value = global_config['this_competition']
    form[cfg_attr_defs_label].value = global_config['attr_definitions']
    form[cfg_db_master_label].value = global_config['issues_db_master']
        
    return form

def process_form(global_config, form):
    global_config['logger'].debug( 'Process Set Configuration Form' )

    global_config['this_competition'] = form[cfg_this_comp_label].value
    global_config['attr_definitions'] = form[cfg_attr_defs_label].value
    
    global_config['issues_db_master'] = form[cfg_db_master_label].value
    
    
    
