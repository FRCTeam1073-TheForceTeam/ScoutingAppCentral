'''
Created on Feb 7, 2013

@author: ksthilaire
'''

import os
import re
import web
import urllib2

import ImageFileUtils
import AttributeDefinitions
import DbSession
import DataModel
import FileSync
import WebCommonUtils

def get_datafiles(input_dir, pattern, recursive,logger):
    '''Get list of files to be displayed.

    Args:
        input_dir: Directory to search.
        pattern: Regular expression to use to filter files.
        recursive: Whether or not to recurse into input_dir.
        logger: logger for debug printing

    Returns:
        A list of files.
    '''
    
    # make sure that the directory path exists
    try: 
        os.makedirs(input_dir)
    except OSError:
        if not os.path.isdir(input_dir):
            raise

    file_list = []    
    
    if recursive:
        for root, dirs, files in os.walk(input_dir):
            logger.debug( 'Root: %s, Dirs: %s, Files: %s', root, dirs, files)
            for name in files:
                if pattern.match(name):
                    file_list.append(os.path.join(root, name))
    else:
        files = os.listdir(input_dir)
        logger.debug('Files: %s', files)
        for name in files:
            if pattern.match(name):
                file_list.append(os.path.join(input_dir, name))

    logger.debug('File List: %s', file_list)
    return file_list


def get_team_datafiles_page(global_config, name, display_notes=True):
    
    global_config['logger'].debug( 'GET Team Data Files: %s', name )
    session = DbSession.open_db_session(global_config['db_name'] + global_config['this_season'])

    if global_config['attr_definitions'] == None:
        return None
    
    attrdef_filename = './config/' + global_config['attr_definitions']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)
    page=''
    
    team_info = DataModel.getTeamInfo(session, int(name))
    if team_info:
        page += '<h3>Team Info</h3>'
        page += '<li>Team Nickname: ' + team_info.nickname + '</li>'
        page += '<li>Affiliation: ' + team_info.fullname + '</li>'
        page += '<li>Location: ' + team_info.location + '</li>'
        page += '<li>Rookie Season: ' + str(team_info.rookie_season) + '</li>'
        page += '<li>Website: <a href="' + team_info.website + '">' + team_info.website + '</a></li>'
        page += '<br>'
     
    competitions = []
    this_comp = global_config['this_competition']
    season = global_config['this_season']
    competitions.append(this_comp+season)
    competitions_str = global_config['other_competitions']
    competitions_str = competitions_str.replace(this_comp,'')
    if competitions_str.count(',') > 0:
        other_comps = competitions_str.split(',')
        for other_comp in other_comps:
            if other_comp != '':
                competitions.append(other_comp+season)
    elif competitions_str != '':
        competitions.append(competitions_str+season)
        
    for comp in competitions:
        if comp != '':
            input_dir = './static/data/' + comp + '/ScoutingData/'
            pattern = 'Team' + name + '_' + '[a-zA-Z0-9_]*.txt'
            datafiles = get_datafiles(input_dir, re.compile(pattern), False, global_config['logger'])
            
            input_dir = './static/data/' + comp + '/ScoutingPictures/'
            pattern = 'Team' + name + '_' + '[a-zA-Z0-9_]*.jpg|mp4'
            mediafiles = get_datafiles(input_dir, re.compile(pattern), False, global_config['logger'])
                        
            if len(datafiles) == 0 and len(mediafiles) == 0:
                continue
            
            page += '<hr>'
            page += '<h3> ' + comp + '</h3>'

            team_attributes = DataModel.getTeamAttributesInOrder(session, name, comp)
            if len(team_attributes) > 0:
                page += '<ul>'
                page += '<h3>Scouting Data Summary:</h3>'
                
                page += '<ul>'
                page += '<table border="1" cellspacing="5">'
                page += '<tr>'
                page += '<th>Attribute Name</th>'
                page += '<th>Matches</th>'
                page += '<th>Cumulative Value</th>'
                page += '<th>Average Value</th>'
                #page += '<th>Last Value</th>'
                page += '<th>All Values</th>'
                page += '</tr>'
    
                for attribute in team_attributes:
                    attr_def = attr_definitions.get_definition( attribute.attr_name )
                    include_attr = False
                    if attr_def:
                        if attr_def.has_key('Include_In_Team_Display') \
                                and attr_def['Include_In_Team_Display'] == 'Yes':
                                include_attr = True
                        elif attr_def.has_key('Include_In_Report') \
                                and attr_def['Include_In_Report'] == 'Yes':
                            include_attr = True
                        elif attr_def.has_key('Weight') \
                                and attr_def.has_key('Weight') != '0':
                            include_attr = True

                    if include_attr == True:   
                        page += '<tr>'
                        if attr_def.has_key('Display_Name'):
                            page += '<td>%s</td>' % attr_def['Display_Name']
                        else:
                            page += '<td>%s</td>' % attr_def['Name']
                            
                        page += '<td>%s</td>' % str(attribute.num_occurs)
                        page += '<td>%s</td>' % str(attribute.cumulative_value)
                        page += '<td>%0.2f</td>' % (attribute.avg_value)
                        #page += '<td>%s</td>' % str(attribute.attr_value)
                        page += '<td>%s</td>' % attribute.all_values
                        page += '</tr>'
                        
                page += '</table>'    
                page += '</ul>'
                page += '</ul>'

            if len(datafiles) > 0:         
                page += '<ul>'
                page += '<h3>Pit and Match Data:</h3>'
                page += '<ul>'
                for filename in datafiles:
                    segments = filename.split('/')
                    basefile = segments[-1]
                    # the following line inserts a hyperlink to the file itself, the second line
                    # inserts a hyperlink to a url that allows the webserver to create a nicer display of
                    # the file contents
                    #page += '<li><a href="' + filename.lstrip('.') + '">' + basefile + '</a></li>'
                    page += '<li><a href="' + '/ScoutingData/' + comp + '/' + basefile + '">' + basefile + '</a></li>'
                page += '</ul>'

            if len(mediafiles) > 0:         
                page += '<h3>Pictures and Videos:</h3>'
                page += '<ul>'
                for filename in mediafiles:
                    segments = filename.split('/')
                    basefile = segments[-1]
                    page += '<li><a href="' + filename.lstrip('.') + '">' + basefile + '</a></li>'
                page += '</ul>'
            page += '</ul>'

    if display_notes == True:        
        page += '<hr>'
        page += '<h3> Notes for Team ' + name + '</h3>'
        page += '<ul>'
            
        comp = global_config['this_competition'] + global_config['this_season']
        
        team_notes = DataModel.getTeamNotes(session, name, comp)
        for note in team_notes:
            page += '<li>' + note.data + '</li>'
        
        page += '</ul>'
    
    return page

