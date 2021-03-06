'''
Created on Dec 19, 2011

@author: ksthilaire
'''


import os
import web
import sys
import traceback
import datetime
import subprocess
import json
import threading

import DbSession
import DataModel
import DebriefDataModel
import IssueTrackerDataModel
import UsersDataModel
import AttributeDefinitions

from shutil import copyfile
from optparse import OptionParser

import BluetoothSyncServer
#import BluetoothWebProxyServer
import ConfigUtils
import CompAlias
import FileSync
import ImageFileUtils
import Logger
import ProcessFiles
import TimerThread
import WebAdminPage
import WebTeamData
import WebUiGen
import WebSetConfig
import WebDeleteAttr
import WebModifyAttr
import WebLogin
import WebIssueTracker
import WebDebrief
import WebUsers
import WebEventData
import WebCommonUtils
import WebAttributeDefinitions


#render = web.template.render('templates/', base='layout', globals={'utils':WebCommonUtils})
render = web.template.render('templates/', base='bootstrap_layout', globals={'utils':WebCommonUtils})

urls = (
    '/login(.*)',           'Login',
    '/logout',              'Logout',
    '/accessdenied',        'AccessDenied',
    '/accountdisabled',     'AccountDisabled',
    '/home(.*)',            'HomePage',
    '/admin',               'AdminPage',    
    '/team/(.*)',           'TeamServer',
    '/score/(.*)',          'TeamScore',
    '/scorebreakdown/(.+)',      'TeamScoreBreakdown',
    '/rankchart(.*)',       'TeamRanking',
    '/rankings(.*)',        'TeamRankingJson',
    '/attrrankings/(.*)/(.*)',   'TeamAttributeRankings',
    '/rankingsarray',       'TeamRankingsArray',
    '/recalculaterankings/(.*)', 'RecalculateRankings',
    '/test',                'TeamAttributes',
    '/teamdata/(.*)',       'TeamDataFiles',
    '/ScoutingData/(.*)',   'TeamDataFile',
    '/notes/(.*)',          'TeamNotes',
    '/genui',               'GenUi',
    '/config',              'SetConfig',
    '/modifyattr',          'ModifyAttr',
    '/deleteattr',          'DeleteAttr',
    '/deleteattrfile',      'DeleteAttrFile',
    '/newissue',            'NewIssue',
    '/newissue/(.*)',       'NewPlatformIssue',
    '/issue/(.*)',          'Issue',
    '/issueupdate/(.*)',    'IssueUpdate',
    '/issuecomment/(.*)',   'IssueComment',
    '/debriefcomment/(.*)/(.*)', 'DebriefComment',
    '/deletecomment/(.*)/(.+)',  'DeleteComment',
    '/issues',              'IssuesHomePage',
    '/issues/(.*)',         'PlatformIssuesHomePage',
    '/debrief/(.*)/(.*)',   'DebriefPage',
    '/debriefs/(.*)',       'DebriefsHomePage',
    '/user/(.*)',           'User',
    '/userprofile',         'UserProfile',
    '/newuser',             'NewUser',
    '/deleteuser',          'DeleteUser',
    '/deleteuser/(.*)',     'DeleteSpecificUser',
    '/users',               'Users',
    '/loadusers',           'LoadUsers',
    '/taskgroup_email/(.*)','TaskGroupEmail',
    '/taskgroup/(.*)',      'TaskGroup',
    '/taskgroups',          'TaskGroups',
    '/events(.*)',          'Events',
    '/teams(.*)',           'Teams',
    '/event/(.*)',          'EventData',
    '/eventstandings/(.*)', 'EventStandings',
    '/eventresults/(.*)',   'EventResults',
    '/setweights',          'SetWeights',
    '/attrrank(.*)',        'AttrRankPage',
    '/allianceselect(.*)',  'AllianceSelectionPage',
    '/downloads',           'DownloadsPage',
    '/upload/',             'Upload',
    '/eventgallery/(.*)',   'EventGallery',
    '/teamattrrank(.*)',    'TeamAttributeRanking',

    '/scoutingapp',         'ScoutingAppPage',
    '/scoutingfiles(.*)',   'ScoutingDataPage',
    '/scoutingfile/(.*)',   'ScoutingFilePage',
    
    '/eventdata/(.*)',      'JsonEventFile',
    '/teamdata2/(.*)',      'JsonTeamFile',

    '/api/rankings(.*)',            'TeamRankingJson',
    '/api/picklist(.*)',            'TeamPicklistJson',
    '/api/updatepicklist(.*)',      'TeamUpdatePicklistJson',
    '/api/scoutingdata/(.*)',       'TeamDataFileJson',
    '/api/scorebreakdown/(.+)',     'TeamScoreBreakdownJson',
    '/api/teamdatasummary/(.+)',    'TeamScoutingDataSummaryJson',
    '/api/teamscore/(.+)',          'TeamScoreJson',
    '/api/teams/(.*)',              'TeamListJson',
    '/api/teaminfo/(.*)',           'TeamInfoJson',
    '/api/teamyears/(.*)',          'TeamYearsJson',
    '/api/teamdatafiles/(.+)',      'TeamDataFilesJson',
    '/api/teammediafiles/(.+)',     'TeamMediaFilesJson',
    '/api/teamnotes/(.+)',          'TeamDataNotesJson',
    '/api/teamattrrank/(.+)',       'TeamAttributeRankingsJson',
    '/api/eventinfo/(.*)',          'EventInfoJson',
    '/api/eventstandings/(.*)',     'EventStandingsJson',
    '/api/eventranklist/(.*)',      'EventRanklistJson',
    '/api/eventresults/(.+)',       'EventResultsJson',
    '/api/eventstats/(.+)',         'EventStatsJson',
    '/api/eventschedule/(.+)',      'EventScheduleJson',
    '/api/events',                  'EventsJson',
    '/api/district/rankings',       'DistrictRankingsJson',
    '/api/issue/(.*)',              'IssueJson',
    '/api/issues/(.*)',             'PlatformIssuesJson',
    '/api/debriefs/(.*)',           'DebriefsJson',
    '/api/users',                   'UsersJson',
    '/api/attrlist(.*)',            'AttributesJson',
    '/api/attrfilter/(.*)',         'AttributesFilter',
    '/api/geolocation',             'GeoLocationJson',
    '/api/teamparticipation',       'TeamParticipationJson',
    '/api/scoutingdatafiles/(.*)',  'ScoutingDataFilesJson',
    
    
    '/images/(.*)',                 'Images',
    
    '/testpage(.*)',                'TestPage',
        
    '/static/(.*)',                 'FileRequest',
    '/copyfile',                    'CopyFile',
    '/sync/(.*)',                   'Sync'
)


logger = Logger.init_logger('./config', 'logging.conf', 'scouting.webapp')

