'''
Created on Dec 18, 2014

@author: ken_sthilaire
'''

import os

event_info_table  = {}
event_alias_table = {}

class EventInfo(object):
    event_code = None
    event_name = None
    event_alias = None
    event_attr = None
    
    def __init__(self, code, alias, name, attr=None):
        self.event_code  = code.upper()
        self.event_alias = alias
        self.event_name  = name
        self.event_attr  = attr
        
def get_event_by_code( event_code ):
    try:
        event_info = event_info_table[event_code.upper()]
    except:
        event_info = None
        
    return event_info

def get_event_by_alias( event_alias ):
    try:
        event_info = event_alias_table[event_alias.upper()]
    except:
        event_info = None
        
    return event_info

def get_event_info( event_code ):
    # try to access the event from the table by event code
    event_info = get_event_by_code( event_code )

    if event_info is None:
        # if not found, then try again from the event alias table
        event_info = get_event_by_alias( event_code )

    return event_info

#
# map the event alias to the event_code. if there is no alias,
# then return the alias as the event_code
#
def get_eventcode_by_alias( event_alias ):
    try:
        event_info = event_alias_table[event_alias.upper()]
        event_code = event_info.event_code
    except:
        event_info = None
        event_code = event_alias.upper()
        
    return event_code

def get_comp_alias_list():
    comp_list = []

    for alias in event_alias_table:
        comp_list.append(alias)

    return comp_list
        
def get_comp_eventcode_list():
    comp_list = []

    for alias in event_alias_table:
        comp_list.append(event_alias_table[alias][1])

    return comp_list
        
def get_comp_and_eventcode_list():
    comp_list = []

    for alias in event_alias_table:
        comp_list.append((alias,event_alias_table[alias].event_code))

    return comp_list

def read_comp_alias_config(config_filename):
    if os.path.exists(config_filename):
        cfg_file = open(config_filename, 'r')
        for cfg_line in cfg_file:
            if cfg_line.startswith('#'):
                continue
            cfg_line = cfg_line.rstrip()
            if cfg_line.count(',') == 2:
                attr_override=None
                (event_code,comp_alias,event_name) = cfg_line.split(',',2)
            elif cfg_line.count(',') == 3:
                (event_code,comp_alias,event_name,attr_override) = cfg_line.split(',',3)
            else:
                # ignore lines that don't have an equal sign in them
                print 'Unexpected competition line: %s' % cfg_line
                continue   

            event_info = EventInfo(event_code.upper(),comp_alias.upper(),event_name,attr_override)
            event_info_table[event_info.event_code] = event_info
            event_alias_table[event_info.event_alias] = event_info

        cfg_file.close()

def write_comp_alias_config(config_dict, config_filename):
    cfg_file = open(config_filename, 'w+')
    cfg_file.write('# Competition event alias definitions\n')
    for event_info in event_info_table.iteritems():
        line = '%s,%s,%s\n' % (event_info.event_code,event_info.event_alias,event_info.event_name)
        cfg_file.write(line)
    cfg_file.close()