def get_team_server_page(global_config, name):
        
    global_config['logger'].debug( 'GET Team Server: %s', name )
    
    session = DbSession.open_db_session(global_config['db_name'] + global_config['this_season'])
    
    web.header('Content-Type', 'application/json')
    result = []
    result.append('{ "attributes": [\n')
    comp = global_config['this_competition'] + global_config['this_season']
    team_attributes = DataModel.getTeamAttributes(session, name, comp)
    for attribute in team_attributes:
        result.append(attribute.json())
        result.append(',\n')
    if len(team_attributes) > 0:
        result = result[:-1]
    result.append(']}')
    return ''.join(result)

def get_team_score_page(global_config, name):
        
    global_config['logger'].debug( 'GET Team Score: %s', name )
    
    session = DbSession.open_db_session(global_config['db_name'] + global_config['this_season'])
    
    web.header('Content-Type', 'application/json')
    result = []
    result.append('{ "score": [')
    comp = global_config['this_competition'] + global_config['this_season']
    team_score = DataModel.getTeamScore(session, name, comp)
    for score in team_score:
        result.append(score.json())
        result.append(',\n')
    if len(team_score) > 0:
        result = result[:-1]
    result.append(']}')
    return ''.join(result)

def get_team_notes_page(global_config, name):
        
    global_config['logger'].debug( 'GET Team Notes: %s', name )
    
    session = DbSession.open_db_session(global_config['db_name'] + global_config['this_season'])
    
    #web.header('Content-Type', 'application/json')
    notes_string = ''
    comp = global_config['this_competition'] + global_config['this_season']
    team_notes = DataModel.getTeamNotes(session, name, comp)
    for note in team_notes:
        notes_string += note.data + '\n'
    return notes_string

