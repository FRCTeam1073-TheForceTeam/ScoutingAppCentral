'''
Created on Dec 19, 2011

@author: ksthilaire
'''


import os
import web
import sys
import traceback
import datetime

import DbSession
import DataModel
import DebriefDataModel
import IssueTrackerDataModel
import UsersDataModel
import AttributeDefinitions

from optparse import OptionParser

import BluetoothSyncServer
import FileSync
import DataModel
import Logger
import ProcessFiles
import TimerThread
import WebHomePage
import WebAdminPage
import WebTeamData
import WebGenExtJsStoreFiles
import WebUiGen
import WebSetConfig
import WebLogin
import WebIssueTracker
import WebDebrief
import WebUsers
import WebEventData
import WebCommonUtils
import WebAttributeDefinitions


render = web.template.render('templates/', base='layout', globals={'utils':WebCommonUtils})

urls = (
    '/login',               'Login',
    '/logout',              'Logout',
    '/accessdenied',        'AccessDenied',
    '/accountdisabled',     'AccountDisabled',
    '/home',                'HomePage',
    '/admin',               'AdminPage',    
    '/team/(.*)',           'TeamServer',
    '/score/(.*)',          'TeamScore',
    '/api/scorebreakdown/(.+)',  'TeamScoreBreakdownJson',
    '/scorebreakdown/(.+)',      'TeamScoreBreakdown',
    '/rankchart(.*)',       'TeamRanking',
    '/api/rankings(.*)',    'TeamRankingJson',
    '/rankings(.*)',        'TeamRankingJson',
    '/attrrankings/(.*)/(.*)',   'TeamAttributeRankings',
    '/rankingsarray',       'TeamRankingsArray',
    '/recalculaterankings', 'RecalculateRankings',
    '/test',                'TeamAttributes',
    '/teamdata/(.*)',       'TeamDataFiles',
    '/ScoutingData/(.*)',   'TeamDataFile',
    '/notes/(.*)',          'TeamNotes',
    '/genui',               'GenUi',
    '/config',              'SetConfig',
    '/newissue',            'NewIssue',
    '/newissue/(.*)',       'NewPlatformIssue',
    '/api/issue/(.*)',      'IssueJson',
    '/issue/(.*)',          'Issue',
    '/issueupdate/(.*)',    'IssueUpdate',
    '/issuecomment/(.*)',   'IssueComment',
    '/debriefcomment/(.*)/(.*)', 'DebriefComment',
    '/deletecomment/(.*)/(.+)',  'DeleteComment',
    '/issues',              'IssuesHomePage',
    '/issues/(.*)',         'PlatformIssuesHomePage',
    '/api/issues/(.*)',     'PlatformIssuesJson',
    '/debrief/(.*)/(.*)',   'DebriefPage',
    '/debriefs/(.*)',       'DebriefsHomePage',
    '/user/(.*)',           'User',
    '/userprofile',         'UserProfile',
    '/newuser',             'NewUser',
    '/deleteuser',          'DeleteUser',
    '/users',               'Users',
    '/loadusers',           'LoadUsers',
    '/taskgroup_email/(.*)','TaskGroupEmail',
    '/taskgroup/(.*)',      'TaskGroup',
    '/taskgroups',          'TaskGroups',
    '/events',              'Events',
    '/eventstandings/(.*)', 'EventStandings',
    '/eventresults/(.*)',   'EventResults',
    '/setweights',          'SetWeights',
    '/attrrank(.*)',        'AttrRankPage',
    
    '/testpage(.*)',        'TestPage',
        
    '/sync/(.*)',           'Sync'
)


logger = Logger.init_logger('./config', 'logging.conf', 'scouting.webapp')

global_config = { 'my_team'            : '1073',
                  'this_competition'   : 'Test2014', 
                  'other_competitions' : '', 
                  'db_name'            : 'scouting', 
                  'issues_db_name'     : 'issues',
                  'issues_db_master'   : 'No',
                  'debriefs_db_name'   : 'debriefs',
                  'users_db_name'      : 'users',
                  'attr_definitions'   : None,
                  'team_list'          : '',
                  'event_code'         : '',
                  'issue_types'        : 'Robot,MobileBase',
                  'logger':logger }

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

read_config(global_config, './config/ScoutingAppConfig.txt')
db_name = global_config['db_name'] + '.db'
    
webserver_app = web.application(urls, globals())

