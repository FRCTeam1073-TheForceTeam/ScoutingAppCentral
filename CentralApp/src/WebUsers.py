'''
Created on Feb 14, 2013

@author: ksthilaire
'''

from web import form
import time

import DbSession
import IssueTrackerDataModel

'''
# Form definition and callback class for the issue get and post operations
issue_platforms = ['', 'Robot', 'Tablet']
issue_subgroups = ['','Mechanical', 'Software', 'Electrical', 'Integration', 'Strategy', 'Business', 'Unassigned']
issue_components = ['','Drivetrain', 'Shooter', 'Collector', 'Climber', 'Strategy', 'Business', 'Unassigned']
issue_statuses = ['','Open', 'Closed', 'Working', 'Resolved']
issue_priorities = ['Low', 'High', 'Critical', 'Blocking']
issue_owners = ['','Michael Ross', 'Aaron Pepin', 'Sarah Drazin', 'Unassigned']

issue_id_label = 'Id:'
issue_summary_label ='Summary:'
issue_platform_label ='Platform:'
issue_status_label ='Status:'
issue_priority_label = 'Priority:'
issue_subgroup_label = 'Subgroup:'
issue_component_label = 'Component:'
issue_owner_label = 'Owner:'
issue_submitter_label = 'Submitter:'
issue_description_label = 'Description:'
issue_comment_label = 'Comment:'

issueform = form.Form( 
    form.Textbox(issue_id_label, size=20),
    form.Dropdown(issue_platform_label, issue_platforms),
    form.Textbox(issue_summary_label, size=60),
    form.Dropdown(issue_status_label, issue_statuses),
    form.Dropdown(issue_priority_label, issue_priorities),
    form.Dropdown(issue_subgroup_label, issue_subgroups),
    form.Dropdown(issue_component_label, issue_components),
    form.Dropdown(issue_owner_label, issue_owners),
    form.Dropdown(issue_submitter_label, issue_owners),
    form.Textarea(issue_description_label, size=1024),
    form.Textarea(issue_comment_label, size=256))

new_issueform = form.Form(                        
    form.Dropdown(issue_platform_label, issue_platforms),
    form.Textbox(issue_summary_label, size=60),
    form.Dropdown(issue_status_label, issue_statuses),
    form.Dropdown(issue_priority_label, issue_priorities),
    form.Dropdown(issue_subgroup_label, issue_subgroups),
    form.Dropdown(issue_component_label, issue_components),
    form.Dropdown(issue_owner_label, issue_owners),
    form.Dropdown(issue_submitter_label, issue_owners),
    form.Textarea(issue_description_label, size=1024),
    form.Textarea(issue_comment_label, size=256))

def get_new_issue_form(global_config):
    global_config['logger'].debug( 'GET New Issue Form' )
        
    form = new_issueform()
    return form

def process_new_issue_form(global_config, form):
    global_config['logger'].debug( 'Process New Issue Form' )
    
    session = DbSession.open_db_session(global_config['issues_db_name'])
                    
    # TODO: need to come up with a way to generate the next available issue number
    platform = form[issue_platform_label].value
    issue_id = IssueTrackerDataModel.getIssueId(session, platform)
    
    summary = form[issue_summary_label].value
    status = form[issue_status_label].value
    priority = form[issue_priority_label].value
    subgroup = form[issue_subgroup_label].value
    owner = form[issue_owner_label].value
    submitter = form[issue_submitter_label].value
    component = form[issue_component_label].value
    description = form[issue_description_label].value
    comment = form[issue_comment_label].value
    timestamp = str(int(time.time()))
    
    issue_string =  'Id:' + issue_id + '\n'
    issue_string += 'Timestamp:%s\n' % timestamp 
    issue_string += issue_platform_label + platform + '\n'
    issue_string += issue_summary_label + summary + '\n'
    issue_string += issue_status_label + status + '\n'
    issue_string += issue_priority_label + priority + '\n'
    issue_string += issue_subgroup_label + subgroup + '\n'
    issue_string += issue_component_label + component + '\n'
    issue_string += issue_owner_label + owner + '\n'
    issue_string += issue_submitter_label + submitter + '\n'
    issue_string += issue_description_label + description + '\n'
    issue_string += issue_comment_label + comment + '\n'
    
    filename = './static/Issues/Web_%s.txt' % issue_id
    fd = open(filename, 'w')
    fd.write(issue_string)
    fd.close()
    
    #TODO: Add component to the data model
    IssueTrackerDataModel.addOrUpdateIssue(session, issue_id, summary, 
                                           status, priority, subgroup, 
                                           component, submitter, owner, 
                                           description)
    IssueTrackerDataModel.addOrUpdateIssueComment(session, issue_id, 
                                                  submitter, timestamp,
                                                  comment)
    session.commit()
    
    return issue_string            

def get_issue_form(global_config, issue_id):
    global_config['logger'].debug( 'GET Issue Form, Issue: %s', issue_id )
        
    session = DbSession.open_db_session(global_config['issues_db_name'])

    issue_id = issue_id
    platform = issue_id.split('-')[0]
    issue = IssueTrackerDataModel.getIssue(session, issue_id)
    
    form = issueform()
    form[issue_id_label].value = issue_id
    form[issue_platform_label].value = platform
    form[issue_summary_label].value = issue.summary
    form[issue_status_label].value = issue.status
    form[issue_priority_label].value = issue.priority
    form[issue_subgroup_label].value = issue.subgroup
    form[issue_owner_label].value = issue.owner
    form[issue_submitter_label].value = issue.submitter
    form[issue_component_label].value = issue.component
    form[issue_description_label].value = issue.description

    return form

def process_issue_form(global_config, form, issue_id):
    global_config['logger'].debug( 'Process Issue Form Issue: %s', issue_id )
    
    session = DbSession.open_db_session(global_config['issues_db_name'])
                    
    platform = issue_id.split('-')[0]
    summary = form[issue_summary_label].value
    status = form[issue_status_label].value
    priority = form[issue_priority_label].value
    subgroup = form[issue_subgroup_label].value
    owner = form[issue_owner_label].value
    submitter = form[issue_submitter_label].value
    component = form[issue_component_label].value
    description = form[issue_description_label].value
    comment = form[issue_comment_label].value
    timestamp = str(int(time.time()))
    
    issue_string =  'Id:' + issue_id + '\n'
    issue_string += 'Timestamp:%s\n' % timestamp 
    issue_string += issue_platform_label + platform + '\n'
    issue_string += issue_summary_label + summary + '\n'
    issue_string += issue_status_label + status + '\n'
    issue_string += issue_priority_label + priority + '\n'
    issue_string += issue_subgroup_label + subgroup + '\n'
    issue_string += issue_component_label + component + '\n'
    issue_string += issue_owner_label + owner + '\n'
    issue_string += issue_submitter_label + submitter + '\n'
    issue_string += issue_description_label + description + '\n'
    issue_string += issue_comment_label + comment + '\n'
    
    filename = './static/Issues/Web_%s.txt' % issue_id
    fd = open(filename, 'w')
    fd.write(issue_string)
    fd.close()
    
    #TODO: Add platform to the data model
    IssueTrackerDataModel.addOrUpdateIssue(session, issue_id, summary, 
                                           status, priority, subgroup, 
                                           component, submitter, owner, 
                                           description)
    IssueTrackerDataModel.addOrUpdateIssueComment(session, issue_id, 
                                                  submitter, timestamp,
                                                  comment)
    session.commit()
    
    return issue_string            
'''

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