def get_team_rankings_page(global_config, comp=None):
        
    global_config['logger'].debug( 'GET Team Rankings' )
    
    session = DbSession.open_db_session(global_config['db_name'] + global_config['this_season'])
        
    web.header('Content-Type', 'application/json')
    result = []
    result.append('{ "rankings": [\n')
    
    if comp == None:
        comp = global_config['this_competition'] + global_config['this_season']       
        
    team_rankings = DataModel.getTeamsInRankOrder(session, comp, False)
    for team in team_rankings:
        # round the score to an integer value
        team.score = float(int(team.score))
        result.append(team.json())
        result.append(',\n')
    if len(team_rankings) > 0:
        result = result[:-1]
    result.append(']}')
    return ''.join(result)

def get_team_rankings_array(global_config):
        
    global_config['logger'].debug( 'GET Team Rankings Array' )
    
    session = DbSession.open_db_session(global_config['db_name'] + global_config['this_season'])
        
    web.header('Content-Type', 'application/json')
    result = []
    result.append('[')
    comp = global_config['this_competition'] + global_config['this_season']
    team_rankings = DataModel.getTeamsInRankOrder(session, comp)
    for team in team_rankings:
        data_str = '[%d,%d]' % (team.team,int(team.score))
        result.append(data_str)
        result.append(',')
    if len(team_rankings) > 0:
        result = result[:-1]
    result.append(']')
    return ''.join(result)


def get_team_attr_rankings_page(global_config, comp, attr_name):
        
    global_config['logger'].debug( 'GET Team Attribute Rankings' )
    
    session = DbSession.open_db_session(global_config['db_name'] + global_config['this_season'])
        
    attrdef_filename = './config/' + global_config['attr_definitions']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)
    attr = attr_definitions.get_definition(attr_name)
    try:
        stat_type = attr['Statistic_Type']
    except:
        stat_type = 'Total'

    web.header('Content-Type', 'application/json')
    result = []
    result.append('{ "rankings": [\n')
            
    team_rankings = DataModel.getTeamAttributesInRankOrder(session, comp, attr_name, False)
    for team in team_rankings:
        if stat_type == 'Average':
            value = int(team.cumulative_value/team.num_occurs)
        else:
            value = int(team.cumulative_value)
        data_str = '{ "team": %d, "value": %d }' % (team.team,value)
        result.append(data_str)
        result.append(',\n')
    if len(team_rankings) > 0:
        result = result[:-1]
        result.append('\n')
    result.append(']}')
    return ''.join(result)

def get_team_score_breakdown_json(global_config, name, comp=None, store_json_file=False):
        
    global_config['logger'].debug( 'GET Team Score Breakdown: %s', name )
    
    if comp == None:
        comp = global_config['this_competition'] + global_config['this_season']
        season = global_config['this_season']
    else:
        season = WebCommonUtils.map_comp_to_season(comp)
    session = DbSession.open_db_session(global_config['db_name'] + season)
    
    attrdef_filename = './config/' + global_config['attr_definitions']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)
    
    web.header('Content-Type', 'application/json')
    result = []

    result.append('{ "score_breakdown": [\n')

    team_attributes = DataModel.getTeamAttributesInOrder(session, name, comp)
    for attribute in team_attributes:
        attr_def = attr_definitions.get_definition( attribute.attr_name )
        if attr_def:
            try:
                stat_type = attr_def['Statistic_Type']
            except:
                stat_type = 'Total'

            weight = int(float(attr_def['Weight']))
            if weight != 0:
                if stat_type == 'Average':
                    value = int(attribute.cumulative_value/attribute.num_occurs)
                else:
                    value = int(attribute.cumulative_value)
                data_str = '{"attr_name": "%s", "raw_score": %d, "weighted_score": %d}' % (attribute.attr_name,int(value),int(weight*value)) 
                result.append(data_str)
                result.append(',\n')
    if len(team_attributes) > 0:
        result = result[:-1]
        result.append('\n')
    result.append(']}')
    
    json_str = ''.join(result)
    
    if store_json_file is True:
        try:
            FileSync.put( global_config, '%s/EventData/team%s_scouting_scorebreakdown.json' % (comp,name), 'text', json_str)
        except:
            raise
        
    return json_str


