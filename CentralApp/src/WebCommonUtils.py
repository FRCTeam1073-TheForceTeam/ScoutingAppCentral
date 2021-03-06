import os
import json

import AttributeDefinitions
import DbSession
import DataModel
import CompAlias
import FileSync
import WebEventData
import WebTeamData
import WebAttributeDefinitions

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

def get_myteam():    
    my_config = ScoutingAppMainWebServer.global_config
    return my_config['my_team']
    
def get_mywebsite():    
    my_config = ScoutingAppMainWebServer.global_config
    return my_config['my_website']
    
def get_comp_list():
    
    my_config = ScoutingAppMainWebServer.global_config
    complist = list()
    season = my_config['this_season']
    this_comp = my_config['this_competition']
    complist.append(this_comp+season)
    
    other_competitions = CompAlias.get_comp_alias_list()

    for comp in other_competitions:
        if comp and comp.upper() != my_config['this_competition'].upper():
            complist.append(comp+season)

    return complist

def get_short_comp_list(season=None):
    
    my_config = ScoutingAppMainWebServer.global_config
    complist = list()
    if season == None:
        season = my_config['this_season']
    this_comp = my_config['this_competition']
    complist.append(this_comp)
    
    other_competitions = CompAlias.get_comp_alias_list()
    
    for comp in other_competitions:
        if comp and comp.upper() != my_config['this_competition'].upper():
            complist.append(comp)

    return complist

def get_season_list():
    
    my_config = ScoutingAppMainWebServer.global_config
    this_season = my_config['this_season']
    
    season_list = list()
    season_list.append( this_season )
       
    try:
        past_seasons = my_config['past_seasons'].split(',')
    except:
        past_seasons = list()

    for season in past_seasons:
        season_list.append(season.lstrip())
    
    return season_list

def get_comp_and_eventcode_list(season=None):
    
    my_config = ScoutingAppMainWebServer.global_config
    complist = list()
    if season == None:
        season = my_config['this_season']
    this_comp = my_config['this_competition']
    complist.append((this_comp,CompAlias.get_eventcode_by_alias(this_comp)))
    
    other_competitions = CompAlias.get_comp_and_eventcode_list()
    
    for comp in other_competitions:
        if comp and comp[0].upper() != my_config['this_competition'].upper():
            complist.append(comp)

    return complist

# retrieve the list of competitions that the specified team has been scouted, including this competition
def get_team_comp_list(this_comp, team):
    
    my_config = ScoutingAppMainWebServer.global_config
    complist = list()
    
    if this_comp == None:
        this_comp = my_config['this_competition'] + my_config['this_season']
        season = my_config['this_season']
    else:
        season = map_comp_to_season(this_comp)
        
    complist.append(this_comp)
    
    team_complist = WebTeamData.get_team_event_list_from_tba(my_config, team, season)
    if not team_complist:
        session = DbSession.open_db_session(my_config['db_name'] + my_config['this_season'])
        team_scores = DataModel.getTeamScore(session, team)
        for score in team_scores:
            comp = score.competition.upper()
            # currently, the competition season is stored in the database
            # as part of the competition. So, we need to add it for the comparison,
            # but not as we define the complist itself
            if comp != this_comp.upper():
                complist.append(comp)
        session.remove()
                
    else:
        for comp in team_complist:
            if comp.upper() != this_comp.upper():
                complist.append(comp)
            
    return complist

# retrieve a list of team info name/value pairs
def get_team_info_str(team):
    
    my_config = ScoutingAppMainWebServer.global_config
    session = DbSession.open_db_session(my_config['db_name'] + my_config['this_season'])

    team_info_str=list()
    team_info = DataModel.getTeamInfo(session, int(team))
    if team_info:
        team_info_str.append(('Team Nickname',team_info.nickname,'string'))
        team_info_str.append(('Affiliation',team_info.fullname,'string'))
        team_info_str.append(('Location',team_info.location,'string'))
        team_info_str.append(('Rookie Season',team_info.rookie_season,'string'))
        team_info_str.append(('Website',team_info.website,'link'))

    session.remove()
    return team_info_str

def get_issue_types():
    my_config = ScoutingAppMainWebServer.global_config
    issue_types = my_config['issue_types'].split(',')
    return issue_types

def get_attr_list(short_comp=None):
    my_config = ScoutingAppMainWebServer.global_config
    attr_list = list()
    
    attrdef_filename = get_attrdef_filename(short_comp)
    if attrdef_filename is not None:
        attr_definitions = AttributeDefinitions.AttrDefinitions(my_config)
        attr_definitions.parse(attrdef_filename)
        attr_dict = attr_definitions.get_definitions()
        attr_list = attr_dict.keys()
        attr_list.sort()
                
    return attr_list

