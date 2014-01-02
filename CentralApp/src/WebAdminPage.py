'''
Created on Feb 7, 2013

@author: ksthilaire
'''

import DbSession
import DataModel
import WebCommonUtils

def get_page(global_config, access_level):
    global_config['logger'].debug( 'GET Admin Page' )
    
    session = DbSession.open_db_session(global_config['db_name'])
            
    page = ''
    page += '<hr>'
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

    return page