def get_team_attributes_page(global_config):
        
    global_config['logger'].debug( 'GET Team Attributes' )
    
    session = DbSession.open_db_session(global_config['db_name'] + global_config['this_season'])
    
    attrdef_filename = './config/' + global_config['attr_definitions']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)
    
    web.header('Content-Type', 'application/json')
    result = []
    result.append('{ "attributes": [\n')
    comp = global_config['this_competition'] + global_config['this_season']
    team_rankings = DataModel.getTeamsInRankOrder(session, comp)
    for team_entry in team_rankings:
        result.append("{ 'Team': " + str(team_entry.team))
        result.append(", 'Score': " + '%.2f' % team_entry.score )
        team_attributes = DataModel.getTeamAttributesInOrder(session, team_entry.team, comp)
        for attribute in team_attributes:
            attr_def = attr_definitions.get_definition( attribute.attr_name )
            if attr_def:
                weight = int(float(attr_def['Weight']))
                if weight != 0:
                    result.append( ", '" + attribute.attr_name + "': ")
                    if ( attr_def['Statistic_Type'] == 'Total'):
                        #result.append( str(attribute.cumulative_value) )
                        result.append( DataModel.mapValueToString(attribute.cumulative_value, attribute.all_values, attr_def, True) )
                    elif ( attr_def['Statistic_Type'] == 'Average'):
                        #result.append( str(attribute.avg_value) )
                        result.append( DataModel.mapValueToString(attribute.avg_value, attribute.all_values, attr_def, True) )
                    else:
                        #result.append( str(attribute.attr_value) )
                        result.append( DataModel.mapValueToString(attribute.attr_value, attribute.all_values, attr_def, True) )
                    
        result.append(' }')
        result.append(',\n')
    if len(team_rankings) > 0:
        result = result[:-1]
        result.append('\n')
    result.append(']}')
    return ''.join(result)

def get_team_datafile_page(global_config, filename):
        
    global_config['logger'].debug( 'GET Team Data File: %s', filename )
        
    comp, name = filename.split('/', 1)
    filepath = './static/data/' + comp + '/ScoutingData/' + name
    datafile = open( filepath, "r" )
    
    page =''
    page += '<table border="1" cellspacing="5">'    
    page += '<tr>'
    page += '<th>Attribute Name</th>'
    page += '<th>Attribute Value</th>'
    page += '</tr>'
    
    while 1:
        lines = datafile.readlines(100)
        if not lines:
            break
        for line in lines:
            line = line.rstrip('\n')
            name, value = line.split(':')
            
            page += '<tr>'
            page += '<td>' + name + '</td>'
            page += '<td>' + value + '</td>'
            page += '</tr>'
            
    page += '</table>'
    return page

def get_team_datafile_json(global_config, filename, store_json_file=False):
        
    global_config['logger'].debug( 'GET Team Data File Json: %s', filename )
        
    comp, fname = filename.split('/', 1)
    filepath = './static/data/' + comp + '/ScoutingData/' + fname
    datafile = open( filepath, "r" )
    
    team = fname.split('_')[0].lstrip('Team')

    result = []
    result.append('{ "competition": "%s",\n' % comp)
    result.append('  "team": "%s",\n' % team)
    result.append('  "filename": "%s",\n' % fname)
    result.append('  "scouting_data": [\n')
    
    while 1:
        lines = datafile.readlines(500)
        if not lines:
            break
        for line in lines:
            line = line.rstrip('\n')
            try:
                name, value = line.split(':',1)
            except:
                pass

            result.append('   { "name": "%s", "value": "%s" }' % (name,value))
            result.append(',\n')
            
        if len(lines) > 0:
            result = result[:-1]
    result.append('] }\n')
    
    json_str = ''.join(result)
    
    if store_json_file is True:
        try:
            short_fname = fname.replace('.txt','')
            FileSync.put( global_config, '%s/EventData/team%s_scouting_file_%s.json' % (comp,team,short_fname), 'text', json_str)
        except:
            raise
        
    return json_str


