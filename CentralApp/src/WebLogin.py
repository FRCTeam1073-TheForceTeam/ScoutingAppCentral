'''
Created on Feb 08, 2013

@author: ksthilaire
'''

import re
import base64
import web

import DbSession
import IssueTrackerDataModel

allowed = (
    ('user','dean'),
    ('user2','woodie')
)

logged_out_users = {}
    
def auth_user(global_config):
    auth = web.ctx.env.get('HTTP_AUTHORIZATION')
    authreq = False
    
    if auth is None:
        authreq = True
    else:
        auth = re.sub('^Basic ','',auth)
        username,password = base64.decodestring(auth).split(':')
        
        if logged_out_users.has_key(username):
            del logged_out_users[username]
        else:
            session = DbSession.open_db_session(global_config['issues_db_name'])
            user = IssueTrackerDataModel.getUser(session, username)
            if user:
                if user.state == 'Disabled':
                    raise web.seeother('/accountdisabled')
                #if (username,password) in allowed:
                if user.check_password(password) == True:
                    raise web.seeother('/home')
        authreq = True
    if authreq:
        web.header('WWW-Authenticate','Basic realm="FRC1073 ScoutingAppCentral"')
        web.ctx.status = '401 Unauthorized'
        return

def do_logout(global_config):
    auth = web.ctx.env.get('HTTP_AUTHORIZATION')
    if auth is None:
        raise web.seeother('/login')
    else:
        auth = re.sub('^Basic ','',auth)
        username,password = base64.decodestring(auth).split(':')
        logged_out_users[username] = True
        web.header('Cache-Control','no-cache')
        web.header('Pragma','no-cache')
        
        result = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
        result += '<html>'
        result += '<head>'
        result += '<body>'
        result += username + ' is now logged out, click <a href="/login">Here</a> to log back in'
        result += '</body>'
        result += '</head>'
        result += '</html>'
        return result

def check_access(global_config, access_level):
    auth = web.ctx.env.get('HTTP_AUTHORIZATION')
    
    if auth is None:
        raise web.seeother('/login')
    else:
        auth = re.sub('^Basic ','',auth)
        username,password = base64.decodestring(auth).split(':')
        
        # here is where we need to do a lookup in the user database and see if the
        # user is authorized to access this page.
        session = DbSession.open_db_session(global_config['issues_db_name'])
        user = IssueTrackerDataModel.getUser(session, username)
        if user:
            if user.check_access_level(access_level) == True:
                return (username,user.access_level)
            
        raise web.seeother('/accessdenied')
        
def do_account_disabled(global_config):
    auth = web.ctx.env.get('HTTP_AUTHORIZATION')
    if auth is None:
        raise web.seeother('/login')
    else:
        auth = re.sub('^Basic ','',auth)
        username,password = base64.decodestring(auth).split(':')
        logged_out_users[username] = True
        web.header('Cache-Control','no-cache')
        web.header('Pragma','no-cache')
        
        result = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
        result += '<html>'
        result += '<head>'
        result += '<body>'
        result += username + ' account is disabled, click <a href="/login">Here</a> once account is re-enabled'
        result += '</body>'
        result += '</head>'
        result += '</html>'
        return result

