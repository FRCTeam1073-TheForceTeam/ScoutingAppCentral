'''
Created on Feb 21, 2014

@author: ken_sthilaire
'''

from web import form
from myform import pureform as pureform

import os

import AttributeDefinitions
import DataModel

attrdef_form = None


attrdef_overrides = {}
attrdef_overrides_filename = './config/attrdef_overrides.txt'


def read_attr_overrides(attr_dict):
    global attrdef_overrides

    if os.path.exists(attrdef_overrides_filename):
        override_file = open(attrdef_overrides_filename, 'r')
        for override_line in override_file:
            if override_line.startswith('#'):
                continue
            override_line = override_line.rstrip()
            if override_line.count('=') > 0:
                (attr,value) = override_line.split('=',1)
                
                if attr_dict.has_key(attr):
                    attr_dict[attr]['Weight'] = value
                attrdef_overrides[attr] = value
            else:
                # ignore lines that don't have an equal sign in them
                pass   
        override_file.close()

def write_attr_overrides(attr_dict):
    global attrdef_overrides
    override_file = open(attrdef_overrides_filename, 'w+')
    #for key, value in attrdef_overrides.iteritems():
    for key, attr_def in sorted(attr_dict.items()):
        attrdef_overrides[key] = attr_def['Weight']
        
    for attr, weight in sorted(attrdef_overrides.items()):
        line = '%s=%s\n' % (attr,weight)
        override_file.write(line)
    override_file.close()

            
 
def init_attr_def_forms(attr_definitions):
    global attrdef_form
 
    attrdef_form = pureform()
    
    attr_dict = attr_definitions.get_definitions()
    
    try:
        for key, attr_def in sorted(attr_dict.items()):
            attrdef_form.inputs += (form.Textbox(key, size=10),)
    except Exception, e:
        print 'Exception: %s' % str(e)

    
def get_attr_def_form(global_config):
    global_config['logger'].debug( 'GET Attribute Definitions Form' )

    form = attrdef_form()
    
    if global_config['attr_definitions'] == None:
        print 'No Attribute Definitions, Skipping Process Files'
    else:
        attrdef_filename = './config/' + global_config['attr_definitions']
        if os.path.exists(attrdef_filename):
            attr_definitions = AttributeDefinitions.AttrDefinitions()
            attr_definitions.parse(attrdef_filename)
            attr_dict = attr_definitions.get_definitions()

            read_attr_overrides(attr_dict)
                                
            for key, attr_def in sorted(attr_dict.items()):
                form[key].value = str(int(float(attr_def['Weight'])))
                
    return form

def process_attr_def_form(global_config, form):
    global_config['logger'].debug( 'Process Attribute Definitions Form' )
    
    if global_config['attr_definitions'] == None:
        print 'No Attribute Definitions, Skipping Process Files'
    else:
        attrdef_filename = './config/' + global_config['attr_definitions']
        if os.path.exists(attrdef_filename):
            attr_definitions = AttributeDefinitions.AttrDefinitions()
            attr_definitions.parse(attrdef_filename)
            attr_dict = attr_definitions.get_definitions()

            for key, attr_def in sorted(attr_dict.items()):
                attr_def['Weight'] = form[key].value
                            
            write_attr_overrides(attr_dict);
            
            DataModel.recalculate_scoring(global_config, attr_definitions)