def get_team_info_json(global_config, comp, name, store_json_file=False):   
    global_config['logger'].debug( 'GET Team %s Info', name )
    
    season = WebCommonUtils.map_comp_to_season(comp)
    session = DbSession.open_db_session(global_config['db_name'] + season)
    
    team_info = DataModel.getTeamInfo(session, int(name))
    
    web.header('Content-Type', 'application/json')
    result = []
    result.append('{ "team": "%s", "team_data" : [\n' % name)
    result.append('   { "name": "%s", "value": "%s" }' % ('nickname', team_info.nickname))
    result.append(',\n')
    result.append('   { "name": "%s", "value": "%s" }' % ('affiliation', team_info.fullname))
    result.append(',\n')
    result.append('   { "name": "%s", "value": "%s" }' % ('location', team_info.location))
    result.append(',\n')
    result.append('   { "name": "%s", "value": "%s" }' % ('rookie_season', team_info.rookie_season))
    result.append(',\n')
    result.append('   { "name": "%s", "value": "%s" }' % ('website', team_info.website))
    result.append('\n')
    
    result.append(' ] }\n')
    
    json_str = ''.join(result)

    if store_json_file is True:
        try:
            FileSync.put( global_config, '%s/EventData/team%s_teaminfo.json' % (comp,name), 'text', json_str)
        except:
            raise
        
    return json_str

     
def get_team_score_json(global_config, name, comp, store_json_file=False):
        
    global_config['logger'].debug( 'GET Team %s Score For Competition %s', name, comp )
    
    season = WebCommonUtils.map_comp_to_season(comp)
    session = DbSession.open_db_session(global_config['db_name'] + season)
    
    result = []
    result.append('{ "competition" : "%s", "team" : "%s", ' % (comp,name))
    team_scores = DataModel.getTeamScore(session, name, comp)
    if len(team_scores)==1:
        result.append('"score": "%s" }' % team_scores[0].score)
    else:
        result.append('  "score": [')
        for score in team_scores:
            result.append(score.json())
            result.append(',\n')
        if len(team_scores) > 0:
            result = result[:-1]
        result.append(']}')
        
    json_str = ''.join(result)
    
    if store_json_file is True:
        try:
            FileSync.put( global_config, '%s/EventData/team%s_scouting_score.json' % (comp,name), 'text', json_str)
        except:
            raise
        
    return json_str

def get_team_scouting_data_summary_json(global_config, comp, name, store_json_file=False):
    
    global_config['logger'].debug( 'GET Team %s Scouting Data For Competition %s', name, comp )
    
    season = WebCommonUtils.map_comp_to_season(comp)
    session = DbSession.open_db_session(global_config['db_name'] + season)

    if global_config['attr_definitions'] == None:
        return None
    
    attrdef_filename = './config/' + global_config['attr_definitions']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)

    result = []

    result.append('{ "competition" : "%s", "team" : "%s",\n' % (comp,name))
    result.append('  "scouting_data_summary" : [\n')

    team_attributes = DataModel.getTeamAttributesInOrder(session, name, comp)
    if len(team_attributes) > 0:
        some_attr_added = False
        for attribute in team_attributes:
            attr_def = attr_definitions.get_definition( attribute.attr_name )
            include_attr = False
            if attr_def:
                if attr_def.has_key('Include_In_Team_Display') \
                        and attr_def['Include_In_Team_Display'] == 'Yes':
                        include_attr = True
                elif attr_def.has_key('Include_In_Report') \
                        and attr_def['Include_In_Report'] == 'Yes':
                    include_attr = True
                elif attr_def.has_key('Weight') \
                        and attr_def.has_key('Weight') != '0':
                    include_attr = True

            if include_attr == True:  
                some_attr_added = True
                if attr_def.has_key('Display_Name'):
                    attr_name = attr_def['Display_Name']
                else:
                    attr_name = attr_def['Name']
                result.append('   { "name": "%s", "matches": "%s", "cumulative_value": "%s", "average_value": "%s", "all_values": "%s" }' % \
                              (attr_name,str(attribute.num_occurs),str(attribute.cumulative_value),str(attribute.avg_value),attribute.all_values ))
                result.append(',\n')
        if some_attr_added:
            result = result[:-1]
        
    result.append(' ] }\n')
    json_str = ''.join(result)
    
    if store_json_file is True:   
        try:
            FileSync.put( global_config, '%s/EventData/team%s_scouting_data_summary.json' % (comp,name), 'text', json_str)
        except:
            raise
        
    return json_str

