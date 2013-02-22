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

import IssueTrackerDataModel
import AttributeDefinitions
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from optparse import OptionParser

import WebHomePage
import WebTeamData
import WebGenExtJsStoreFiles
import WebUiGen
import WebSetConfig
import WebLogin
import WebIssueTracker
import WebUsers

render = web.template.render('templates/')

urls = (
    '/login',               'Login',
    '/home',                'HomePage',    
    '/team/(.*)',           'TeamServer',
    '/score/(.*)',          'TeamScore',
    '/rankings',            'TeamRankings',
    '/test',                'TeamAttributes',
    '/teamdata/(.*)',       'TeamDataFiles',
    '/ScoutingData/(.*)',   'TeamDataFile',
    '/notes/(.*)',          'TeamNotes',
    '/genui',               'GenUi',
    '/config',              'SetConfig',
    '/newissue',            'NewIssue',
    '/issue/(.*)',          'Issue',
    '/issues',              'IssuesHomePage',
    '/user/(.*)',           'User',
    '/users',               'Users',
    '/taskgroup_email/(.*)','TaskGroupEmail'
)


logging.config.fileConfig('config/logging.conf')
logger = logging.getLogger('scouting.webapp')

global_config = {'my_team': '1074',
                 'this_competition':None, 
                 'other_competitions':None, 
                 'db_name': 'scouting2013',
                 'team_list':None,
                 'issues_db_name': 'issues2013',
                 'logger': logger }

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

read_config(global_config, './config/ScoutingAppConfig.txt')
db_name = global_config['db_name']   
    
webserver_app = web.application(urls, globals())

class Login:
    def GET(self):
        
        return WebLogin.auth_user()

class HomePage(object):

    def GET(self):
        WebLogin.check_access()
        
        return WebHomePage.get_page(global_config)
    
class TeamDataFiles(object):

    def GET(self, name):
        return WebTeamData.get_team_datafiles_page(global_config, name)
                           
class TeamServer(object):

    def GET(self, name):
        return WebTeamData.get_team_server_page(global_config, name)
        
class TeamScore(object):

    def GET(self, name):
        return WebTeamData.get_team_score_page(global_config, name)

class TeamNotes(object):

    def GET(self, name):
        return WebTeamData.get_team_notes_page(global_config, name)

class TeamRankings(object):

    def GET(self):
        return WebTeamData.get_team_rankings_page(global_config)

class TeamAttributes(object):

    def GET(self):
        return WebTeamData.get_team_attributes_page(global_config)
   
class TeamDataFile(object):

    def GET(self, filename):
        return WebTeamData.get_team_datafile_page(global_config, filename)
    
class GenUi(object):
    
    def GET(self):
        form = WebUiGen.get_form(global_config)
        return render.formtest(form)
   
    def POST(self):
        form = WebUiGen.get_form(global_config)
        if not form.validates(): 
            return render.formtest(form)
        else:
            return WebUiGen.process_form(global_config, form)
   
class SetConfig(object):
    def GET(self):
        
        form = WebSetConfig.get_form(global_config)
        return render.cfg_form(form)

    def POST(self):
        form = WebSetConfig.get_form(global_config)
        if not form.validates(): 
            return render.cfg_form_done(form)
        else:
            WebSetConfig.process_form(global_config, form)
            return render.cfg_form_done(form)

class NewIssue(object):
    def GET(self):
        form = WebIssueTracker.get_new_issue_form(global_config)
        return render.new_issue_form(form)
           
    def POST(self):
        form = WebIssueTracker.get_new_issue_form(global_config)
        if not form.validates(): 
            return render.new_issue_form_done(form)
        else:
            return WebIssueTracker.process_new_issue_form(global_config, form)
               
class Issue(object):
    
    def GET(self, issue_id):
        form = WebIssueTracker.get_issue_form(global_config, issue_id)
        return render.issue_form(form)

    def POST(self, issue_id):
        form = WebIssueTracker.get_issue_form(global_config, issue_id)
        if not form.validates(): 
            return render.issue_form_done(form)
        else:
            return WebIssueTracker.process_issue_form(global_config, form, issue_id)
        
class IssuesHomePage(object):

    def GET(self):
        return WebIssueTracker.get_issues_home_page(global_config)

class Users(object):
    def GET(self):
        return WebUsers.get_user_list_page(global_config)
    
class User(object):
    
    def GET(self, username):
        form = WebUsers.get_user_form(global_config, username)
        return render.user_form(form)

    def POST(self, username):
        form = WebUsers.get_user_form(global_config, username)
        if not form.validates(): 
            return render.user_form_done(form)
        else:
            try:
                return WebUsers.process_user_form(global_config, form, username)
            except Exception, e:
                return str(e)

class TaskGroupEmail(object):
    def GET(self, name):
        return IssueTrackerDataModel.getTaskgroupEmailLists(global_config, name)
    
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

    # create the issues database if required
    db_name = global_config['issues_db_name']
    db_connect='sqlite:///%s'%(db_name)
    my_db = create_engine(db_connect)
    if not os.path.exists('./' + db_name):    
        IssueTrackerDataModel.create_db_tables(my_db)
        IssueTrackerDataModel.create_admin_user(db_name, 'squirrel!')

    # Build the attribute definition dictionary from the definitions spreadsheet file
    attrdef_filename = './config/' + global_config['attr_definitions']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)

    if options.users_file != '':
        users_file = './config/' + options.users_file
        logger.debug('Loading Users from file: %s' % users_file)
        IssueTrackerDataModel.add_users_from_file(db_name, users_file)

    print 'Sys Args: %s' % sys.argv
    sys.argv[1:] = args
    
    
    WebGenExtJsStoreFiles.gen_js_store_files(attr_definitions)
    
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
