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
                            
            attr_definitions.write_attr_overrides();
            competition = global_config['this_competition'] + global_config['this_season']
            if competition == None:
                raise Exception( 'Competition Not Specified!')
            
            DataModel.recalculate_scoring(global_config, competition, attr_definitions)


def get_attr_tree_json(global_config):
    
    global_config['logger'].debug( 'GET Attribute Definitions Tree JSON' )

    attrdef_filename = './config/' + global_config['attr_definitions']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)
    
    #categories = attr_definitions.get_sub_categories()
    
    result = []
    result.append('{ "item": [\n')
    
    checked = 0
    opened = 1
    result.append('    { "text": "%s", "open": %d, "checked": %d, "id": "Skip_%s", "item": [ \n' % ('All Attributes',opened,checked,'All'))
    
    category_dict = attr_definitions.get_attr_dict_by_category()
    for category, attrlist in category_dict.iteritems():
        if category != 'Uncategorized':
            result.append('    { "text": "%s", "checked": %d, "id": "Skip_%s", "item": [ \n' % (category,checked,category))
            for attrname in sorted(attrlist):
                result.append('        { "text": "%s", "checked": %d, "id": "%s", "item": [ ] }' % (attrname,checked,attrname))
                result.append(',\n')
                          
            if len(attrlist) > 0:
                result = result[:-1]
                result.append('\n')

            result.append( '    ] }')
            result.append(',\n')
            
    attrlist = category_dict['Uncategorized']
    if len( attrlist ) > 0:
        for attrname in sorted(attrlist):
            result.append('    { "text": "%s", "checked": %d, "id": "%s", "item": [ ] }' % (attrname,checked,attrname))
            result.append(',\n')
                      
    result = result[:-1]
    result.append('],\n    "id": 1 \n}\n')
    result.append('],\n    "id": 0 \n}\n')
                                 
    json_str = ''.join(result)

    return json_str