def get_team_scouting_datafiles_json(global_config, comp, name, store_json_file=False):
    
    global_config['logger'].debug( 'GET Team %s Scouting Datafiles For Competition %s', name, comp )

    result = []

    result.append('{ "competition" : "%s", "team" : "%s",\n' % (comp,name))
    result.append('  "scouting_datafiles" : [\n')

    input_dir = './static/data/' + comp + '/ScoutingData/'
    pattern = 'Team' + name + '_' + '[a-zA-Z0-9_]*.txt'
    datafiles = get_datafiles(input_dir, re.compile(pattern), False, global_config['logger'])

    for filename in datafiles:
        segments = filename.split('/')
        basefile = segments[-1]
        
        result.append('   { "filename": "%s" }' % (basefile))
        result.append(',\n')
        
        if store_json_file is True:
            get_team_datafile_json( global_config, comp + '/' + basefile, store_json_file )
    
    if len(datafiles) > 0:         
        result = result[:-1]

    result.append(' ] }\n')
    json_str = ''.join(result)
    
    if store_json_file is True:
        try:
            FileSync.put( global_config, '%s/EventData/team%s_scouting_datafiles.json' % (comp,name), 'text', json_str)
        except:
            raise
        
    return json_str
    
def get_team_scouting_mediafiles_json(global_config, comp, name, store_json_file=False):
    
    global_config['logger'].debug( 'GET Team %s Scouting Mediafiles For Competition %s', name, comp )

    result = []

    result.append('{ "competition" : "%s", "team" : "%s",\n' % (comp,name))
    result.append('  "scouting_mediafiles" : [\n')

    input_dir = './static/data/' + comp + '/ScoutingPictures/'
    pattern = 'Team' + name + '_' + '[a-zA-Z0-9_]*.jpg|mp4'
    mediafiles = get_datafiles(input_dir, re.compile(pattern), False, global_config['logger'])

    for filename in mediafiles:
        segments = filename.split('/')
        basefile = segments[-1]
        
        result.append('   { "filename": "%s" }' % (basefile))
        result.append(',\n')
    
    if len(mediafiles) > 0:         
        result = result[:-1]
        
    result.append(' ],\n')
    result.append('  "thumbnailfiles" : [\n')

    ImageFileUtils.create_thumbnails(mediafiles)
    thumbnail_dir = input_dir + "Thumbnails/"
    pattern = '[0-9]*x[0-9]*_Team' + name + '_' + '[a-zA-Z0-9_]*.jpg|mp4'
    thumbnailfiles = get_datafiles(thumbnail_dir, re.compile(pattern), False, global_config['logger'])
    
    for filename in thumbnailfiles:
        segments = filename.split('/')
        basefile = segments[-1]
        
        result.append('   { "filename": "%s" }' % (basefile))
        result.append(',\n')
    
    if len(thumbnailfiles) > 0:         
        result = result[:-1]

    result.append(' ] }\n')
    json_str = ''.join(result)
    
    if store_json_file is True:
        try:
            FileSync.put( global_config, '%s/EventData/team%s_scouting_mediafiles.json' % (comp,name), 'text', json_str)
        except:
            raise
        
    return json_str

