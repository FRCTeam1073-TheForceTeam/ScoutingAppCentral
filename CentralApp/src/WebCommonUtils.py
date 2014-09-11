import os
import AttributeDefinitions
import DbSession
import DataModel
import WebEventData

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
    season = my_config['this_season']
    this_comp = my_config['this_competition']
    complist.append(this_comp+season)
    
    other_competitions = my_config['other_competitions'].split(',')

    for comp in other_competitions:
        if comp and comp != my_config['this_competition']:
            complist.append(comp+season)

    return complist

# retrieve the list of competitions that the specified team has been scouted, including this competition
def get_team_comp_list(this_comp, team):
    
    my_config = ScoutingAppMainWebServer.global_config
    complist = list()
    
    if this_comp == None:
        this_comp = my_config['this_competition'] + my_config['this_season']
        
    complist.append(this_comp)
    
    session = DbSession.open_db_session(my_config['db_name'])
    team_scores = DataModel.getTeamScore(session, team)
    for score in team_scores:
        comp = score.competition
        # currently, the competition season is stored in the database
        # as part of the competition. So, we need to add it for the comparison,
        # but not as we define the complist itself
        if comp != this_comp:
            complist.append(comp)
    return complist

# retrieve a list of team info name/value pairs
def get_team_info_str(team):
    
    my_config = ScoutingAppMainWebServer.global_config
    session = DbSession.open_db_session(my_config['db_name'])

    team_info_str=list()
    team_info = DataModel.getTeamInfo(session, int(team))
    if team_info:
        team_info_str.append(('Team Nickname',team_info.nickname,'string'))
        team_info_str.append(('Affiliation',team_info.fullname,'string'))
        team_info_str.append(('Location',team_info.location,'string'))
        team_info_str.append(('Rookie Season',team_info.rookie_season,'string'))
        team_info_str.append(('Website',team_info.website,'link'))
    return team_info_str

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

def get_event_info_str(event_name):
    my_config = ScoutingAppMainWebServer.global_config
    
    year = event_name[0:4]
    event_code = event_name[4:]
    event_dict = WebEventData.get_event_info_dict(my_config, year, event_code)

    event_info_str=list()
    if event_dict:
        event_info_str.append(('Name',event_dict['name'],'string'))
        event_info_str.append(('Code',event_dict['event_code'].upper(),'string'))
        event_info_str.append(('Location',event_dict['location'],'string'))
        event_info_str.append(('Start Date',event_dict['start_date'],'string'))
        event_info_str.append(('End Date',event_dict['end_date'],'string'))
    return event_info_str

def map_event_code_to_comp(event_name):
    my_config = ScoutingAppMainWebServer.global_config
    season = my_config['this_season']
    
    #TODO: Need to replace this hardcoded behavior with something more dynamic/configurable
    #       We may also just want to adopt the FIRST short event codes, too, though they
    #       aren't all that obvious what they refer to.
    comp = event_name[4:]
    if comp == 'mabos':
        comp = 'NU' + season
    elif comp == 'nhdur':
        comp = 'UNH' + season
    elif comp == 'rismi':
        comp = 'RI' + season
    elif comp == 'necmp':
        comp = 'NECMP' + season
    else:
        pass
            
    return comp        

def map_comp_to_event_code_to_comp(comp):
    my_config = ScoutingAppMainWebServer.global_config
    season = my_config['this_season']
    
    #TODO: Need to replace this hardcoded behavior with something more dynamic/configurable
    #       We may also just want to adopt the FIRST short event codes, too, though they
    #       aren't all that obvious what they refer to.
    event_code = comp.replace(season,'')
    if event_code == 'NU':
        event_code = 'mabos'
    elif event_code == 'UNH':
        event_code = 'nhdur'
    elif event_code == 'RI':
        event_code = 'rismi'
    elif event_code == 'NECMP':
        event_code = 'necmp'
    else:
        pass
            
    return event_code        
    
    