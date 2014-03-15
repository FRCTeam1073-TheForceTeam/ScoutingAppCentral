'''
Created on Feb 14, 2013

@author: ksthilaire
'''

from web import form
from myform import pureform as pureform

import DbSession
import UsersDataModel
import WebCommonUtils

user_roles = [ 'Mentor', 'Student', 'Guest' ]
user_subgroups = ['','Mechanical', 'Software', 'Electrical', 'Integration', 'Strategy', 'Business']
user_contact_modes = ['Text', 'Email']
user_carriers = ['AT&T', 'Verizon', 'USCellular', 'Sprint', 'TMobile', 'Other', 'None']
user_access_levels = [0,1,2,3,4,5,6,7,8,9,10]
user_states = ['Enabled', 'Disabled']

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
user_access_level_label = 'Access_Level:'
user_taskgroups_label = 'Taskgroups:'
user_state_label = 'State:'

users_list = []

userform = pureform(
    form.Textbox(user_username_label, size=30),
    form.Password(user_password_label, size=30),
    form.Password(user_password_confirm_label, size=30),
    form.Textbox(user_emailaddress_label, size=30),
    form.Textbox(user_display_name_label, size=30),
    form.Textbox(user_nickname_label, size=30),
    form.Dropdown(user_access_level_label, user_access_levels),
    form.Dropdown(user_role_label, user_roles),
    form.Dropdown(user_subgroup_label, user_subgroups),
    form.Dropdown(user_contact_mode_label, user_contact_modes),
    form.Textbox(user_cellphone_label, size=30),
    form.Textbox(user_taskgroups_label, size=80),
    form.Dropdown(user_carrier_label, user_carriers),
    form.Dropdown(user_state_label, user_states))

userprofileform = pureform(
    form.Textbox(user_username_label, size=30),
    form.Password(user_password_label, size=30),
    form.Password(user_password_confirm_label, size=30),
    form.Textbox(user_emailaddress_label, size=30),
    form.Textbox(user_display_name_label, size=30),
    form.Textbox(user_nickname_label, size=30),
    form.Dropdown(user_subgroup_label, user_subgroups),
    form.Dropdown(user_contact_mode_label, user_contact_modes),
    form.Textbox(user_cellphone_label, size=30),
    form.Dropdown(user_carrier_label, user_carriers))

deleteuserform = pureform(
    form.Dropdown(user_username_label, users_list))
                           
user_file_label = 'Users Spreadsheet Filename:'
load_users_form = pureform(
    form.Textbox(user_file_label, size=30))

def get_user_form(global_config, username):
    global_config['logger'].debug( 'GET User Form For: %s', username )
        
    session = DbSession.open_db_session(global_config['users_db_name'])

    user = UsersDataModel.getUser(session, username)
    form = userform()
    if user:
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
        form[user_access_level_label].value = user.access_level
        form[user_state_label].value = user.state
        form[user_taskgroups_label].value = UsersDataModel.getUserTaskgroups(session, user.username)
    else:
        form[user_access_level_label].value = 10
        form[user_role_label].value = 'Guest'

    session.close()

    return form

def process_user_form(global_config, form, username, my_access_level, new_user=False):
    if new_user == True:
        username = form[user_username_label].value
        
    global_config['logger'].debug( 'Process User Profile For: %s', username )
    
    session = DbSession.open_db_session(global_config['users_db_name'])
                                
    email_address = form[user_emailaddress_label].value
    cellphone = form[user_cellphone_label].value
    carrier = form[user_carrier_label].value
    subgroup = form[user_subgroup_label].value
    
    user = UsersDataModel.getUser(session, username)
    if user:
        if new_user == True:
            raise Exception('User Already Exists!')
            
        # validate the password confirmation only if the user actually changed his
        # password
        if form[user_password_label].value != user.password:
            if form[user_password_label].value != form[user_password_confirm_label].value:
                raise Exception('Passwords Do NOT Match')
        # also make sure to pull username from the database, in case the user
        # provided the nickname
        username = user.username
    password = form[user_password_label].value
    display_name = form[user_display_name_label].value
    role = form[user_role_label].value
    contact_mode = form[user_contact_mode_label].value
    nickname = form[user_nickname_label].value
    access_level = int(form[user_access_level_label].value)
    if access_level == 0:
        if my_access_level >0: 
            raise Exception('Only Supreme Admins (aka NOT you) can set access level to 0')
    taskgroups = form[user_taskgroups_label].value
    state = form[user_state_label].value
    
    UsersDataModel.addOrUpdateUser(session, username, email_address, 
                                          cellphone, carrier, subgroup, password, 
                                          display_name, role, contact_mode, nickname,
                                          access_level, state)

    UsersDataModel.updateUserTaskgroups(session, username, taskgroups)
        
    session.commit()
    session.close()
    return '/users'

def get_delete_user_form(global_config):
    global_config['logger'].debug( 'GET Delete User Form' )
        
    session = DbSession.open_db_session(global_config['users_db_name'])

    form = deleteuserform()

    # apply the valid list of user names to the dropdown 
    # for the username field
    username_list = UsersDataModel.getUsernameList(session)
    form[user_username_label].args = username_list
    form[user_username_label].args = username_list

    session.close()

    return form

