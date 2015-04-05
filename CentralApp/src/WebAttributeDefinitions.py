'''
Created on Feb 21, 2014

@author: ken_sthilaire
'''

from web import form
from myform import pureform as pureform

import os

import AttributeDefinitions
import DataModel
import ConfigUtils

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


def get_attr_tree_json(global_config, filter_name = None):
    
    global_config['logger'].debug( 'GET Attribute Definitions Tree JSON' )

    attrdef_filename = './config/' + global_config['attr_definitions']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)
    
    #categories = attr_definitions.get_sub_categories()
    
    attr_filter = get_saved_filter(filter_name)
    
    result = []
    result.append('{ "item": [\n')
    
    if filter_name != None:
        checked = 0
    else:
        checked = 1
        
    opened = 1
    result.append('    { "text": "%s", "open": %d, "checked": %d, "id": "Skip_%s", "item": [ \n' % ('All Attributes',opened,checked,'All'))
    
    category_dict = attr_definitions.get_attr_dict_by_category()
    for category, attrlist in category_dict.iteritems():
        if category != 'Uncategorized':
            result.append('    { "text": "%s", "checked": %d, "id": "Skip_%s", "item": [ \n' % (category,checked,category))
            for attrname in sorted(attrlist):
                if filter_name is None:
                    result.append('    { "text": "%s", "checked": %d, "id": "%s", "item": [ ] }' % (attrname,checked,attrname))
                else:
                    if attrname in attr_filter:
                        check_attr = 1
                    else:
                        check_attr = 0
                    result.append('    { "text": "%s", "checked": %d, "id": "%s", "item": [ ] }' % (attrname,check_attr,attrname))
                result.append(',\n')
                          
            if len(attrlist) > 0:
                result = result[:-1]
                result.append('\n')

            result.append( '    ] }')
            result.append(',\n')
            
    attrlist = category_dict['Uncategorized']
    if len( attrlist ) > 0:
        for attrname in sorted(attrlist):
            if filter_name is None:
                result.append('    { "text": "%s", "checked": %d, "id": "%s", "item": [ ] }' % (attrname,checked,attrname))
            else:
                if attrname in attr_filter:
                    check_attr = 1
                else:
                    check_attr = 0
                result.append('    { "text": "%s", "checked": %d, "id": "%s", "item": [ ] }' % (attrname,check_attr,attrname))
                    
            result.append(',\n')
                      
    result = result[:-1]
    result.append('],\n    "id": 1 \n}\n')
    result.append('],\n    "id": 0 \n}\n')
                                 
    json_str = ''.join(result)

    return json_str

saved_filters = {}
def get_saved_filter( filter_name ):
    global saved_filters
    
    if len(saved_filters) == 0:
        ConfigUtils.read_config( saved_filters, './config/savedfilters.txt' )
        
    filter_list = []
    try:
        name = filter_name.title()
        filter_str = saved_filters[name]
        filter_list = filter_str.split('+')
    except:
        pass
    
    return filter_list
    
def get_saved_filter_json( filter_name ):
    global saved_filters
    
    if len(saved_filters) == 0:
        ConfigUtils.read_config( saved_filters, './config/savedfilters.txt' )
        
    result = []
    result.append('{ "filters": [\n')
    
    if filter_name != None:
        try:
            filter_name = filter_name.title()
            filter_str = saved_filters[filter_name]
        except:
            pass
    
        result.append('   { "name": "%s", "filter_str": "%s" }\n' % (filter_name,filter_str))
    else:
        for filter_name, filter_str in saved_filters.iteritems():
            result.append('   { "name": "%s", "filter_str": "%s" }' % (filter_name,filter_str))
            result.append(',\n')
            
        if len(saved_filters) > 0:
            result = result[:-1]
    
    result.append('] }\n')
    
    json_str = ''.join(result) 
    return json_str
    
def save_filter(filter_name, filter_str):
    
    global saved_filters
    
    if len(saved_filters) == 0:
        ConfigUtils.read_config( saved_filters, './config/savedfilters.txt' )
            
    name = filter_name.title()
    saved_filters[name] = filter_str
    
    ConfigUtils.write_config( saved_filters, './config/savedfilters.txt' )
    
    return

def delete_filter(filter_name):
    
    global saved_filters

    if len(saved_filters) == 0:
        ConfigUtils.read_config( saved_filters, './config/savedfilters.txt' )
            
    name = filter_name.title()
    try:
        del saved_filters[name]
        ConfigUtils.write_config( saved_filters, './config/savedfilters.txt' )
    except KeyError:
        pass
    
def get_filter_list():
    
    global saved_filters

    if len(saved_filters) == 0:
        ConfigUtils.read_config( saved_filters, './config/savedfilters.txt' )
            
    return saved_filters.keys()

    