global_config = { 'my_team'            : '1073',
                  'my_district'        : 'District',
                  'my_website'         : 'www.usfirst.org',
                  'this_season'        : '2017',
                  'this_competition'   : 'Test', 
                  'other_competitions' : '', 
                  'google_sheets_intf' : 'Disabled',
                  'excel_sheets_intf'  : 'Disabled',
                  'db_name'            : 'scouting', 
                  'issues_db_name'     : 'issues',
                  'issues_db_master'   : 'No',
                  'debriefs_db_name'   : 'debriefs',
                  'users_db_name'      : 'users',
                  'attr_definitions'   : None,
                  'team_list'          : '',
                  #'event_code'         : '',
                  'issue_types'        : 'Robot,MobileBase',
                  'logger'             : logger,
                  'events'             : {}
                }

def read_config(config_dict, config_filename):
    if os.path.exists(config_filename):
        cfg_file = open(config_filename, 'r')
        for cfg_line in cfg_file:
            if cfg_line.startswith('#'):
                continue
            cfg_line = cfg_line.rstrip()
            if cfg_line.count('=') > 0:
                (attr,value) = cfg_line.split('=',1)
                config_dict[attr] = value
            else:
                # ignore lines that don't have an equal sign in them
                pass   
        cfg_file.close()

def write_config(config_dict, config_filename):
    cfg_file = open(config_filename, 'w+')
    for key, value in config_dict.iteritems():
        line = '%s=%s\n' % (key,value)
        cfg_file.write(line)
    cfg_file.close()

ConfigUtils.read_config(global_config, './config/ScoutingAppConfig.txt')
db_name = global_config['db_name'] + '.db'
    
webserver_app = web.application(urls, globals())

class Login(object):
    def GET(self, param_str):
        path_param = web.ctx.query
        path_segments = path_param.split('=')
        desired_path = '/home'
        if len(path_segments) > 1:
            if path_segments[0] == '?path':
                desired_path = path_segments[1]
        return WebLogin.auth_user(global_config,desired_path)
    
class Logout(object):
    def GET(self):
        return WebLogin.do_logout(global_config)

class AccessDenied(object):
    def GET(self):
        return 'Sorry, you are not authorized to access this page'
    
class AccountDisabled(object):
    def GET(self):
        return WebLogin.do_account_disabled(global_config)
    
class HomePage(object):

    def GET(self, param_str):
        username, access_level = WebLogin.check_access(global_config,10)
        season = global_config['this_season']
        competition = global_config['this_competition']
        params = param_str.split('/')
        numparams = len(params)
        if numparams > 1:
            if len(params[1]) > 0:
                season = params[1]
            if numparams > 2:
                if len(params[2]) > 0:
                    competition = params[2]
        return render.homePage()
    
    
class TestPage(object):

    def GET(self, param_str):
        username, access_level = WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        comp = 'GSR2013'
        attr = 'Teleop_Stacks'
        if numparams == 3:
            comp = params[1]
            attr = params[2]
        return render.attrRank(comp,attr)


class AttrRankPage(object):

    def GET(self, param_str):
        username, access_level = WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        competition = global_config['this_competition']
        season = global_config['this_season']
        numparams = len(params)
        if numparams > 1:
            if len(params[1]) > 0:
                season = params[1]
            if numparams > 2:
                if len(params[2]) > 0:
                    competition = params[2]
        return render.attrRank(season,competition)    
    

class AllianceSelectionPage(object):

    def GET(self, param_str):
        username, access_level = WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        competition = global_config['this_competition']
        season = global_config['this_season']
        numparams = len(params)
        if numparams > 1:
            if len(params[1]) > 0:
                season = params[1]
            if numparams > 2:
                if len(params[2]) > 0:
                    competition = params[2]
        return render.allianceSelection(season,competition)
    
class AdminPage(object):

    def GET(self):
        access_level = WebLogin.check_access(global_config,1)[1]
        result = WebAdminPage.get_page(global_config, access_level)
        if global_config.has_key('my_team'):
            team = global_config['my_team']
        else:
            team = '1073'
        return render.page('Team %s Administration' % team, result)
    
''' replaced with the tabbed page just below
class TeamDataFiles(object):

    def GET(self, name):
        user_info = WebLogin.check_access(global_config,10)
        access_level = user_info[1]
        display_notes = False
        if access_level < 10:
            display_notes = True
            
        result = WebTeamData.get_team_datafiles_page(global_config, name, display_notes)
        return render.page('Team %s Scouting Data Page' % name, result)
'''
                              