def process_delete_user_form(global_config, form):
    global_config['logger'].debug( 'Process Delete User' )
    
    session = DbSession.open_db_session(global_config['users_db_name'])
    username = form[user_username_label].value
    UsersDataModel.deleteUser(session, username)
    session.commit()
    session.close()

    return '/users'

def get_userprofile_form(global_config, username):
    global_config['logger'].debug( 'GET User Form For: %s', username )
        
    session = DbSession.open_db_session(global_config['users_db_name'])

    user = UsersDataModel.getUser(session, username)
    
    form = userprofileform()
    form[user_username_label].value = user.username
    form[user_emailaddress_label].value = user.email_address
    form[user_cellphone_label].value = user.cellphone
    form[user_carrier_label].value = user.carrier
    form[user_subgroup_label].value = user.subgroup
    form[user_password_label].value = user.password
    form[user_display_name_label].value = user.display_name
    form[user_contact_mode_label].value = user.contact_mode
    form[user_nickname_label].value = user.altname

    session.close()

    return form

def process_userprofile_form(global_config, form, username):
    global_config['logger'].debug( 'Process User Profile For: %s', username )
    
    session = DbSession.open_db_session(global_config['users_db_name'])
                                
    email_address = form[user_emailaddress_label].value
    cellphone = form[user_cellphone_label].value
    carrier = form[user_carrier_label].value
    subgroup = form[user_subgroup_label].value
    
    # set default access level and rols, and override if the user is already in the system
    access_level = 5
    role = 'Guest'
    user = UsersDataModel.getUser(session, username)
    if user:
        # validate the password confirmation only if the user actually changed his
        # password
        if form[user_password_label].value != user.password:
            if form[user_password_label].value != form[user_password_confirm_label].value:
                raise Exception('Passwords Do NOT Match')

        access_level = user.access_level
        role = user.role
        state = user.state
        
    password = form[user_password_label].value
    display_name = form[user_display_name_label].value
    contact_mode = form[user_contact_mode_label].value
    nickname = form[user_nickname_label].value
                    
    UsersDataModel.addOrUpdateUser(session, username, email_address, 
                                          cellphone, carrier, subgroup, password, 
                                          display_name, role, contact_mode, nickname,
                                          access_level, state)
    session.commit()
    session.close()

    return '/home'

user_file_label = 'Users Spreadsheet Filename:'
load_users_form = pureform(
    form.Textbox(user_file_label, size=30))

def get_load_user_form(global_config):
    global_config['logger'].debug('GET Load Users Form' )
    form = load_users_form()
    return form

def process_load_user_form(global_config, form):
    global_config['logger'].debug('Process Load Users Form')
                                    
    users_file = './config/' + form[user_file_label].value
    global_config['logger'].debug('Loading Users from file: %s' % users_file)
    
    session = DbSession.open_db_session(global_config['users_db_name'])

    UsersDataModel.add_users_from_file(session, users_file)
    
    session.close()
    
    return '/users'

def insert_users_table(user_list):
        
        table_str = '<table border="1" cellspacing="5">'
        
        table_str += '<tr>'
        table_str += '<th>Username</th>'
        table_str += '<th>Email_Address</th>'
        table_str += '<th>Display_Name</th>'
        table_str += '<th>Nickname</th>'
        table_str += '<th>Access_Level</th>'
        table_str += '<th>Role</th>'
        table_str += '<th>Subgroup</th>'
        table_str += '<th>Contact_Mode</th>'
        table_str += '<th>Cellphone</th>'
        table_str += '<th>Carrier</th>'
        table_str += '<th>State</th>'
        table_str += '</tr>'
        
        for user in user_list:
            table_str += '<tr>'            
            table_str += '<td><a href="/user/' + user.username + '"> ' + user.username + '</a></td>'
            table_str += '<td>' + user.email_address + '</td>'
            table_str += '<td>' + user.display_name + '</td>'
            table_str += '<td>' + user.altname + '</td>'
            table_str += '<td>' + str(user.access_level) + '</td>'
            table_str += '<td>' + user.role + '</td>'
            table_str += '<td>' + user.subgroup + '</td>'
            table_str += '<td>' + user.contact_mode + '</td>'
            table_str += '<td>' + user.cellphone + '</td>'
            table_str += '<td>' + user.carrier + '</td>'
            table_str += '<td>' + user.state + '</td>'
            table_str += '</tr>'
        table_str += '</table>'
        table_str += '</ul>'
        return table_str

def get_user_list_page(global_config):
 
    session = DbSession.open_db_session(global_config['users_db_name'])

    result = ''
    result += '<hr>'
    result += '<br>'
    result += '<a href="/newuser"> Create New User</a></td>'
    result += '<br>'
    result += '<a href="/deleteuser"> Delete User</a></td>'
    result += '<br>'
    result += '<a href="/loadusers"> Load Users From File</a></td>'
    result += '<br>'
    result += '<br>'
    result += '<hr>'
    
    user_list = UsersDataModel.getUserList(session)
    result += insert_users_table(user_list)

    session.close()
    return result

