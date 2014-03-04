import os
import AttributeDefinitions

def get_html_head(title_str = 'FIRST Team 1073 - The Force Team'):
    head_str  = '<head>\n'
    head_str += '<meta charset="utf-8" />\n'
    head_str += '<title>%s</title>\n' % title_str
    head_str += '<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=1, minimum-scale=0.0, maximum-scale=2.0" />\n'
    head_str += '<link rel="shortcut icon" href="/static/media/images/1073-favicon.ico" type="image/x-icon" />\n'
    head_str += '<link rel="stylesheet" href="/static/media/css/style.css" type="text/css" media="screen" />\n'

    head_str += '	<style type="text/css" title="currentStyle">\n'
    head_str += '		@import "/static/media/css/demo_page.css";\n'
    head_str += '		@import "/static/media/css/demo_table.css";\n'
    head_str += '	</style>\n'

    head_str += '<script type="text/javascript" language="javascript" src="/static/media/js/jquery.js"></script>\n'
    head_str += '<script type="text/javascript" language="javascript" src="/static/media/js/jquery.dataTables.js"></script>\n'
    head_str += '</head>\n'
    
    return head_str

import ScoutingAppMainWebServer

def get_comp_list():
    
    my_config = ScoutingAppMainWebServer.global_config
    complist = list()
    complist.append(my_config['this_competition'])
    
    other_competitions = my_config['other_competitions'].split(',')
    for comp in other_competitions:
        if comp and comp != my_config['this_competition']:
            complist.append(comp)

    return complist

def get_issue_types():
    my_config = ScoutingAppMainWebServer.global_config
    issue_types = my_config['issue_types'].split(',')
    return issue_types

def get_attr_list():
    my_config = ScoutingAppMainWebServer.global_config
    attr_list = list()
    
    attrdef_filename = './config/' + my_config['attr_definitions']
    if os.path.exists(attrdef_filename):
        attr_definitions = AttributeDefinitions.AttrDefinitions()
        attr_definitions.parse(attrdef_filename)
        attr_dict = attr_definitions.get_definitions()
        attr_list = attr_dict.keys()
        attr_list.sort()
                
    return attr_list
