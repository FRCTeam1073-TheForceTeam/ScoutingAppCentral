'''
Created on Feb 7, 2013

@author: ksthilaire
'''

from web import form

# Form definition and callback class for the application configuration settings
cfg_this_comp_label = "Competition:"
cfg_attr_defs_label = "Attributes Definitions File:"
cfgform = form.Form( 
    form.Textbox(cfg_this_comp_label, size=60),
    form.Textbox(cfg_attr_defs_label, size=60))


def get_form(global_config):
    global_config['logger'].debug( 'GET Set Configuration Form' )
        
    form = cfgform()
    return form

def process_form(global_config, form):
    global_config['logger'].debug( 'Process Set Configuration Form' )

    global_config['this_competition'] = form[cfg_this_comp_label].value
    global_config['attr_definitions'] = form[cfg_attr_defs_label].value
    
