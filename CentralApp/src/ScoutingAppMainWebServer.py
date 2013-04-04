'''
Created on Dec 19, 2011

@author: ksthilaire
'''


import os
import web
import sys
import traceback

import logging
import logging.config

import DbSession
import DataModel
import DebriefDataModel
import IssueTrackerDataModel
import AttributeDefinitions
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from optparse import OptionParser

import FileSync
import DataModel
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

render = web.template.render('templates/')

urls = (
    '/login',               'Login',
    '/logout',              'Logout',
    '/accessdenied',        'AccessDenied',
    '/accountdisabled',     'AccountDisabled',
    '/home',                'HomePage',
    '/admin',               'AdminPage',    
    '/team/(.*)',           'TeamServer',
    '/score/(.*)',          'TeamScore',
    '/rankings',            'TeamRankings',
    '/recalculaterankings',  'RecalculateRankings',
    '/test',                'TeamAttributes',
    '/teamdata/(.*)',       'TeamDataFiles',
    '/ScoutingData/(.*)',   'TeamDataFile',
    '/notes/(.*)',          'TeamNotes',
    '/genui',               'GenUi',
    '/config',              'SetConfig',
    '/newissue',            'NewIssue',
    '/issue/(.*)',          'Issue',
    '/issueupdate/(.*)',    'IssueUpdate',
    '/issuecomment/(.*)',   'IssueComment',
    '/debriefcomment/(.*)', 'DebriefComment',
    '/deletecomment/(.+)',  'DeleteComment',
    '/issues',              'IssuesHomePage',
    '/debrief/(.*)',        'DebriefPage',
    '/debriefs',            'DebriefsHomePage',
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
    
    '/sync/(.*)',           'Sync'
)


logging.config.fileConfig('config/logging.conf')
logger = logging.getLogger('scouting.webapp')

global_config = { 'my_team'            : '1073',
                  'this_competition'   : None, 
                  'other_competitions' : None, 
                  'db_name'            : 'scouting2013', 
                  'issues_db_name'     : 'issues2013',
                  'issues_db_master'   : 'No',
                  'debriefs_db_name'   : 'debriefs2013',
                  'attr_definitions'   : None,
                  'team_list'          : None,
                  'event_code'         : None,
                  'logger':logger }

def read_config(config_dict, config_filename):
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
db_name = global_config['db_name']   
    
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
        return WebHomePage.get_page(global_config, access_level)
    
class AdminPage(object):

    def GET(self):
        username, access_level = WebLogin.check_access(global_config,1)
        return WebAdminPage.get_page(global_config, access_level)
    
