'''
Created on Feb 14, 2013

@author: ksthilaire
'''

from web import form

import DbSession
import IssueTrackerDataModel

user_roles = [ 'Mentor', 'Student', 'Guest' ]
user_subgroups = ['','Mechanical', 'Software', 'Electrical', 'Integration', 'Strategy', 'Business']
user_contact_modes = ['Text', 'Email']
user_carriers = ['AT&T', 'Verizon', 'USCellular', 'Sprint', 'Other', 'None']

user_username_label ='Username:'
user_emailaddress_label ='Email_Address:'
user_display_name_label ='Display_Name:'
user_nickname_label ='Nickname:'
user_role_label = 'Role:'
user_subgroup_label = 'Subgroup:'
user_contact_mode_label = 'Contact_Mode:'
user_cellphone_label = 'Cellphone:'
user_carrier_label = 'Carrier:'
user_password_label = 'Password:'
user_password_confirm_label = 'Confirm:'

userform = form.Form( 
    form.Textbox(user_username_label, size=30),
    form.Password(user_password_label, size=30),
    form.Password(user_password_confirm_label, size=30),
    form.Textbox(user_emailaddress_label, size=30),
    form.Textbox(user_display_name_label, size=30),
    form.Textbox(user_nickname_label, size=30),
    form.Dropdown(user_role_label, user_roles),
    form.Dropdown(user_subgroup_label, user_subgroups),
    form.Dropdown(user_contact_mode_label, user_contact_modes),
    form.Textbox(user_cellphone_label, size=30),
    form.Dropdown(user_carrier_label, user_carriers))

def get_user_form(global_config, username):
    global_config['logger'].debug( 'GET User Form For: %s', username )
        
    session = DbSession.open_db_session(global_config['issues_db_name'])

    user = IssueTrackerDataModel.getUser(session, username)
    
    form = userform()
    form[user_username_label].value = user.username
    form[user_emailaddress_label].value = user.email_address
    form[user_cellphone_label].value = user.cellphone
    form[user_carrier_label].value = user.carrier
    form[user_subgroup_label].value = user.subgroup
    form[user_password_label].value = user.password
    form[user_display_name_label].value = user.display_name
    form[user_role_label].value = user.role
    form[user_contact_mode_label].value = user.contact_mode
    form[user_nickname_label].value = user.altname

    return form

def process_user_form(global_config, form, username):
    global_config['logger'].debug( 'Process User Profile For: %s', username )
    
    session = DbSession.open_db_session(global_config['issues_db_name'])
                    
    email_address = form[user_emailaddress_label].value
    cellphone = form[user_cellphone_label].value
    carrier = form[user_carrier_label].value
    subgroup = form[user_subgroup_label].value
    if form[user_password_label].value != form[user_password_confirm_label].value:
        raise Exception('Passwords Do NOT Match')

    password = form[user_password_label].value
    display_name = form[user_display_name_label].value
    role = form[user_role_label].value
    contact_mode = form[user_contact_mode_label].value
    nickname = form[user_nickname_label].value
    if role == 'Mentor':
        access_level = 3
    elif role == 'Student':
        access_level = 5
    elif role == 'Guest':
        access_level = 10
                
    IssueTrackerDataModel.addOrUpdateUser(session, username, email_address, 
                                          cellphone, carrier, subgroup, password, 
                                          display_name, role, contact_mode, nickname,
                                          access_level)
    
    session.commit()
    
    return 'User Profile Updated Successfully For: %s' % username            


def insert_users_table(user_list):
        
        table_str = '<table border="1" cellspacing="5">'
        
        table_str += '<tr>'
        table_str += '<th>Username</th>'
        table_str += '<th>Email_Address</th>'
        table_str += '<th>Display_Name</th>'
        table_str += '<th>Nickname</th>'
        table_str += '<th>Role</th>'
        table_str += '<th>Subgroup</th>'
        table_str += '<th>Contact_Mode</th>'
        table_str += '<th>Cellphone</th>'
        table_str += '<th>Carrier</th>'
        table_str += '</tr>'
        
        for user in user_list:
            table_str += '<tr>'            
            table_str += '<td><a href="/user/' + user.username + '"> ' + user.username + '</a></td>'
            table_str += '<td>' + user.email_address + '</td>'
            table_str += '<td>' + user.display_name + '</td>'
            table_str += '<td>' + user.altname + '</td>'
            table_str += '<td>' + user.role + '</td>'
            table_str += '<td>' + user.subgroup + '</td>'
            table_str += '<td>' + user.contact_mode + '</td>'
            table_str += '<td>' + user.cellphone + '</td>'
            table_str += '<td>' + user.carrier + '</td>'
            table_str += '</tr>'
        table_str += '</table>'
        table_str += '</ul>'
        return table_str

def get_user_list_page(global_config):
 
    session = DbSession.open_db_session(global_config['issues_db_name'])

    result = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
    result += '<html>'
    result += '<head>'
    result += '<body>'
    result += '<h2> Team ' + global_config['my_team'] + ' Users' + '</h3>'
    result += '<hr>'
    result += '<br>'
    result += '<a href="/home"> Home</a></td>'
    result += '<br>'
    result += '<a href="/newuser"> Create New User</a></td>'
    result += '<br>'
    result += '<br>'
    result += '<hr>'
    
    user_list = IssueTrackerDataModel.getUserList(session)
    result += insert_users_table(user_list)
    
    result += '</body>'
    result += '</html>'
    return result