def get_team_scouting_notes_json(global_config, comp, name, store_json_file=False):
    
    global_config['logger'].debug( 'GET Team %s Scouting Notes For Competition %s', name, comp )
    
    season = WebCommonUtils.map_comp_to_season(comp)
    session = DbSession.open_db_session(global_config['db_name'] + season)

    result = []

    result.append('{ "competition" : "%s", "team" : "%s",\n' % (comp,name))
    result.append('  "scouting_notes" : [\n')

    team_notes = DataModel.getTeamNotes(session, name, comp)
    for note in team_notes:
        result.append('   { "tag": "%s", "note": "%s" }' % (note.tag,note.data))
        result.append(',\n')
        
    if len(team_notes) > 0:         
        result = result[:-1]

    result.append(' ] }\n')
    
    json_str = ''.join(result)

    if store_json_file is True:
        try:
            FileSync.put( global_config, '%s/EventData/team%s_scouting_notes.json' % (comp,name), 'text', json_str)
        except:
            raise
        
    return json_str

def get_team_list_json(global_config, comp, store_json_file=False):
    global team_info_dict
    
    global_config['logger'].debug( 'GET Team List For Competition %s', comp )

    season = WebCommonUtils.map_comp_to_season(comp)
    session = DbSession.open_db_session(global_config['db_name'] + season)

    result = []

    result.append('{ "teams" : [\n')

    team_list = DataModel.getTeamsInNumericOrder(session, comp)
    for team in team_list:
        team_info = None
        # TODO - Remove this hardcoded number for the valid team number. This check prevents
        # requesting information for invalid team numbers, which has been known to happen when
        # tablet operators enter bogus team numbers by mistake
        if team.team < 10000:
            team_info = DataModel.getTeamInfo(session, int(team.team))
            
        if team_info:
            result.append('   { "team_number": "%s", "nickname": "%s" }' % (team.team,team_info.nickname))
            result.append(',\n')
        
    if len(team_list) > 0:         
        result = result[:-1]
        result.append(' ] }\n')
        json_str = ''.join(result)
    else:
        json_str = get_team_list_json_from_tba(global_config, comp)

    if store_json_file is True:
        try:
            FileSync.put( global_config, '%s/EventData/%s.json' % (comp,'teams'), 'text', json_str)
        except:
            raise
        
    return json_str

def get_team_list_json_from_tba(global_config, comp):
    
    global_config['logger'].debug( 'GET Team List For Competition From TBA %s', comp )

    result = []
    result.append('{ "teams" : ')
    
    event_code = WebCommonUtils.map_comp_to_event_code(comp)
    season = WebCommonUtils.map_comp_to_season(comp)
    
    url_str = 'http://www.thebluealliance.com/api/v2/event/%s%s/teams?X-TBA-App-Id=frc1073:scouting-system:v01' % (season,event_code.lower())
    event_data = ''
    try:
        event_data = urllib2.urlopen(url_str).read()
    except:
        event_data = '[ ]'
        pass

    result.append( event_data )
    result.append('  }\n')
    return ''.join(result)
    
def get_team_rankings_json(global_config, comp=None, store_json_file=False):
        
    global_config['logger'].debug( 'GET Team Rankings Json' )
    store_data_to_file = False
    
    if comp == None:
        comp = global_config['this_competition'] + global_config['this_season']
        season = global_config['this_season']
    else:
        season = WebCommonUtils.map_comp_to_season(comp)

    session = DbSession.open_db_session(global_config['db_name'] + season)

    result = []
    result.append('{ "rankings": [\n')
    
        
    team_rankings = DataModel.getTeamsInRankOrder(session, comp, False)
    for team in team_rankings:
        # round the score to an integer value
        team.score = float(int(team.score))
        if team.score > 0:
            result.append(team.json())
            result.append(',\n')
    if len(result) > 0:
        result = result[:-1]

    result.append(']}')
    
    json_str = ''.join(result)
    
    if store_json_file is True:
        try:
            FileSync.put( global_config, '%s/EventData/%s.json' % (comp,'scoutingrankings'), 'text', json_str)
        except:
            raise
        
    return json_str