class TeamDataFiles(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        return WebTeamData.get_team_datafiles_page(global_config, name)
                           
class TeamServer(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        return WebTeamData.get_team_server_page(global_config, name)
        
class TeamScore(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        return WebTeamData.get_team_score_page(global_config, name)

class TeamNotes(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        return WebTeamData.get_team_notes_page(global_config, name)

class TeamRankings(object):

    def GET(self):
        WebLogin.check_access(global_config,10)
        return WebTeamData.get_team_rankings_page(global_config)

class TeamAttributes(object):

    def GET(self):
        WebLogin.check_access(global_config,10)
        return WebTeamData.get_team_attributes_page(global_config)
   
class TeamDataFile(object):

    def GET(self, filename):
        WebLogin.check_access(global_config,10)
        return WebTeamData.get_team_datafile_page(global_config, filename)

class RecalculateRankings(object):

    def GET(self):
        WebLogin.check_access(global_config,4)
        DataModel.recalculate_scoring(global_config)
        WebGenExtJsStoreFiles.gen_js_store_files(global_config)

        raise web.seeother('/static/test/designer.html')

class Events(object):

    def GET(self):
        WebLogin.check_access(global_config,10)
        return WebEventData.get_events_page(global_config)
                           
class EventStandings(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        return WebEventData.get_event_standings_page(global_config, name)
                           
class EventResults(object):

    def GET(self, name):
        WebLogin.check_access(global_config,10)
        return WebEventData.get_event_results_page(global_config, name)
                           
    
class GenUi(object):
    
    def GET(self):
        WebLogin.check_access(global_config,0)
        form = WebUiGen.get_form(global_config)
        return render.formtest(form)
   
    def POST(self):
        WebLogin.check_access(global_config,0)
        form = WebUiGen.get_form(global_config)
        if not form.validates(): 
            return render.formtest(form)
        else:
            return WebUiGen.process_form(global_config, form)
   
class SetConfig(object):
    def GET(self):
        WebLogin.check_access(global_config,0)        
        form = WebSetConfig.get_form(global_config)
        return render.cfg_form(form)

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
        return render.new_issue_form(form)
           
    def POST(self):
        WebLogin.check_access(global_config,2)
        form = WebIssueTracker.get_new_issue_form(global_config)
        if not form.validates(): 
            return render.new_issue_form_done(form)
        else:
            result = WebIssueTracker.process_new_issue_form(global_config, form)
            raise web.seeother(result)

class IssueComment(object):
    def GET(self, issue_id):
        WebLogin.check_access(global_config,5)
        form = WebIssueTracker.get_issue_comment_form(global_config, issue_id)
        return render.issue_comment_form(form)
           
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
        return render.issue_form(form)

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
            return WebIssueTracker.get_issue_page(global_config, issue_id, allow_update=True)
        else:
            return WebIssueTracker.get_issue_page(global_config, issue_id)
        
class DeleteComment(object):
    
    def GET(self, param_str):
        username, access_level = WebLogin.check_access(global_config,1)
        params = param_str.split('/')
        if params[0] == 'issue':
            result = WebIssueTracker.delete_comment(global_config,params[1], params[2])
        elif params[0] == 'debrief':
            result = WebDebrief.delete_comment(global_config,params[1], params[2])
        else:
            return "404 Not Found"

        raise web.seeother(result)
 
        
class IssuesHomePage(object):

    def GET(self):
        username, access_level = WebLogin.check_access(global_config,5)
        if access_level <= 1:
            return WebIssueTracker.get_issues_home_page(global_config,allow_create=True)
        else:
            return WebIssueTracker.get_issues_home_page(global_config)

class Users(object):
    def GET(self):
        WebLogin.check_access(global_config,1)
        return WebUsers.get_user_list_page(global_config)
    
class LoadUsers(object):
    
    def GET(self):
        WebLogin.check_access(global_config,1)
        form = WebUsers.get_load_user_form(global_config)
        return render.user_form(form)

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
        return render.user_form(form)

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
        return render.user_form(form)

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
        return render.user_form(form)

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
        return render.user_form(form)

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

    def GET(self):
        WebLogin.check_access(global_config,5)
        return WebDebrief.get_debriefs_home_page(global_config)

class DebriefPage(object):

    def GET(self, match):
        username, access_level = WebLogin.check_access(global_config,5)
        if access_level <=1:
            return WebDebrief.get_debrief_page(global_config, match, allow_update=True)
        else:
            return WebDebrief.get_debrief_page(global_config, match)
        WebLogin.check_access(global_config,5)

class DebriefComment(object):
    def GET(self, match):
        WebLogin.check_access(global_config,5)
        form = WebDebrief.get_match_comment_form(global_config, match)
        return render.issue_comment_form(form)
           
    def POST(self, match):
        username,access_level = WebLogin.check_access(global_config,5)
        form = WebDebrief.get_match_comment_form(global_config, match)
        if not form.validates(): 
            return render.issue_comment_form_done(form)
        else:
            result = WebDebrief.process_match_comment_form(global_config, form, match, username)
            raise web.seeother(result)
        
class TaskGroupEmail(object):
    def GET(self, name):
        email_lists = IssueTrackerDataModel.getTaskgroupEmailLists(global_config, name)
        fd = open('./config/TaskGroupEmailLists.txt', 'w+')
        fd.write( email_lists )
        fd.close()
        return email_lists

class Sync(object):
    def GET(self, request_path):
        response_body = FileSync.get(global_config, request_path)
        return response_body
        
    def PUT(self, request_path):
        content_type = web.ctx.env['CONTENT_TYPE']
        FileSync.put(global_config, request_path, content_type, web.data())
        return
    
     
'''    
class UsersUpdate(object):
    def GET(self):
            
    def POST(self):
'''
   
if __name__ == "__main__":

    # command line options handling
    parser = OptionParser()
    
    parser.add_option(
        "-t","--test",action="store_true",dest="test",default=False,
        help="Processed test toggle")
    parser.add_option(    
        "-u","--users",dest="users_file",default='',
        help="List of Users to use for issue tracking")
   
    # Parse the command line arguments
    (options,args) = parser.parse_args()

    logger.debug("Running the Scouting App Web Server")

    db_name = global_config['db_name']
    issues_db_name = global_config['issues_db_name']
    debriefs_db_name = global_config['debriefs_db_name']
    session         = DbSession.open_db_session(db_name, DataModel)
    issues_session  = DbSession.open_db_session(issues_db_name, IssueTrackerDataModel)
    debrief_session = DbSession.open_db_session(debriefs_db_name, DebriefDataModel)
 
    # load the users file if one is specified
    if options.users_file != '':
        users_file = './config/' + options.users_file
        logger.debug('Loading Users from file: %s' % users_file)
        IssueTrackerDataModel.add_users_from_file(issues_db_name, users_file)

    # make sure that there is a default admin user. If no admin user exists, then create one
    if IssueTrackerDataModel.getUser( issues_session, 'admin' ) is None:
        IssueTrackerDataModel.create_admin_user(issues_session, 'squirrel!')

    # Build the attribute definition dictionary from the definitions spreadsheet file
    attrdef_filename = './config/' + global_config['attr_definitions']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)

    print 'Sys Args: %s' % sys.argv
    sys.argv[1:] = args
    
    
    WebGenExtJsStoreFiles.gen_js_store_files(global_config, attr_definitions)
    
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