def get_attrdef_filename(short_comp=None,comp=None):
    my_config = ScoutingAppMainWebServer.global_config
    attrdef_filename = None

    if short_comp is None and comp is not None:
        short_comp,_ = split_comp_str(comp)

    # if the competition name is provided, look up the config for a 
    # specific attrbute definition file
    if short_comp is not None:
        event_info = CompAlias.get_event_info(short_comp)
        if event_info is not None:
            if event_info.event_attr is not None:
                attrdef_filename = './config/' + event_info.event_attr
                
    # if no competition specific attribute definition file is set, then
    # use the global configuration
    if attrdef_filename is None:
        if len(my_config['attr_definitions']):
            attrdef_filename = './config/' + my_config['attr_definitions']
            
    # make sure that the filename exists, else return None
    if attrdef_filename is not None and not os.path.exists(attrdef_filename):
        attrdef_filename = None
        my_config['logger'].debug( 'Attribute File %s Does Not Exist' % attrdef_filename )
        print 'Attribute File %s Does Not Exist' % attrdef_filename
        
    return attrdef_filename
    
def get_filter_list():
    my_config = ScoutingAppMainWebServer.global_config
    filter_list = list()
    
    filter_list = WebAttributeDefinitions.get_filter_list()
    
    return filter_list
    
def get_file_list(dir_name,thumbnail_size=None):
    file_list = []    

    # if the directory name starts with a slash, prepend a '.' to make it a relative
    # path from this point.
    if dir_name.startswith('/'):
        dir_name = '.' + dir_name
                
    for root, dirs, files in os.walk(dir_name):
        # strip off any leading '.' in the root path so that the resulting entry
        # will have an absolute path
        root = root.lstrip('.')
        
        #print 'Root:', root, ' Dirs: ', dirs, ' Files:', files
        for name in files:
            # build the path to the file by joining the root with the filename.
            # note that we will replace any backslash in the resulting path with forward
            # slashes
            file_path = os.path.join(root,name).replace('\\','/')
            if thumbnail_size != None:
                thumbnail_name = thumbnail_size + '_' + name
                thumbnail_path = os.path.join(root+'/Thumbnails/', thumbnail_name).replace('\\','/')
                file_entry = (file_path, name,thumbnail_path)
            else:
                # create a tuple with the path and the file name so that a hyperlink can be easily 
                # generated from the file entry
                file_entry = (file_path, name)
            
            # and append the entry to the list
            file_list.append(file_entry)
                
    return file_list

def get_event_info_str(event_name, season=None):
    my_config = ScoutingAppMainWebServer.global_config
    
    if event_name.startswith('201'):
        year = event_name[0:4]
        event_code = event_name[4:]
    else:
        if season == None:
            year = my_config['this_season']
        else:
            year = season
        event_code = event_name

    event_dict = WebEventData.get_event_info_dict(my_config, year, event_code)
    
    event_info_str=list()
    if event_dict:
        event_info_str.append(('Name',event_dict['name'],'string'))
        event_info_str.append(('Code',event_dict['event_code'].upper(),'string'))
        event_info_str.append(('Location',event_dict['location_name'],'string'))
        event_info_str.append(('Start Date',event_dict['start_date'],'string'))
        event_info_str.append(('End Date',event_dict['end_date'],'string'))
    else:
        # We couldn't load the event information, so let's try to pull from local
        # alias file
        event_info = CompAlias.get_event_by_code(event_code)
        if event_info:
            event_info_str.append(('Name', event_info.event_name, 'string'))
            event_info_str.append(('Code', event_info.event_code, 'string'))
        else:
            event_info_str.append(('Name', 'Unknown','string'))
            event_info_str.append(('Code', event_code.upper(),'string'))

    return event_info_str

def map_event_code_to_comp(event_name, season=None):
    my_config = ScoutingAppMainWebServer.global_config
    
    if season == None:
        if event_name.startswith('201'):
            season = event_name[0:4]
        else:
            season = my_config['this_season']
    
    if event_name.startswith('201'):
        comp = event_name[4:]
    else:
        comp = event_name
    event_info = CompAlias.get_event_by_code(comp)
    if event_info != None:
        comp = event_info.event_alias           
    
    return comp + season

def map_event_code_to_short_comp(event_name, season=None):
    my_config = ScoutingAppMainWebServer.global_config
    
    if season == None:
        if event_name.startswith('201'):
            season = event_name[0:4]
        else:
            season = my_config['this_season']
    
    if event_name.startswith('201'):
        comp = event_name[4:]
    else:
        comp = event_name
    event_info = CompAlias.get_event_by_code(comp)
    if event_info != None:
        comp = event_info.event_alias
    
    return comp        

def map_event_code_to_season(event_name):
    my_config = ScoutingAppMainWebServer.global_config
    if event_name.startswith('201'):
        season = event_name[0:4]
    else:
        season = my_config['this_season']
                
    return season        

def map_comp_to_event_code(comp):
    my_config = ScoutingAppMainWebServer.global_config
    
    if len(comp) > 4:
        season_str = comp[-4:]
        if season_str.startswith( '201' ):
            comp = comp[0:-4]
            
    event_info = CompAlias.get_event_by_alias(comp)
    if event_info != None:
        comp = event_info.event_code
            
    return comp
    