class Login(object):
    def GET(self):
        return WebLogin.auth_user(global_config)
    
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

    def GET(self):
        username, access_level = WebLogin.check_access(global_config,10)
        result = WebHomePage.get_page(global_config, access_level)
        if global_config.has_key('my_team'):
            team = global_config['my_team']
        else:
            team = '1073'
        return render.page('Team %s Competition Central' % team, result)

    
class TestPage(object):

    def GET(self, param_str):
        username, access_level = WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        comp = 'GSR2013'
        attr = 'Teleop_Points'
        if numparams == 3:
            comp = params[1]
            attr = params[2]
        return render.attrRank(comp,attr)
    
class AttrRankPage(object):

    def GET(self, param_str):
        username, access_level = WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        comp = global_config['this_competition']
        attr = 'Teleop_Goals'
        if numparams == 3:
            comp = params[1]
            attr = params[2]
        return render.attrRank(comp,attr)
    
class AdminPage(object):

    def GET(self):
        access_level = WebLogin.check_access(global_config,1)[1]
        result = WebAdminPage.get_page(global_config, access_level)
        if global_config.has_key('my_team'):
            team = global_config['my_team']
        else:
            team = '1073'
        return render.page('Team %s Administration' % team, result)
    
class TeamDataFiles(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        result = WebTeamData.get_team_datafiles_page(global_config, name)
        return render.page('Team %s Scouting Data Page' % name, result)
                           
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
            comp = global_config['this_competition']
        elif numparams >= 2:
            comp = params[0]
            name = params[1]
        else:
            return None
        return WebTeamData.get_team_score_breakdown_page(global_config, name, comp)

        
class TeamScoreBreakdown(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        if numparams == 1:
            comp = global_config['this_competition']
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
            comp = global_config['this_competition']
        else:
            comp = params[1]
        return WebTeamData.get_team_rankings_page(global_config, comp)

class TeamRanking(object):

    def GET(self, param_str):
        WebLogin.check_access(global_config,10)
        params = param_str.split('/')
        numparams = len(params)
        if numparams < 2 or params[1] == '':
            comp = global_config['this_competition']
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
        result = WebTeamData.get_team_datafile_page(global_config, filename)
        return render.page('Scouting Data File: %s' % filename.split('/', 1)[1], result)


class RecalculateRankings(object):

    def GET(self):
        WebLogin.check_access(global_config,4)
        DataModel.recalculate_scoring(global_config)
        
        raise web.seeother('/rankchart')

class Events(object):

    def GET(self):
        WebLogin.check_access(global_config,10)
        result = WebEventData.get_events_page(global_config, '2014')
        return render.page('FIRST Robotics Competition Events', result)
                           
class EventStandings(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        year = name[0:4]
        event_code = name[4:]
        result = WebEventData.get_event_standings_page(global_config, year, event_code)
        return render.page('FIRST Robotics Standings Details - %s' % event_code.upper(), result)
                           
class EventResults(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        year = name[0:4]
        event_code = name[4:]
        result = WebEventData.get_event_results_page(global_config, year, event_code)
        return render.page('FIRST Robotics Event Match Results - %s' % event_code.upper(), result)                           
    
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
        if access_level <= 1:
            result = WebIssueTracker.get_platform_issues_home_page(global_config, platform_type, allow_create=True)
        else:
            result = WebIssueTracker.get_platform_issues_home_page(global_config, platform_type)
        return render.page('Team 1073 %s Issues' % platform_type, result)

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
        return WebIssueTracker.get_platform_issues(global_config, platform_type, status)

class Users(object):
    def GET(self):
        WebLogin.check_access(global_config,1)
        result = WebUsers.get_user_list_page(global_config)
        return render.page('User Administration', result)
    
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
        WebLogin.check_access(global_config,5)
        result = WebDebrief.get_debriefs_home_page(global_config, competition)
        return render.page('Team 1073 Match Debriefs', result)

class DebriefPage(object):

    def GET(self, comp, match):
        username, access_level = WebLogin.check_access(global_config,5)
        if access_level <=1:
            result = WebDebrief.get_debrief_page(global_config, comp, match, allow_update=True)
        else:
            result = WebDebrief.get_debrief_page(global_config, comp, match)
        return render.page('Team 1073 Debrief For Match %s:%s' % (comp,match), result)

class DebriefComment(object):
    def GET(self, comp, match):
        WebLogin.check_access(global_config,5)
        form = WebDebrief.get_match_comment_form(global_config, comp, match)
        return render.debrief_comment_form(form, comp, match)
           
    def POST(self, comp, match):
        username,access_level = WebLogin.check_access(global_config,5)
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

class Sync(object):
    def GET(self, request_path):
        response_body = FileSync.get(global_config, request_path)
        return response_body
        
    def PUT(self, request_path):
        content_type = web.ctx.env['CONTENT_TYPE']
        FileSync.put(global_config, request_path, content_type, web.data())
        return

class SetWeights(object):
    def GET(self):
        WebLogin.check_access(global_config,7)
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

    
     
'''    
class UsersUpdate(object):
    def GET(self):
            
    def POST(self):
'''
   
counter = 0
def process_files():
    global counter
    counter += 1
    
    try:
        print 'Scanning for new files to process'
        start_time = datetime.datetime.now()
        
        input_dir = './static/data/' + global_config['this_competition'] + '/ScoutingData/'

        if global_config['attr_definitions'] == None:
            print 'No Attribute Definitions, Skipping Process Files'
        else:
            attrdef_filename = './config/' + global_config['attr_definitions']
            if os.path.exists(attrdef_filename):
                attr_definitions = AttributeDefinitions.AttrDefinitions()
                attr_definitions.parse(attrdef_filename)
                   
                ProcessFiles.process_files(global_config, attr_definitions, input_dir)
                ProcessFiles.process_issue_files(global_config, input_dir)
                ProcessFiles.process_debrief_files(global_config, input_dir)
                print 'Scan %d complete, elapsed time - %s' % (counter,str(datetime.datetime.now()-start_time))
            else:
                print 'Attribute File %s Does Not Exist' % attrdef_filename
    except Exception, e:
        global_config['logger'].debug('Exception Caught Processing Files: %s' % str(e) )
        traceback.print_exc(file=sys.stdout)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        exception_info = traceback.format_exception(exc_type, exc_value,exc_traceback)
        for line in exception_info:
            line = line.replace('\n','')
            global_config['logger'].debug(line)

   
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
        "-b","--bluetooth",action="store_true", dest="bluetoothServer", default=False,
        help='Run Bluetooth Server')
   
    # Parse the command line arguments
    (options,args) = parser.parse_args()

    logger.debug("Running the Scouting App Web Server")

    db_name          = global_config['db_name']
    issues_db_name   = global_config['issues_db_name']
    debriefs_db_name = global_config['debriefs_db_name']
    users_db_name    = global_config['users_db_name']
    

    session          = DbSession.open_db_session(db_name, DataModel)
    '''
    issues_session   = DbSession.open_db_session(issues_db_name, IssueTrackerDataModel)
    debrief_session  = DbSession.open_db_session(debriefs_db_name, DebriefDataModel)
    '''
    
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
        logger.debug('Loading Users from file: %s' % users_file)
        UsersDataModel.add_users_from_file(users_session, users_file)

    # make sure that there is a default admin user. If no admin user exists, then create one
    if UsersDataModel.getUser( users_session, 'admin' ) is None:
        UsersDataModel.create_admin_user(users_session, 'squirrel!')

    users_session.close()

    # Build the attribute definition dictionary from the definitions spreadsheet file
    if global_config['attr_definitions'] != None:
        attrdef_filename = './config/' + global_config['attr_definitions']
        if os.path.exists(attrdef_filename):
            attr_definitions = AttributeDefinitions.AttrDefinitions()
            attr_definitions.parse(attrdef_filename)
            
            # WebGenExtJsStoreFiles.gen_js_store_files(global_config, attr_definitions)
            WebAttributeDefinitions.init_attr_def_forms(attr_definitions)


    # make sure that the required directories exist
    directories = ('ScoutingData', 'ScoutingPictures')
    for directory in directories:        
        base_dir = './static/data/' + global_config['this_competition'] + '/' + directory + '/'
        try: 
            os.makedirs(base_dir)
        except OSError:
            if not os.path.isdir(base_dir):
                raise
    
    # also create the configuration directory used to provide data to the tablets
    base_dir = './static/ScoutingConfig'
    try: 
        os.makedirs(base_dir)
    except OSError:
        if not os.path.isdir(base_dir):
            raise


    print 'Sys Args: %s' % sys.argv
    sys.argv[1:] = args
    
    if int(options.processloop) > 0:
        process_file_timer = TimerThread.RepeatedTimer(int(options.processloop), process_files)
    
    bluetooth_sync_server = None
    if options.bluetoothServer:
        bluetooth_sync_server = BluetoothSyncServer.BluetoothSyncServer()
        bluetooth_sync_server.start()

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