local_picklist = None
def create_picklist_json(global_config, comp=None, store_json_file=False):
        
    global_config['logger'].debug( 'Create Picklist Json' )
    
    global local_picklist
    store_data_to_file = False
    
    if comp == None:
        comp = global_config['this_competition'] + global_config['this_season']
        season = global_config['this_season']
    else:
        season = WebCommonUtils.map_comp_to_season(comp)

    session = DbSession.open_db_session(global_config['db_name'] + season)
    
    result = []
    result.append('{ "picklist": [\n')
            
    local_picklist = DataModel.getTeamsInRankOrder(session, comp, True)
    rank = 1
    for team in local_picklist:
        # round the score to an integer value
        team.score = float(int(team.score))
        if team.score > 0:
            row = '{ "rank" : %d, "team" : %d, "score" : %d, "competition" : "%s" }' % (rank, team.team, int(team.score), team.competition)
            result.append(row)
            result.append(',\n')
            rank += 1
    if len(result) > 0:
        result = result[:-1]

    result.append(']}')
    
    json_str = ''.join(result)
    
    if store_json_file is True:
        try:
            FileSync.put( global_config, '%s/EventData/%s.json' % (comp,'picklist'), 'text', json_str)
        except:
            raise
        
    return json_str
    
def update_picklist_json(global_config, from_position, to_position, comp=None, store_json_file=True):
        
    global_config['logger'].debug( 'Create Picklist Json' )

    global local_picklist
    
    if local_picklist is None:
        create_picklist_json(global_config, comp, store_json_file=True)
                
    result = []
    result.append('{ "picklist": [\n')
    
    if comp == None:
        comp = global_config['this_competition'] + global_config['this_season']
    
    item_to_update = local_picklist.pop( from_position-1 )
    local_picklist.insert(to_position-1, item_to_update)    
    rank = 1
    for team in local_picklist:
        # round the score to an integer value
        team.score = float(int(team.score))
        if team.score > 0:
            row = '{ "rank" : %d, "team" : %d, "score" : %d, "competition" : "%s" }' % (rank, team.team, int(team.score), team.competition)
            result.append(row)
            result.append(',\n')
            rank += 1
    if len(result) > 0:
        result = result[:-1]

    result.append(']}')
    
    json_str = ''.join(result)
    
    if store_json_file is True:
        try:
            FileSync.put( global_config, '%s/EventData/%s.json' % (comp,'picklist'), 'text', json_str)
        except:
            raise
        
    return json_str

def update_team_event_files( global_config, year, event, directory ):
    
    result = False
    
    # for now, we only support updating files in the EventData directory, so only continue if that's the 
    # directory that was specified.
    if directory.upper() == 'EVENTDATA':
        # call each of the get_event_xxx() functions to attempt to retrieve the json data. This action
        # will also store the json payload to the EventData directory completing the desired 
        # operation
        get_team_rankings_json( global_config, event+year, store_json_file=True )
        get_team_list_json( global_config, event+year, store_json_file=True )
       
        result = True
        
    return result

def update_team_data_files( global_config, year, event, directory, team=None ):
    
    global_config['logger'].debug( 'Updating Team DataFiles' )

    session = DbSession.open_db_session(global_config['db_name'] + year)
    comp = event+year

    result = False
    team_list = []
    if team == None or team == '':
        team_list = DataModel.getTeamsInNumericOrder(session, comp)
    else:
        team_list.append(team)
        
    # for now, we only support updating files in the TeamData directory, so only continue if that's the 
    # directory that was specified.
    if directory.upper() == 'TEAMDATA' or directory.upper() == 'EVENTDATA':
        for team_entry in team_list:
            
            # TODO: added a special test here to skip teams with a number greater than 10000. Some data
            # was erroneously entered with team numbers really high...
            if team_entry.team < 10000:
                get_team_info_json(global_config, comp, team_entry.team, store_json_file=True)
                get_team_score_json(global_config, team_entry.team, comp, store_json_file=True)
                get_team_score_breakdown_json(global_config, team_entry.team, comp, store_json_file=True)
                get_team_scouting_notes_json(global_config, comp, team_entry.team, store_json_file=True)           
                get_team_scouting_mediafiles_json(global_config, comp, str(team_entry.team), store_json_file=True)
                get_team_scouting_datafiles_json(global_config, comp, str(team_entry.team), store_json_file=True)
                get_team_scouting_data_summary_json(global_config, comp, team_entry.team, store_json_file=True)
        result = True
        
    return result