def map_comp_to_season(comp):
    my_config = ScoutingAppMainWebServer.global_config
    
    season = my_config['this_season']
    
    # now overwrite the season if the competition string has an embedded year
    if len(comp) > 4:
        season_str = comp[-4:]
        if season_str.startswith( '201' ):
            season = season_str
    
    return season

def split_comp_str(comp):
    valid_season = False

    if len(comp) > 4:
        # check if the competition starts with the year, like how FIRST does it (e.g. 2017mabos)
        if comp.startswith( '201' ):
            season_str = comp[0:4]
            comp_str = comp[4:]
            valid_season = True
        else:
            comp_str = comp[0:(len(comp)-4)]
            season_str = comp[-4:]
            if season_str.startswith( '201' ):
                valid_season = True
    if valid_season:
        return (comp_str, season_str)
    else:
        return None

def get_district_string():
    
    my_config = ScoutingAppMainWebServer.global_config
    
    try:
        district_string = my_config['my_district']
    except:
        district_string = 'District'
        
    return district_string

def get_geo_location_json( include_teams=True, include_events=True ):

    geo_locations = {}
    filename = 'geo_coordinates_for'
        
    my_config = ScoutingAppMainWebServer.global_config
    session = DbSession.open_db_session(my_config['db_name'] + my_config['this_season'])
    
    if include_events:
        filename += '_Events'
        events = session.query(DataModel.EventInfo).all()
        for event in events:
            if event.geo_location is not None:
                geo_locations[event.event_key] = json.loads(event.geo_location)
    
    if include_teams:
        filename += '_Teams'
        teams = session.query(DataModel.TeamInfo).all()
        for team in teams:
            if team.geo_location is not None:
                team_key = 'frc%d' % team.team
                geo_locations[team_key] = json.loads(team.geo_location)
    
    geo_location_json = json.dumps(geo_locations)
    geo_location_js = 'var %s = \'%s\';' % (filename,geo_location_json)

    # store the geo location information to a file, too
    try:
        FileSync.put( my_config, 'GlobalData/%s.json' % (filename), 'text', geo_location_json)
        FileSync.put( my_config, 'GlobalData/%s.js' % (filename), 'text', geo_location_js)
    except:
        raise
    
    session.remove()
    return geo_location_json

def get_team_participation_json():

    team_participation = {}
    filename = 'team_participation'
        
    my_config = ScoutingAppMainWebServer.global_config
    session = DbSession.open_db_session(my_config['db_name'] + my_config['this_season'])
    
    teams = session.query(DataModel.TeamInfo).all()
    for team in teams:
        team_key = 'frc%d' % team.team
        if team.first_competed is not None:
            info = {}
            info['first_competed'] = team.first_competed
            info['last_competed'] = team.last_competed
            team_participation[team_key] = info
    
    team_participation_json = json.dumps(team_participation)
    team_participation_js = 'var %s = \'%s\';' % (filename,team_participation_json)

    # store the geo location information to a file, too
    try:
        FileSync.put( my_config, 'GlobalData/%s.json' % (filename), 'text', team_participation_json)
        FileSync.put( my_config, 'GlobalData/%s.js' % (filename), 'text', team_participation_js)
    except:
        raise
    
    session.remove()
    return team_participation_json

def handle_geo_overlap( geo_dict, geo_location_str, direction_flag=True ):
    
    try:
         location = json.loads(geo_dict[geo_location_str])
         print 'Overlapping location: %s' % str(location)
         if direction_flag:
             location["lng"] += .01
         else:
             location["lat"] += .01
             
         return handle_geo_overlap(geo_dict, json.dumps(location), direction_flag)
    except:
         geo_dict[geo_location_str] = geo_location_str
         return json.loads(geo_location_str)


if __name__ == "__main__":
    
    geo_locations = {}
    filename = 'geo_coordinates_for'
        
    db_name = 'scouting2016'
    session = DbSession.open_db_session(db_name)
    
    filename += '_Events'
    events = session.query(DataModel.EventInfo).all()
    
    event_geo_info = {}
    team_geo_info = {}
    
    for event in events:
        if event.geo_location is not None:
            try:
                event_year_info = event_geo_info[event.event_year]
                geo_locations[event.event_key] = handle_geo_overlap( event_year_info, event.geo_location, True )
            except:
                event_geo_info[event.event_year] = {}
                event_geo_info[event.event_year][event.geo_location] = event.geo_location 
                geo_locations[event.event_key] = json.loads(event.geo_location)
    

    filename += '_Teams'
    teams = session.query(DataModel.TeamInfo).all()
    for team in teams:
        if team.geo_location is not None:
            team_key = 'frc%d' % team.team
            geo_locations[team_key] = handle_geo_overlap( team_geo_info, team.geo_location, False )
    
    geo_location_json = json.dumps(geo_locations)
    geo_location_js = 'var %s = \'%s\';' % (filename,geo_location_json)

    # store the geo location information to a file, too
    FileSync.put( {}, 'GlobalData/%s.json' % (filename), 'text', geo_location_json)
    FileSync.put( {}, 'GlobalData/%s.js' % (filename), 'text', geo_location_js)

    session.remove()


