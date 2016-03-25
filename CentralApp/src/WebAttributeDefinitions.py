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
import FileSync

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
                try:
                    weight = float(attr_def['Weight'])
                except:
                    weight = 0.0
                form[key].value = str(int(weight))
                
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

def get_attr_def_item_json( global_config, attr_def, attr_filter, checked_ind ):

    attr_name = attr_def['Name']
    result = []
    result.append('    { "text": "%s", "checked": %d, "id": "%s", "item": [' % (attr_name,checked_ind,attr_name))
    
    if attr_def['Control'] == 'Radio' or attr_def['Control'] == 'Checkbox':
        map_values_str = attr_def['Map_Values']
        map_values = map_values_str.split(':')
        for map_value in map_values:
            checked_override = checked_ind
            map_tokens = map_value.split('=')
            map_name = map_tokens[0]
            map_filter_str = '%s=%s' % (attr_name,map_name)
            if map_filter_str in attr_filter:
                checked_override = 1
            result.append('        { "text": "%s", "checked": %d, "id": "%s=%s", "item": [ ] }' % (map_name,checked_override,attr_name,map_name))
            result.append(',\n')
        result = result[:-1]
    
    result.append(' ] }')
    
    result_str = ''.join(result)    
    return result_str

def get_attr_tree_json(global_config, filter_name = None, store_data_to_file=False):
    
    global_config['logger'].debug( 'GET Attribute Definitions Tree JSON' )

    attrdef_filename = './config/' + global_config['attr_definitions']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)
    
    competition = global_config['this_competition'] + global_config['this_season']
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
                checked_ind = 0
                if filter_name is None:
                    # if there is no specified filter, then set the checked indicator based on the overall setting
                    checked_ind = checked
                else:
                    # otherwise, if a filter is specified, then set the checked indicator based on if the attribute
                    # name is specified in the filter list
                    if attrname in attr_filter:
                        checked_ind = 1
                tree_item_str = get_attr_def_item_json( global_config, attr_definitions.get_definition(attrname), attr_filter, checked_ind )
                result.append(tree_item_str)
                result.append(',\n')
                          
            if len(attrlist) > 0:
                result = result[:-1]
                result.append('\n')

            result.append( '    ] }')
            result.append(',\n')
            
    attrlist = category_dict['Uncategorized']
    if len( attrlist ) > 0:
        for attrname in sorted(attrlist):
            checked_ind = 0
            if filter_name is None:
                # if there is no specified filter, then set the checked indicator based on the overall setting
                checked_ind = checked
            else:
                # otherwise, if a filter is specified, then set the checked indicator based on if the attribute
                # name is specified in the filter list
                if attrname in attr_filter:
                    checked_ind = 1
            tree_item_str = get_attr_def_item_json( global_config, attr_definitions.get_definition(attrname), attr_filter, checked_ind )
            result.append(tree_item_str)
            result.append(',\n')
                      
    result = result[:-1]
    result.append('],\n    "id": 1 \n}\n')
    result.append('],\n    "id": 0 \n}\n')
                                 
    json_str = ''.join(result)
    
    if store_data_to_file:
        try:
            if filter_name == None:
                file_name = 'attrtree.json'
            else:
                file_name = 'attrtree_%s.json' % filter_name
            FileSync.put( global_config, '%s/EventData/%s' % (competition,file_name), 'text', json_str)                
        except:
            raise


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
    
def get_saved_filter_json( global_config, filter_name, store_data_to_file=False ):
    global saved_filters
    
    competition = global_config['this_competition'] + global_config['this_season']

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
        for name, filter_str in saved_filters.iteritems():
            result.append('   { "name": "%s", "filter_str": "%s" }' % (name,filter_str))
            result.append(',\n')
            
        if len(saved_filters) > 0:
            result = result[:-1]
    
    result.append('] }\n')
    
    json_str = ''.join(result)
    
    if store_data_to_file:
        try:
            if filter_name == None:
                file_name = 'attrfilters.json'
            else:
                file_name = 'attrfilter_%s.json' % filter_name
            FileSync.put( global_config, '%s/EventData/%s' % (competition,file_name), 'text', json_str)                
        except:
            raise

    return json_str
    
def save_filter(filter_name, filter_str):
    
    global saved_filters
    
    if len(saved_filters) == 0:
        ConfigUtils.read_config( saved_filters, './config/savedfilters.txt' )
            
    name = filter_name.title()
    name = name.replace(' ', '_')
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
    
    filters = saved_filters.keys()
    filters.sort()
    return filters

def update_event_data_files( global_config, directory ):
    
    result = False
    
    # for now, we only support updating files in the EventData directory, so only continue if that's the 
    # directory that was specified.
    if directory.upper() == 'EVENTDATA':
        # call each of the get_event_xxx() functions to attempt to retrieve the json data. This action
        # will also store the json payload to the EventData directory completing the desired 
        # operation
        
        # update the JSON data file for the attribute tree and all filters
        get_saved_filter_json( global_config, filter_name=None, store_data_to_file=True )
        get_attr_tree_json(global_config, filter_name = None, store_data_to_file=True)        
                
        # then update the JSON data files for each of the defined filters 
        filter_list = get_filter_list()
        for name in filter_list:
            get_saved_filter_json( global_config, name, store_data_to_file=True )
            get_attr_tree_json(global_config, name, store_data_to_file=True)        
        
        result = True
        
    return result
    