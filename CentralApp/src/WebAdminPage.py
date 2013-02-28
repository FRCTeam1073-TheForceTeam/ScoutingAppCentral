'''
Created on Feb 7, 2013

@author: ksthilaire
'''

import DbSession
import DataModel

def get_page(global_config, access_level):
    global_config['logger'].debug( 'GET Admin Page' )
    
    session = DbSession.open_db_session(global_config['db_name'])
            
    page = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
    page += '<html>'
    page += '<head>'
    page += '<body>'
    if global_config.has_key('my_team'):
        page += '<h2> Team ' + global_config['my_team'] + ' Administration Home Page' + '</h3>'
    else:
        page += '<h2> Team 1073 Administration Page' + '</h3>'
    page += '<hr>'
    page += '<a href="/logout">Logout</a></td>'
    page += '<br>'
    page += '<a href="/userprofile">User Settings</a></td>'
    page += '<hr>'
    page += '<br>'
    page += '<a href="/users">User Management</a></td>'
    page += '<br>'
    page += '<a href="/taskgroups">Task Group Admin</a></td>'
    page += '<br>'
    page += '<a href="/taskgroup_email/all">Create Task Group Email/Text List File</a></td>'
    page += '<br>'
    if access_level == 0:
        page += '<a href="/genui">Tablet User Interface Generation</a></td>'
        page += '<br>'
        page += '<a href="/config">System Configuration</a></td>'
        page += '<br>'
    page += '<br>'
    page += '<hr>'
    page += '</body>'
    page += '</html>'
    return page