class TeamDataFiles(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        
        params = param_str.split('/')
        numparams = len(params)
        if numparams >= 2:
            comp = params[0]
            name = params[1]
        else:
            comp = global_config['this_competition'] + global_config['this_season']
            name = params[0]

        return render.teamDataTabbed(comp,name)
                           
class TeamInfoJson(object):

    def GET(self, param_str):
        user_info = WebLogin.check_access(global_config,10)

        params = param_str.split('/')
        numparams = len(params)
        if numparams >= 2:
            comp = params[0]
            name = params[1]
        else:
            comp = global_config['this_competition'] + global_config['this_season']
            name = params[0]
            
        web.header('Content-Type', 'application/json')

        result = WebTeamData.get_team_info_json(global_config, comp, name)
        return result
                           
    def POST(self, param_str):
        #user_info = WebLogin.check_access(global_config,10)

        params = param_str.split('/')
        numparams = len(params)
        name = None
        if numparams == 1:
            if params[0] != '':
                name = params[0]

        WebTeamData.load_team_info(global_config, name)
        
        #WebTeamData.set_team_geo_location(global_config, name)
        return 
                           
class TeamYearsJson(object):

    def POST(self, param_str):
        #user_info = WebLogin.check_access(global_config,10)

        params = param_str.split('/')
        numparams = len(params)
        name = None
        if numparams == 1:
            if params[0] != '':
                name = params[0]
        
        WebTeamData.load_team_participation_years(global_config, name)
        return 
                           
class TeamScoutingDataSummaryJson(object):

    def GET(self, param_str):
        user_info = WebLogin.check_access(global_config,10)
        
        params = param_str.split('/')
        numparams = len(params)
        result = None
        if numparams >= 2:
            comp = params[0]
            name = params[1]
            
            query_data = web.input(filter=None,queryname=None)
            if query_data.filter is None:
                if query_data.queryname is None:
                    filter_name = None
                    attr_filter = []
                else:
                    filter_name = query_data.queryname
                    attr_filter = WebAttributeDefinitions.get_saved_filter(filter_name)
            else:
                filter_name = 'Filter_%d' % hash(query_data.filter)
                attr_filter = query_data.filter.split()
            
            result = WebTeamData.get_team_scouting_data_summary_json(global_config,comp,name,attr_filter=attr_filter, filter_name=filter_name)
        return result

class TeamDataFilesJson(object):

    def GET(self, param_str):
        user_info = WebLogin.check_access(global_config,10)
        
        params = param_str.split('/')
        numparams = len(params)
        result = None
        if numparams >= 2:
            comp = params[0]
            name = params[1]
            result = WebTeamData.get_team_scouting_datafiles_json(global_config,comp,name)
        return result

class TeamMediaFilesJson(object):

    def GET(self, param_str):
        user_info = WebLogin.check_access(global_config,10)
        
        params = param_str.split('/')
        numparams = len(params)
        result = None
        if numparams >= 2:
            comp = params[0]
            name = params[1]
            result = WebTeamData.get_team_scouting_mediafiles_json(global_config,comp,name)
        return result

class TeamDataNotesJson(object):

    def GET(self, param_str):
        user_info = WebLogin.check_access(global_config,10)
        
        params = param_str.split('/')
        numparams = len(params)
        result = None
        if numparams >= 2:
            comp = params[0]
            name = params[1]
            
            access_level = user_info[1]
            # do not return notes for guest accounts, just in case the notes aren't very GP
            if access_level < 10:
                result = WebTeamData.get_team_scouting_notes_json(global_config,comp,name)
        return result
                               
class TeamServer(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        return WebTeamData.get_team_server_page(global_config, name)
        
class TeamScore(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        return WebTeamData.get_team_score_page(global_config, name)

class TeamScoreBreakdownJson(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        if numparams == 1:
            comp = global_config['this_competition'] + global_config['this_season']
            name = params[0]
        elif numparams >= 2:
            comp = params[0]
            name = params[1]
        else:
            return None
        
        web.header('Content-Type', 'application/json')

        return WebTeamData.get_team_score_breakdown_json(global_config, name, comp)

class TeamScoreJson(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        if numparams == 1:
            comp = global_config['this_competition'] + global_config['this_season']
            name = params[0]
        elif numparams >= 2:
            comp = params[0]
            name = params[1]
        else:
            return None

        web.header('Content-Type', 'application/json')
        return WebTeamData.get_team_score_json(global_config, name, comp)

class TeamListJson(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        if numparams == 0:
            comp = global_config['this_competition'] + global_config['this_season']
        else:
            comp = params[0].lower()
            
        event, season = WebCommonUtils.split_comp_str(comp)
            
        web.header('Content-Type', 'application/json')
        return WebTeamData.get_team_list_json(global_config, season, event)

        
class TeamScoreBreakdown(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        if numparams == 1:
            comp = global_config['this_competition'] + global_config['this_season']
        elif numparams >= 2:
            comp = params[0]
            name = params[1]
        else:
            return None
        return render.scorePieChart(comp, name)
    
class TeamNotes(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        return WebTeamData.get_team_notes_page(global_config, name)

class TeamRankingJson(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        if numparams < 2 or params[1] == '':
            comp = global_config['this_competition'] + global_config['this_season']
        else:
            comp = params[1]
        query_data = web.input(filter=None,queryname=None,thumbnails=None)
        if query_data.filter is None:
            if query_data.queryname is None:
                filter_name = None
                attr_filter = []
            else:
                filter_name = query_data.queryname
                attr_filter = WebAttributeDefinitions.get_saved_filter(filter_name)
        else:
            filter_name = 'Filter_%d' % hash(query_data.filter)
            attr_filter = query_data.filter.split()

        thumbnails = False
        if query_data.thumbnails is not None:
            if query_data.thumbnails == 'True' or query_data.thumbnails == 'Yes':
                thumbnails = True
                
        web.header('Content-Type', 'application/json')
        
        event, season = WebCommonUtils.split_comp_str(comp)
        
        return WebTeamData.get_team_rankings_json(global_config, season, event, attr_filter, filter_name, thumbnails)

class TeamPicklistJson(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        if numparams < 2 or params[1] == '':
            comp = global_config['this_competition'] + global_config['this_season']
        else:
            comp = params[1]
            
        web.header('Content-Type', 'application/json')
        return WebTeamData.create_picklist_json(global_config, comp, store_json_file=True)

    def POST(self, param_str):
        WebLogin.check_access(global_config,10)
        query_data = web.input()
        
        comp = global_config['this_competition'] + global_config['this_season']
            
        web.header('Content-Type', 'application/json')
        return WebTeamData.create_picklist_json(global_config, comp, store_json_file=True)


class TeamUpdatePicklistJson(object):

    def POST(self, param_str):
        WebLogin.check_access(global_config,10)
        query_data = web.input()
        
        comp = global_config['this_competition'] + global_config['this_season']
            
        web.header('Content-Type', 'application/json')
        return WebTeamData.update_picklist_json(global_config, int(query_data.fromPosition), int(query_data.toPosition), comp, store_json_file=True)

class TeamAttributeRanking(object):

    def GET(self, param_str):
        username, access_level = WebLogin.check_access(global_config,10)
        season = global_config['this_season']
        competition = global_config['this_competition']
        params = param_str.split('/')
        numparams = len(params)
        if numparams > 1:
            if len(params[1]) > 0:
                season = params[1]
            if numparams > 2:
                if len(params[2]) > 0:
                    competition = params[2]
        return render.attrRankPage2(season,competition)


class TeamAttributeRankingsJson(object):

    def GET(self, param_str):
        username, access_level = WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        attr_name = 'Unknown'

        if numparams == 1:
            comp = global_config['this_competition'] + global_config['this_season']
            attr_name = params[0]
        elif numparams >= 2:
            comp = params[0]
            attr_name = params[1]
        else:
            return None

        web.header('Content-Type', 'application/json')
        return WebTeamData.get_team_attr_rankings_json(global_config, comp, attr_name)
        
    
class TeamRanking(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        if numparams < 2 or params[1] == '':
            comp = global_config['this_competition'] + global_config['this_season']
        else:
            comp = params[1]
        return render.scoutingData(comp)
    
class TeamAttributeRankings(object):

    def GET(self, comp, name):
        WebLogin.check_access(global_config,10)
        return WebTeamData.get_team_attr_rankings_page(global_config,comp,name)

class TeamRankingsArray(object):

    def GET(self):
        WebLogin.check_access(global_config,10)
        return WebTeamData.get_team_rankings_array(global_config)

class TeamAttributes(object):

    def GET(self):
        WebLogin.check_access(global_config,10)
        return WebTeamData.get_team_attributes_page(global_config)
   
class TeamDataFile(object):

    def GET(self, filename):
        WebLogin.check_access(global_config,10)
        params = filename.split('/', 1)
        
        return render.dataFile(params[0], params[1])
        #result = WebTeamData.get_team_datafile_page(global_config, filename)
        #return render.page('Scouting Data File: %s' % filename.split('/', 1)[1], result)

class TeamDataFileJson(object):

    def GET(self, filename):
        WebLogin.check_access(global_config,10)
            
        web.header('Content-Type', 'application/json')
        result = WebTeamData.get_team_datafile_json(global_config, filename)
        return result

class RecalculateRankings(object):

    def GET(self, event_code):
        WebLogin.check_access(global_config,4)
        comp = WebCommonUtils.map_event_code_to_comp(event_code)
        DataModel.recalculate_scoring(global_config, comp)
        
        raise web.seeother('/event/%s' % event_code)

class DistrictRankingsJson(object):
    
    def GET(self):
        WebLogin.check_access(global_config,10)
        request_data = web.input()
        result = None
        
        try:
            season = request_data.Year
        except:
            season = global_config['this_season']
            
        try:
            event_type = request_data.Type
            event_type = 'NE'
            
            result = WebEventData.get_district_rankings_json(global_config, season, event_type)
        except:
            event_type = None

        web.header('Content-Type', 'application/json')
        return result
        
class Events(object):

    def GET(self, param_str):
        username, access_level = WebLogin.check_access(global_config,10)
        season = global_config['this_season']
        competition = global_config['this_competition']
        params = param_str.split('/')
        numparams = len(params)
        if numparams > 1:
            if len(params[1]) > 0:
                season = params[1]
            if numparams > 2:
                if len(params[2]) > 0:
                    competition = params[2]
        return render.eventsPage(season,competition)

class Teams(object):

    def GET(self, param_str):
        username, access_level = WebLogin.check_access(global_config,10)
        season = global_config['this_season']
        competition = global_config['this_competition']
        params = param_str.split('/')
        numparams = len(params)
        if numparams > 1:
            if len(params[1]) > 0:
                season = params[1]
            if numparams > 2:
                if len(params[2]) > 0:
                    competition = params[2]
        return render.teamsPage(season,competition)

                           
class EventsJson(object):

    def GET(self):
        WebLogin.check_access(global_config,10)
        request_data = web.input()
        
        try:
            season = request_data.Year
        except:
            season = global_config['this_season']
            
        try:
            event_type = request_data.Type
            event_type = 'NE'
        except:
            event_type = None
            
        if event_type != None:
            result = WebEventData.get_district_events_json(global_config, season, event_type)
        else:
            result = WebEventData.get_events_json(global_config, season, event_type)
            
        web.header('Content-Type', 'application/json')
        return result
                           
class EventData(object):

    def GET(self, event_code):
        user_info = WebLogin.check_access(global_config,10)
        return render.eventData(event_code)
                           
class EventGallery(object):

    def GET(self, event_code):
        user_info = WebLogin.check_access(global_config,10)
        return render.eventGallery(event_code)
                           
class EventStandings(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        year = name[0:4]
        event_code = name[4:]
        result = WebEventData.get_event_standings_page(global_config, year, event_code)
        return render.page('FIRST Robotics Standings Details - %s' % event_code.upper(), result)
                  
class EventInfoJson(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        year = name[0:4]
        event_code = name[4:]
        result = WebEventData.get_event_info_json(global_config, year, event_code)
            
        web.header('Content-Type', 'application/json')
        return result
    
    def POST(self, name):
        WebEventData.load_event_info(global_config, name)
        
        #WebEventData.get_event_geo_location(global_config)
        return
                  
class EventStandingsJson(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        year = name[0:4]
        event_code = name[4:]
        result = WebEventData.get_event_standings_json(global_config, year, event_code)
            
        web.header('Content-Type', 'application/json')
        return result
    
    def POST(self, name):
        return
        
                  
class EventResultsJson(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        result = ''
        params = param_str.split('/')
        if len(params) >= 2:
            year = params[0][0:4]
            event_code = params[0][4:]
            round_str = params[1]
            if len(params)==3:
                team_str = params[2]
            else:
                team_str = None
            result = WebEventData.get_event_matchresults_json(global_config, year, event_code, round_str, team_str)
            
            web.header('Content-Type', 'application/json')
            
        return result

class EventScheduleJson(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        result = ''
        params = param_str.split('/')
        if len(params) >= 1:
            year = params[0][0:4]
            event_code = params[0][4:]
            if len(params)==2:
                team_str = params[1]
            else:
                team_str = None
            result = WebEventData.get_event_matchschedule_json(global_config, year, event_code, team_str)
                        
            web.header('Content-Type', 'application/json')
            
        return result
                           
class EventRanklistJson(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        year = name[0:4]
        event_code = name[4:]
        result = WebEventData.get_event_rank_list_json(global_config, year, event_code)
            
        web.header('Content-Type', 'application/json')
        return result
    
    def POST(self, name):
        return
        
class EventStatsJson(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        result = ''
        params = param_str.split('/')
        if len(params) == 2:
            year = params[0][0:4]
            event_code = params[0][4:]
            stat_type = params[1]
            result = WebEventData.get_event_stats_json(global_config, year, event_code, stat_type)
            
            web.header('Content-Type', 'application/json')
            
        return result
                           
class EventResults(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        year = name[0:4]
        event_code = name[4:]
        result = WebEventData.get_event_results_page(global_config, year, event_code)
        return render.page('FIRST Robotics Event Match Results - %s' % event_code.upper(), result)                           

class GeoLocationJson(object):
    def GET(self):
        #WebLogin.check_access(global_config,10)
                        
        query_data = web.input()
        
        try:
            if query_data.teams == 'Yes':
                include_teams = True
            else:
                include_teams = False
        except:
            include_teams = False
            
        try:
            if query_data.events == 'Yes':
                include_events = True
            else:
                include_events = False
        except:
            include_events = False
        
        return WebCommonUtils.get_geo_location_json(include_teams,include_events)

class TeamParticipationJson(object):
    def GET(self):
        #WebLogin.check_access(global_config,10)
                                
        return WebCommonUtils.get_team_participation_json()

class AttributesJson(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        param_str = param_str.lstrip('/')
        params = []
        
        if param_str != '':
            params = param_str.split('/')
        
        if len(params) >= 1:
            filter_name = params[0]
        else:
            filter_name = None  

        web.header('Content-Type', 'application/json')

        result = WebAttributeDefinitions.get_attr_tree_json(global_config, filter_name)
        
        return result

class AttributesFilter(object):   
     
    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        params = []
        
        if param_str != '':
            params = param_str.split('/')
        
        if len(params) >= 1:
            filter_name = params[0]
        else:
            filter_name = None  
              
        web.header('Content-Type', 'application/json')
        return WebAttributeDefinitions.get_saved_filter_json(global_config, filter_name)
        
    def POST(self, param_str):
        WebLogin.check_access(global_config,10)
        params = param_str.split('/')
                
        query_data = web.input()
        
        if len(params) >= 1:
            filter_name = params[0]
            
            WebAttributeDefinitions.save_filter(filter_name, query_data.filter)
        else:
            raise web.BadRequest
        
        return                 

    def DELETE(self, param_str):
        WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        
        if len(params) >= 1:
            filter_name = params[0]
            
            WebAttributeDefinitions.delete_filter(filter_name)
        else:
            raise web.BadRequest
        
        return                 

                  
class DownloadsPage(object):

    def GET(self):
        user_info = WebLogin.check_access(global_config,10)
        return render.downloadPage('/static/downloads')
                           
class ScoutingAppPage(object):

    def GET(self):
        user_info = WebLogin.check_access(global_config,10)
        return render.scoutingAppMain('Match')
                           
class GenUi(object):
    
    def GET(self):
        WebLogin.check_access(global_config,0)
        form = WebUiGen.get_form(global_config)
        return render.default_form(form)
   
    def POST(self):
        WebLogin.check_access(global_config,0)
        form = WebUiGen.get_form(global_config)
        if not form.validates(): 
            return render.default_form(form)
        else:
            return WebUiGen.process_form(global_config, form)
   
class SetConfig(object):
    def GET(self):
        WebLogin.check_access(global_config,0)        
        form = WebSetConfig.get_form(global_config)
        return render.default_form(form)

    def POST(self):
        WebLogin.check_access(global_config,0)
        form = WebSetConfig.get_form(global_config)
        if not form.validates(): 
            return render.cfg_form_done(form)
        else:
            WebSetConfig.process_form(global_config, form)
            return render.cfg_form_done(form)

class ModifyAttr(object):
    def GET(self):
        WebLogin.check_access(global_config,7)        
        form = WebModifyAttr.get_form(global_config)
        return render.default_form(form)

    def POST(self):
        WebLogin.check_access(global_config,7)
        form = WebModifyAttr.get_form(global_config)
        if not form.validates(): 
            return render.default_form(form)
        else:
            result = WebModifyAttr.process_form(global_config, form)
            return render.default_form_with_msg(form, result)

class DeleteAttr(object):
    def GET(self):
        WebLogin.check_access(global_config,7)        
        form = WebDeleteAttr.get_delete_attr_form(global_config)
        return render.default_form(form)

    def POST(self):
        WebLogin.check_access(global_config,7)
        form = WebDeleteAttr.get_delete_attr_form(global_config)
        if not form.validates(): 
            return render.default_form(form)
        else:
            result = WebDeleteAttr.process_delete_attr_form(global_config, form)
            return render.default_form_with_msg(form, result)

class DeleteAttrFile(object):
    def GET(self):
        WebLogin.check_access(global_config,7)        
        form = WebDeleteAttr.get_delete_file_form(global_config)
        return render.default_form(form)

    def POST(self):
        WebLogin.check_access(global_config,7)
        form = WebDeleteAttr.get_delete_file_form(global_config)
        if not form.validates(): 
            return render.default_form(form)
        else:
            result = WebDeleteAttr.process_delete_file_form(global_config, form)
            return render.default_form_with_msg(form, result)

class NewIssue(object):
    def GET(self):
        WebLogin.check_access(global_config,2)
        form = WebIssueTracker.get_new_issue_form(global_config)
        return render.default_form(form)
           
    def POST(self):
        WebLogin.check_access(global_config,2)
        form = WebIssueTracker.get_new_issue_form(global_config)
        if not form.validates(): 
            return render.new_issue_form_done(form)
        else:
            result = WebIssueTracker.process_new_issue_form(global_config, form)
            raise web.seeother(result)

class NewPlatformIssue(object):
    def GET(self, platform_type):
        WebLogin.check_access(global_config,2)
        form = WebIssueTracker.get_new_issue_form(global_config, platform_type)
        return render.default_form(form)
           
    def POST(self, platform_type):
        WebLogin.check_access(global_config,2)
        form = WebIssueTracker.get_new_issue_form(global_config, platform_type)
        if not form.validates(): 
            return render.new_issue_form_done(form)
        else:
            result = WebIssueTracker.process_new_issue_form(global_config, form)
            raise web.seeother(result)

class IssueComment(object):
    def GET(self, issue_id):
        WebLogin.check_access(global_config,5)
        form = WebIssueTracker.get_issue_comment_form(global_config, issue_id)
        return render.issue_comment_form(form, issue_id)
           
    def POST(self, issue_id):
        username, access_level = WebLogin.check_access(global_config,5)
        form = WebIssueTracker.get_issue_comment_form(global_config, issue_id)
        if not form.validates(): 
            return render.issue_comment_form_done(form)
        else:
            result = WebIssueTracker.process_issue_comment_form(global_config, form, issue_id, username)
            raise web.seeother(result)
        
               
class IssueUpdate(object):
    
    def GET(self, issue_id):
        WebLogin.check_access(global_config,2)
        form = WebIssueTracker.get_issue_form(global_config, issue_id)
        return render.default_form(form)

    def POST(self, issue_id):
        username, access_level = WebLogin.check_access(global_config,2)
        form = WebIssueTracker.get_issue_form(global_config, issue_id)
        if not form.validates(): 
            return render.issue_form_done(form)
        else:
            result = WebIssueTracker.process_issue_form(global_config, form, issue_id, username)
            raise web.seeother(result)
        
class Issue(object):
    
    def GET(self, issue_id):
        username, access_level = WebLogin.check_access(global_config,5)
        if access_level <=1:
            result = WebIssueTracker.get_issue_page(global_config, issue_id, allow_update=True)
        else:
            result = WebIssueTracker.get_issue_page(global_config, issue_id)
        if result:
            return render.page( 'Issue: %s' % issue_id, result)
        else:
            return render.page( 'Issue: %s Not Found' % issue_id, result)
        
class IssueJson(object):
    
    def GET(self, issue_id):           
        web.header('Content-Type', 'application/json')
        return WebIssueTracker.get_issue_json(global_config, issue_id)
        
class DeleteComment(object):
    
    def GET(self, param_str):
        username, access_level = WebLogin.check_access(global_config,1)
        params = param_str.split('/')
        if params[0] == 'issue':
            result = WebIssueTracker.delete_comment(global_config,params[1], params[2])
        elif params[0] == 'debrief':
            result = WebDebrief.delete_comment(global_config,params[1], params[2], params[3])
        else:
            return "404 Not Found"

        raise web.seeother(result)
 
        
class IssuesHomePage(object):

    def GET(self):
        username, access_level = WebLogin.check_access(global_config,5)
        if access_level <= 1:
            result = WebIssueTracker.get_issues_home_page(global_config,allow_create=True)
        else:
            result = WebIssueTracker.get_issues_home_page(global_config)
            
        return render.page('Team 1073 Issues Home Page', result)

class PlatformIssuesHomePage(object):

    def GET(self, platform_type):
        username, access_level = WebLogin.check_access(global_config,5)
        allow_create = False
        if access_level <= 1:
            if global_config['issues_db_master'] == 'Yes':
                allow_create = True
        return render.issueTracker(platform_type,allow_create)

class PlatformIssuesJson(object):

    def GET(self, param_str):
        username, access_level = WebLogin.check_access(global_config,5)
        params = param_str.split('/')
        numparams = len(params)
        platform_type = params[0]
        if numparams > 1:
            status = params[1]
        else:
            status = ''     
            
        web.header('Content-Type', 'application/json')
        return WebIssueTracker.get_platform_issues(global_config, platform_type, status)

class Users(object):
    def GET(self):
        WebLogin.check_access(global_config,1)
        #result = WebUsers.get_user_list_page(global_config)
        #return render.page('User Administration', result)
        return render.users()
    
class UsersJson(object):
    def GET(self):
        WebLogin.check_access(global_config,1)
            
        web.header('Content-Type', 'application/json')
        return WebUsers.get_user_list_json(global_config)
    
class LoadUsers(object):
    
    def GET(self):
        WebLogin.check_access(global_config,1)
        form = WebUsers.get_load_user_form(global_config)
        return render.default_form(form)

    def POST(self):
        WebLogin.check_access(global_config,1)
        form = WebUsers.get_load_user_form(global_config)
        if not form.validates(): 
            return render.user_form_done(form)
        else:
            try:
                result = WebUsers.process_load_user_form(global_config, form)
                raise web.seeother(result)

            except Exception, e:
                return str(e)

class User(object):
    
    def GET(self, username):
        WebLogin.check_access(global_config,1)
        form = WebUsers.get_user_form(global_config, username)
        return render.default_form(form)

    def POST(self, username):
        my_username, my_access_level = WebLogin.check_access(global_config,1)
        form = WebUsers.get_user_form(global_config, username)
        if not form.validates(): 
            return render.user_form_done(form)
        else:
            try:
                result = WebUsers.process_user_form(global_config, form, username, my_access_level)
                raise web.seeother(result)

            except Exception, e:
                return str(e)

class DeleteUser(object):
    
    def GET(self):
        WebLogin.check_access(global_config,1)
        form = WebUsers.get_delete_user_form(global_config)
        return render.default_form(form)

    def POST(self):
        WebLogin.check_access(global_config,1)
        form = WebUsers.get_delete_user_form(global_config)
        if not form.validates(): 
            return render.user_form_done(form)
        else:
            try:
                result = WebUsers.process_delete_user_form(global_config, form)
                raise web.seeother(result)

            except Exception, e:
                return str(e)

class DeleteSpecificUser(object):

    def POST(self, username):
        WebLogin.check_access(global_config,1)

        try:
            WebUsers.process_delete_user(global_config, username)
            return
            #result = WebUsers.process_delete_user(global_config, username)
            #raise web.seeother(result)

        except Exception, e:
            return str(e)
        

class NewUser(object):
    
    def GET(self):
        WebLogin.check_access(global_config,1)
        form = WebUsers.get_user_form(global_config, '')
        return render.default_form(form)

    def POST(self):
        my_username, my_access_level = WebLogin.check_access(global_config,1)
        form = WebUsers.get_user_form(global_config, '')
        if not form.validates(): 
            return render.user_form_done(form)
        else:
            try:
                result = WebUsers.process_user_form(global_config, form, '', my_access_level, new_user=True)
                raise web.seeother(result)

            except Exception, e:
                return str(e)

class UserProfile(object):
    
    def GET(self):
        username,access_level = WebLogin.check_access(global_config,9)
        form = WebUsers.get_userprofile_form(global_config, username)
        return render.default_form(form)

    def POST(self):
        username, access_level = WebLogin.check_access(global_config,9)
        form = WebUsers.get_userprofile_form(global_config, username)
        if not form.validates(): 
            return render.user_form_done(form)
        else:
            try:
                result = WebUsers.process_userprofile_form(global_config, form, username)
                raise web.seeother(result)

            except Exception, e:
                return str(e)

class DebriefsHomePage(object):

    def GET(self,competition):
        WebLogin.check_access(global_config,9)
        return render.debriefsMain(competition)

class DebriefsJson(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,5)
        params = param_str.split('/')
        numparams = len(params)
        if numparams == 0:
            comp = global_config['this_competition'] + global_config['this_season']
        else:
            competition = params[0]
            
        web.header('Content-Type', 'application/json')
        return WebDebrief.get_competition_debriefs(global_config, competition)

class DebriefPage(object):

    def GET(self, comp, match):
        username, access_level = WebLogin.check_access(global_config,9)
        if access_level <=1:
            result = WebDebrief.get_debrief_page(global_config, comp, match, allow_update=True)
        else:
            result = WebDebrief.get_debrief_page(global_config, comp, match)
        return render.page('Team 1073 Debrief For Match %s:%s' % (comp,match), result)

class DebriefComment(object):
    def GET(self, comp, match):
        WebLogin.check_access(global_config,9)
        form = WebDebrief.get_match_comment_form(global_config, comp, match)
        return render.debrief_comment_form(form, comp, match)
           
    def POST(self, comp, match):
        username,access_level = WebLogin.check_access(global_config,9)
        form = WebDebrief.get_match_comment_form(global_config, comp, match)
        if not form.validates(): 
            return render.issue_comment_form_done(form)
        else:
            result = WebDebrief.process_match_comment_form(global_config, form, comp, match, username)
            raise web.seeother(result)
        
class TaskGroupEmail(object):
    def GET(self, name):
        email_lists = UsersDataModel.getTaskgroupEmailLists(global_config, name)
        taskgroups_filename = './static/data/ScoutingConfig/TaskGroupEmailLists.txt'
        fd = open(taskgroups_filename, 'w+')
        fd.write( email_lists )
        fd.close()
        return email_lists
    
class TaskGroup(object):
    def GET(self, name):   
        raise web.notfound('Taskgroup Management Not Yet Available')
    
class TaskGroups(object):
    def GET(self):     
        raise web.notfound('Taskgroup Management Not Yet Available')

class FileRequest(object):
    def GET(self, request_path):
        request_path = request_path.lstrip('/')
        query_str = web.input(checksum=None)

        with_checksum = False
        if query_str.checksum is not None:
            with_checksum = True

        response_body = FileSync.get(global_config, request_path, with_checksum=with_checksum)

        return response_body
        
    def PUT(self, request_path):
        request_path = request_path.lstrip('/')
        content_type = web.ctx.env['CONTENT_TYPE']
        FileSync.put(global_config, request_path, content_type, web.data())
        return

    def DELETE(self, request_path):
        request_path = request_path.lstrip('/')
        FileSync.delete(global_config, request_path)
        return

class Sync(object):
    def OPTIONS(self, request_path):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', 'PUT, POST, GET, DELETE' )
        web.header('Access-Control-Allow-Headers', 'Content-Type')
        web.header('Access-Control-Allow-Credentials', 'true')
        return {'message': 'GET OK!'}        
        
    def GET(self, request_path):
        request_path = request_path.lstrip('/')
        query_str = web.input(checksum=None, recurse=None)

        with_checksum = False
        if query_str.checksum is not None:
            with_checksum = True
    
        recurse = False
        if query_str.recurse is not None:
            recurse = True

        response_body = FileSync.get(global_config, request_path, recurse=recurse, with_checksum=with_checksum)

        return response_body
        
    def PUT(self, request_path):
        
        request_path = request_path.lstrip('/')
        content_type = web.ctx.env['CONTENT_TYPE']
        FileSync.put(global_config, request_path, content_type, web.data())
        return

    def DELETE(self, request_path):
        request_path = request_path.lstrip('/')
        query_str = web.input(delete_data=None)
        if query_str.delete_data is not None:
            ProcessFiles.remove_json_file_data(global_config, request_path)

        FileSync.delete(global_config, request_path)
        return

    def POST(self, request_path):
        request_path = request_path.lstrip('/')
        result = False
        path_elems = request_path.split('/')
        if len(path_elems) >= 2:
            comp_season_list = WebCommonUtils.split_comp_str(path_elems[0])
            if comp_season_list != None:
                # for the sync of event and team data, the URI path is of the following
                # format /Sync/<comp>/EventData/[TeamData/]. if just EventData is provided,
                # then the event data is regenerated, if TeamData is provided, then both
                # the event data and team data is regenerated
                if len(path_elems) >= 2 and path_elems[1] == 'EventData':
                    result = WebEventData.update_event_data_files( global_config,  
                                                                   comp_season_list[1], 
                                                                   comp_season_list[0], 
                                                                   path_elems[1] )
                    if result == True:
                        result = WebTeamData.update_team_event_files( global_config,  
                                                                   comp_season_list[1], 
                                                                   comp_season_list[0], 
                                                                   path_elems[1] )
                    result = WebAttributeDefinitions.update_event_data_files( global_config,  
                                                                   path_elems[1] )
                    
                    # if we hit an error generating the event files, then there is no 
                    # sense going on from here
                    if result == False:
                        raise web.BadRequest
                                        
                if len(path_elems) >= 3 and path_elems[2] == 'TeamData':
                    try:
                        team = path_elems[3]
                        if team == '':
                            team = None
                    except:
                        team = None
                        
                    result = WebTeamData.update_team_data_files( global_config,  
                                                                 comp_season_list[1], 
                                                                 comp_season_list[0], 
                                                                 path_elems[2], team )
                
        if result == False:
            raise web.BadRequest
        
        return

class CopyFile(object):
    
    def POST(self):   
        copy_params = json.loads(web.data())        
        copyfile( copy_params['source'], copy_params['dest'] )
        
        return
    
class JsonEventFile(object):
    
    def GET(self, request_path):
        request_path = request_path.lstrip('/')
        query_str = web.input(season=global_config['this_season'],event=global_config['this_competition'])
        file_path = query_str.event + query_str.season +  '/EventData/' + request_path + '.json'
        response_body = FileSync.get(global_config, file_path)
            
        web.header('Content-Type', 'application/json')
        return response_body
    
    def POST(self, request_path):    
        request_path = request_path.lstrip('/')
        query_str = web.input(season=global_config['this_season'],event=global_config['this_competition'])
        file_path = query_str.event + query_str.season + '/EventData/' + request_path + '.json'
        response_body = FileSync.get(global_config, file_path)
        #TODO: add update of the picklist based on the posted change...
        return
            
    
class JsonTeamFile(object):
    
    def GET(self, request_path):
        request_path = request_path.lstrip('/')
        query_str = web.input(season=global_config['this_season'],event=global_config['this_competition'])
        file_path = query_str.event + query_str.season +  '/TeamData/' + request_path + '.json'
        response_body = FileSync.get(global_config, file_path)
            
        web.header('Content-Type', 'application/json')
        return response_body    
    
class SetWeights(object):
    def GET(self):
        WebLogin.check_access(global_config,10)
        form = WebAttributeDefinitions.get_attr_def_form(global_config)
        return render.default_form(form)
           
    def POST(self):
        WebLogin.check_access(global_config,7)
        form = WebAttributeDefinitions.get_attr_def_form(global_config)
        if not form.validates(): 
            return render.default_form(form)
        else:
            result = WebAttributeDefinitions.process_attr_def_form(global_config, form)
            raise web.seeother(result)

class Upload(object):
    def GET(self):
        return
    
    def POST(self):
        x = web.input(files={})
        
        if 'files' in x: 
            filename="./static/uploadedfiles/" + x.files.filename
            fout = open( filename,'wb+') 
            fout.write(x.files.file.read())
            fout.close()
            ImageFileUtils.create_thumbnails_from_image(filename)

            web.header('Content-Type', 'application/json')
            result = []

            result.append('{ "files" : [\n')
            result.append('{\n')
            
            result.append('"name": "%s"' % x.files.filename)
            result.append(',\n')
            result.append('"url": "/static/uploadedfiles/%s"' % x.files.filename)
            result.append(',\n')
            result.append('"thumbnail": "/static/uploadedfiles/%s"' % x.files.filename)
            result.append(',\n')
            result.append('"type": "%s"' % x.files.type)
            result.append(',\n')
            result.append('"size": %d' % os.path.getsize(filename))
            
            result.append('}\n')
            
            result.append(' ] }\n')
    
            return ''.join(result) 
        else:
            return "No file uploaded"
        
class Images(object):
    def GET(self, image):
        ext = image.split(".")[-1] # Gather extension
        cType = {
            "png":"image/png",
            "jpg":"image/jpeg",
            "gif":"image/gif",
            "ico":"image/x-icon"}
        try:
            web.header("Content-Type", cType[ext]) # Set the Header
            return open('images/%s'%image,"rb").read() # Notice 'rb' for reading images
        except ValueError:
            return image + ' does not exists!'

#
# HERE
#
        
class ScoutingDataPage(object):

    def GET(self, param_str):
        user_info = WebLogin.check_access(global_config,10)
        season = global_config['this_season']
        competition = global_config['this_competition']
        params = param_str.split('/')
        numparams = len(params)
        if numparams > 1:
            if len(params[1]) > 0:
                season = params[1]
            if numparams > 2:
                if len(params[2]) > 0:
                    competition = params[2]

        return render.scoutingDataFiles(season,competition)
    
class ScoutingFilePage(object):

    def GET(self, param_str):
        user_info = WebLogin.check_access(global_config,10)

        return render.scoutingDataFile('/'+ param_str)
                           

class ScoutingDataFilesJson(object):

    def GET(self, param_str):
        user_info = WebLogin.check_access(global_config,10)
        
        web.header('Content-Type', 'application/json')
        
        file_path = 'static/data/%s/ScoutingData' % param_str
        scouting_files_dict = {}
        scouting_files_dict['pending'] = FileSync.get_file_list(file_path, ext='.json', recurse=True)
        scouting_files_dict['verified'] = FileSync.get_file_list(file_path, ext='.verified', recurse=True)
        scouting_files_dict['processed'] = FileSync.get_file_list(file_path, ext='.processed', recurse=True)
        scouting_files_json = json.dumps(scouting_files_dict)
        
        return scouting_files_json

    
     
'''    
class UsersUpdate(object):
    def GET(self):
            
    def POST(self):
'''
command_running_lock = threading.Lock()

command_running = False   
def process_files_timer_callback(cmd):
    '''
    global command_running
    # check to see if there is already a file process invocation underway. If so, 
    # then do not start another one and just return.
    print 'Checking command_running flag - %d' % int(command_running)
    if command_running == False:
        command_running = True
        # launch the file process command using the subprocess call function. This
        # method will not return until the called command itself returns.
        process_file_subprocess = subprocess.call(['python', cmd])
        print 'Subprocess returned - %s' % str(process_file_subprocess)
        command_running = False
        print 'Resetting command_running flag - %d' % int(command_running)
    else:
        print 'Process files command already running'
    '''
    
    global command_running_lock
    if not command_running_lock.acquire(False):
        print 'Process files command already running'
    else:
        try:

            # launch the file process command using the subprocess call function. This
            # method will not return until the called command itself returns.
            process_file_subprocess = subprocess.call(['python', cmd])
            print 'Subprocess returned - %s' % str(process_file_subprocess)
        except:
            traceback.print_exc()
            
        command_running_lock.release()
    return
    
    
if __name__ == "__main__":

    # command line options handling
    parser = OptionParser()
    
    parser.add_option(
        "-t","--test",action="store_true",dest="test",default=False,
        help="Processed test toggle")
    parser.add_option(    
        "-u","--users",dest="users_file",default='',
        help="List of Users to use for issue tracking")
    parser.add_option(
        "-l","--processloop",dest="processloop", default='0',
        help='Process Team Files')
    parser.add_option(    
        "-a","--aliases",dest="comp_alias_file",default='ScoutingAppEventAliases.txt',
        help="Competition Alias Configuration File")
    parser.add_option(
        "-b","--bluetooth",action="store_true", dest="bluetoothServer", default=False,
        help='Run Bluetooth Sync Server')
    parser.add_option(
        "-w","--bluetoothweb",action="store_true", dest="bluetoothWebServer", default=False,
        help='Run Bluetooth Web Server')
   
    # Parse the command line arguments
    (options,args) = parser.parse_args()

    logger.debug("Running the Scouting App Web Server")

    season = global_config['this_season']
    db_name          = global_config['db_name'] + season
    issues_db_name   = global_config['issues_db_name'] + season
    debriefs_db_name = global_config['debriefs_db_name'] + season
    users_db_name    = global_config['users_db_name'] + season
    

    session          = DbSession.open_db_session(db_name, DataModel)
    issues_session   = DbSession.open_db_session(issues_db_name, IssueTrackerDataModel)
    debrief_session  = DbSession.open_db_session(debriefs_db_name, DebriefDataModel)
    
    users_session    = DbSession.open_db_session(users_db_name, UsersDataModel)
 
    # Initialize the issue tracker
    WebIssueTracker.init_issue_tracker()
    
    # we need a temporary directory, so make sure that it exists
    tmp_dir = './tmp'
    try: 
        os.makedirs(tmp_dir)
    except OSError:
        if not os.path.isdir(tmp_dir):
            raise
    
    # load the users file if one is specified
    if options.users_file != '':
        users_file = './config/' + options.users_file
        
        if not users_file.endswith('.xlsx'):
            users_file += '.xlsx'
        logger.debug('Loading Users from file: %s' % users_file)
        UsersDataModel.add_users_from_file(users_session, users_file)

    # load the competition alias file if one is specified
    if options.comp_alias_file != '':
        comp_alias_file = './config/' + options.comp_alias_file        
        logger.debug('Loading Competition Alias file: %s' % comp_alias_file)
        CompAlias.read_comp_alias_config(comp_alias_file)

    # make sure that there is a default admin user. If no admin user exists, then create one
    if UsersDataModel.getUser( users_session, 'admin' ) is None:
        UsersDataModel.create_admin_user(users_session, 'squirrel!')

    session.close()
    issues_session.close()
    debrief_session.close()
    users_session.close()
    

    # Build the attribute definition dictionary from the definitions spreadsheet file
    attrdef_filename = WebCommonUtils.get_attrdef_filename( short_comp=global_config['this_competition'] )
    if attrdef_filename is not None:
        attr_definitions = AttributeDefinitions.AttrDefinitions(global_config)
        attr_definitions.parse(attrdef_filename)
        WebAttributeDefinitions.init_attr_def_forms(attr_definitions)


    # make sure that the required directories exist
    directories = ('ScoutingData', 'ScoutingPictures')
    competition = global_config['this_competition'] + global_config['this_season']        
    for directory in directories:
        base_dir = './static/data/' + competition + '/' + directory + '/'
        try: 
            os.makedirs(base_dir)
        except OSError:
            if not os.path.isdir(base_dir):
                raise
    
    #ImageFileUtils.create_thumbnails_by_directory('./static/data/%s/ScoutingPictures' % competition)

    # also create the configuration directory used to provide data to the tablets
    base_dir = './static/data/ScoutingConfig'
    try: 
        os.makedirs(base_dir)
    except OSError:
        if not os.path.isdir(base_dir):
            raise


    print 'Sys Args: %s' % sys.argv
    arg0 = sys.argv[0]
    sys.argv[1:] = args
    
    process_file_timer = None
    if int(options.processloop) > 0:
        # build the command to launch when the process files callback function is invoked
        launch_cmd = arg0.replace('ScoutingAppMainWebServer', 'ProcessFiles')
        process_file_timer = TimerThread.RepeatedTimer(int(options.processloop), process_files_timer_callback, launch_cmd)
    
    bluetooth_sync_server = None
    if options.bluetoothServer:
        bluetooth_sync_server = BluetoothSyncServer.BluetoothSyncServer(global_config)
        bluetooth_sync_server.start()

    '''
    bluetooth_web_server = None
    if options.bluetoothWebServer:
        if len(sys.argv) == 2:
            web_server_port = int(sys.argv[1])
        else :
            web_server_port = 8080
        bluetooth_web_server = BluetoothWebProxyServer.BluetoothWebProxyServer( web_server_port )
        bluetooth_web_server.start()
    '''

    try:
        webserver_app.run()

    except Exception, e:
        global_config['logger'].debug('Exception Caught Processing Request: %s' % str(e) )
        traceback.print_exc(file=sys.stdout)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        exception_info = traceback.format_exception(exc_type, exc_value,exc_traceback)
        for line in exception_info:
            line = line.replace('\n','')
            global_config['logger'].debug(line)

        print 'Program terminated, press <CTRL-C> to exit'
        data = sys.stdin.readlines()
        
    if bluetooth_sync_server != None:
        bluetooth_sync_server.terminate()
        bluetooth_sync_server.join()

    '''
    if bluetooth_web_server != None:
        bluetooth_web_server.terminate()
        bluetooth_web_server.join()
    '''
        
    if process_file_timer != None:
        process_file_timer.stop()

