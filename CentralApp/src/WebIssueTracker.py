'''
Created on Feb 7, 2013

@author: ksthilaire
'''

from web import form
import time

import DbSession
import IssueTrackerDataModel
import WebCommonUtils

# Form definition and callback class for the issue get and post operations
issue_platforms  = ['Robot', 'MobileBase', 'Ursa', '']
issue_subgroups  = ['Unassigned','Mechanical', 'Software', 'Electrical', 'Integration', 'Strategy', 'Business' ]
issue_components = ['Unassigned','Drive_Train', 'Shooter', 'Feeder', 'Climber', 'Comms', 
                    'Autonomous','Vision', 'Dashboard', 'Inspection', 'Drive_Team', 'Strategy', 'Business']
issue_statuses   = ['Open', 'Closed', 'Working', 'Resolved']
issue_priorities = ['Priority_1', 'Priority_2', 'Priority_3', 'Priority_4', 'Priority_5', 'Priority_6']
issue_username_list = []

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
issue_last_modified_label = 'LastModified:'
issue_last_modified_by_label = 'LastModifiedBy:'

issueform = form.Form( 
    form.Textbox(issue_id_label, size=20),
    form.Dropdown(issue_platform_label, issue_platforms),
    form.Textbox(issue_summary_label, size=60),
    form.Dropdown(issue_status_label, issue_statuses),
    form.Dropdown(issue_priority_label, issue_priorities),
    form.Dropdown(issue_subgroup_label, issue_subgroups),
    form.Dropdown(issue_component_label, issue_components),
    form.Dropdown(issue_owner_label, issue_username_list),
    form.Dropdown(issue_submitter_label, issue_username_list),
    form.Textarea(issue_description_label, size=1024),
    form.Textarea(issue_comment_label, size=1024))

new_issueform = form.Form(                        
    form.Dropdown(issue_platform_label, issue_platforms),
    form.Textbox(issue_summary_label, size=60),
    form.Dropdown(issue_status_label, issue_statuses),
    form.Dropdown(issue_priority_label, issue_priorities),
    form.Dropdown(issue_subgroup_label, issue_subgroups),
    form.Dropdown(issue_component_label, issue_components),
    form.Dropdown(issue_owner_label, issue_username_list),
    form.Dropdown(issue_submitter_label, issue_username_list),
    form.Textarea(issue_description_label, size=1024))

commentform = form.Form( 
    form.Textarea(issue_comment_label, size=1024))

def get_new_issue_form(global_config, platform_type=None):
    global_config['logger'].debug( 'GET New Issue Form' )
        
    session = DbSession.open_db_session(global_config['issues_db_name'])

    form = new_issueform()

    # apply the valid list of user names to the dropdown 
    # for the owner field and the submitter field
    username_list = IssueTrackerDataModel.getDisplayNameList(session)
    form[issue_owner_label].args = username_list
    form[issue_submitter_label].args = username_list
    
    # if the platform type is specified, then constrain the platform to that value
    if platform_type != None:
        form[issue_platform_label].args = [ platform_type ]

    # TODO: can also extract the subgroup and taskgroup(component) lists from the 
    #       database and override the form with the contents
    #       IssueTrackerDataModel.getSubgroupList() and getTaskgroupList()
    
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

    #TODO: Add component to the data model
    issue = IssueTrackerDataModel.addOrUpdateIssue(session, issue_id, summary, 
                                           status, priority, subgroup, 
                                           component, submitter, owner, 
                                           description, timestamp)
    if issue != None:
        issue.create_file('./static/%s/ScoutingData' % global_config['this_competition'])
    session.commit()
    
    return '/issue/%s' % issue_id            


'''
    IssueTrackerDataModel.addOrUpdateIssueComment(session, issue_id, 
                                                  submitter, timestamp,
                                                  comment)
'''

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
    
    # TODO: can also extract the subgroup and taskgroup(component) lists from the 
    #       database and override the form with the contents
    #       IssueTrackerDataModel.getSubgroupList() and getTaskgroupList()
    form[issue_subgroup_label].value = issue.subgroup
    form[issue_component_label].value = issue.component
    
    # apply the valid list of user names to the dropdown 
    # for the owner field and the submitter field
    username_list = IssueTrackerDataModel.getDisplayNameList(session)
    form[issue_owner_label].args = username_list
    form[issue_submitter_label].args = username_list

    form[issue_owner_label].value = issue.owner
    form[issue_submitter_label].value = issue.submitter
    form[issue_description_label].value = issue.description

    return form

def process_issue_form(global_config, form, issue_id, username):
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
    
    #TODO: Add platform to the data model
    issue = IssueTrackerDataModel.addOrUpdateIssue(session, issue_id, summary, 
                                           status, priority, subgroup, 
                                           component, submitter, owner, 
                                           description, timestamp)
    if issue != None:
        issue.create_file('./static/%s/ScoutingData' % global_config['this_competition'])

    if comment != '':
        IssueTrackerDataModel.addOrUpdateIssueComment(session, issue_id, 
                                                      username, timestamp,
                                                      comment)
    session.commit()
    
    return '/issue/%s' % issue_id            

def get_issue_comment_form(global_config, issue_id):
    global_config['logger'].debug( 'GET Issue Comment Form, Issue: %s', issue_id )

    issue_id = issue_id
    form = commentform()

    return form

def process_issue_comment_form(global_config, form, issue_id, username):
    global_config['logger'].debug( 'Process Issue Comment Form: %s', issue_id )
    
    session = DbSession.open_db_session(global_config['issues_db_name'])                   
    comment = form[issue_comment_label].value
    timestamp = str(int(time.time()))

    if comment != '':    
        IssueTrackerDataModel.addOrUpdateIssueComment(session, issue_id, 
                                                      username, timestamp,
                                                      comment)
        session.commit()
    return '/issue/%s' % issue_id            

def get_issue_page(global_config, issue_id, allow_update=False):
    session = DbSession.open_db_session(global_config['issues_db_name'])
    issue = IssueTrackerDataModel.getIssue(session, issue_id)
    if issue:
        result = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
        result += '<html>'
        result += WebCommonUtils.get_html_head('FIRST Team 1073 - Issue %s' % issue_id)
        result += '<body>'
        result += '<h2> Team 1073 Issue ' + issue_id + '</h2>'
        result += '<hr>'
        result += '<a href="/home">Home</a></td>'
        result += '<br>'
        result += '<a href="/issues/%s">Back</a></td>' % issue_id.split('-')[0]
        result += '<hr>'
        result += '<br>'
        result += '<a href="/issues">IssueTracker</a></td>'
        result += '<br>'
        result += '<a href="/debriefs">Match Debriefs</a></td>'
        result += '<br>'
        result += '<br>'
        result += '<hr>'
    
        table_str = '<ul>'
        table_str += '<table border="1" cellspacing="5">'
        
        table_str += '<tr>'
        table_str += '<td>' + issue_id_label + '</td>'
        table_str += '<td>' + issue.issue_id + '</td>'
        table_str += '</tr>'
        table_str += '<tr>'
        table_str += '<td>' + issue_summary_label + '</td>'
        table_str += '<td>' + issue.summary + '</td>'
        table_str += '</tr>'
        table_str += '<tr>'
        table_str += '<td>' + issue_status_label + '</td>'
        table_str += '<td>' + issue.status + '</td>'
        table_str += '</tr>'
        table_str += '<tr>'
        table_str += '<td>' + issue_priority_label + '</td>'
        table_str += '<td>' + issue.priority + '</td>'
        table_str += '</tr>'
        table_str += '<tr>'
        table_str += '<td>' + issue_subgroup_label + '</td>'
        table_str += '<td>' + issue.subgroup + '</td>'
        table_str += '</tr>'
        table_str += '<tr>'
        table_str += '<td>' + issue_component_label + '</td>'
        table_str += '<td>' + issue.component + '</td>'
        table_str += '</tr>'
        table_str += '<tr>'
        table_str += '<td>' + issue_owner_label + '</td>'
        table_str += '<td>' + issue.owner + '</td>'
        table_str += '</tr>'
        table_str += '<tr>'
        table_str += '<td>' + issue_submitter_label + '</td>'
        table_str += '<td>' + issue.submitter + '</td>'
        table_str += '</tr>'
        table_str += '<tr>'
        table_str += '<td>' + issue_description_label + '</td>'
        table_str += '<td>' + issue.description + '</td>'
        table_str += '</tr>'
        table_str += '<tr>'
        table_str += '<td>' + issue_last_modified_label + '</td>'
        table_str += '<td>' + time.strftime('%b %d, %Y %I:%M:%S %p', time.localtime(float(issue.timestamp))) + '</td>'
        #table_str += '<td>' + time.strftime('%c', time.localtime(float(issue.timestamp))) + '</td>'
        table_str += '</tr>'
    
        if issue.debrief_key != None:
            match_str = issue.debrief_key.split('_')[0]           
            table_str += '<td>' + 'Reported In:' + '</td>'
            table_str += '<td><a href="/debrief/' + match_str + '">' + 'Match ' + match_str + '</a></td>'
            table_str += '</tr>'

        table_str += '</table>'
        table_str += '</ul>'
        result += table_str
        
        # result += '<br>'
        result += '<hr>'
        
        if global_config['issues_db_master'] == 'Yes' and allow_update == True:
            result += '<a href="/issueupdate/' + issue_id + '"> Update This Issue</a>'
            result += '<br>'
        result += '<a href="/issuecomment/' + issue_id + '"> Comment On This Issue</a>'
        result += '<br>'
        result += '<hr>'
        result += '<h3>Comments</h3>'
        
        comments = IssueTrackerDataModel.getIssueComments(session, issue_id)
        if len(comments) > 0:
            table_str = '<ul>'
            table_str += '<table border="1" cellspacing="5">'
            table_str += '<tr>'
            table_str += '<th>Timestamp</th>'
            table_str += '<th>Commented By</th>'
            table_str += '<th>Comment</th>'
            if allow_update == True:
                table_str += '<th>Delete</th>'
            table_str += '</tr>'
            for comment in comments:      
                table_str += '<tr>'
                table_str += '<td>' + time.strftime('%b %d, %Y %I:%M:%S %p', time.localtime(float(comment.tag))) + '</td>'
                table_str += '<td>' + comment.submitter + '</td>'
                table_str += '<td>' + comment.data + '</td>'
                if global_config['issues_db_master'] == 'Yes' and allow_update == True:
                    table_str += '<td><a href="/deletecomment/issue/' + issue_id + '/' + comment.tag + '">Delete</a></td>'

                table_str += '</tr>'
            table_str += '</table>'
            table_str += '</ul>'
        
            result += table_str   
        result += '<hr>'
      
        return result    
    else:
        return None
    
def get_issue_json(global_config, issue_id, allow_update=False):
    session = DbSession.open_db_session(global_config['issues_db_name'])
    issue = IssueTrackerDataModel.getIssue(session, issue_id)
    if issue:
        return issue.json()
    else:
        return None

def insert_issues_table(heading, issues):
        table_str = '<h3>' + heading + ' Issues Summary' + '</h3>'
        table_str += '<hr>'
        table_str += '<ul>'
        
        #table_str += '<table border="1" cellspacing="5">'
        table_str += '<script type="text/javascript" charset="utf-8">'
        table_str += '    $(document).ready(function() {'
        table_str += '        $(\'#%s\').dataTable();' % heading
        table_str += '    } );'
        table_str += '</script>'

        table_str += '<table cellpadding="0" cellspacing="0" border="1" class="display" id="' + heading + '" width="100%">'
        table_str += '<thead>'
        table_str += '<tr>'
        table_str += '<th>Issue Id</th>'
        table_str += '<th>Priority</th>'
        table_str += '<th>Owner</th>'
        table_str += '<th>Status</th>'
        table_str += '<th>' + 'Reported In' + '</th>'
        table_str += '<th>Task Group</th>'
        table_str += '<th>Summary</th>'
        table_str += '</tr>'
        table_str += '</thead>'

        table_str += '<tbody>'
        for issue in issues:
            table_str += '<tr>'
            table_str += '<td><a href="/issue/' + issue.issue_id + '"> ' + issue.issue_id + '</a></td>'
            table_str += '<td>' + issue.priority + '</td>'
            table_str += '<td>' + issue.owner + '</td>'
            table_str += '<td>' + issue.status + '</td>'
            if issue.debrief_key != None:
                match_str = issue.debrief_key.split('_')[0]           
                table_str += '<td><a href="/debrief/' + match_str + '">' + 'Match ' + match_str + '</a></td>'
            else:
                table_str += '<td> </td>'
            table_str += '<td>' + issue.component + '</td>'
            table_str += '<td>' + issue.summary + '</td>'
            table_str += '</tr>'
        table_str += '</tbody>'
        table_str += '</table>'
        table_str += '</ul>'
        return table_str

def get_issues_home_page(global_config, allow_create=False):
 
    session = DbSession.open_db_session(global_config['issues_db_name'])

    result = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
    result += '<html>'
    result += WebCommonUtils.get_html_head('FIRST Team 1073 - Issue Tracker Home')
    result += '<body>'
    result += '<h2> Team 1073 Issues Home Page' + '</h2>'
    result += '<hr>'
    result += '<a href="/home">Home</a>'
    result += '<br>'
    result += '<a href="/home">Back</a>'
    result += '<br>'
    result += '<a href="/debriefs"> MatchDebriefs</a></td>'
    result += '<br>'
    result += '<hr>'

    result += '<h3> Platforms' + '</h3>'
    issue_types = IssueTrackerDataModel.getIssueTypes(session)
    for platform in issue_types:
        result += '<a href="/issues/%s">%s</a>' % (platform.issue_type,platform.issue_type)
        result += '<br>'
    result += '<hr>'
    
    if global_config['issues_db_master'] == 'Yes' and allow_create == True:
        result += '<a href="/newissue"> Create New Issue</a></td>'
        result += '<br>'
    result += '<hr>'
    
    
    result += '</body>'
    result += '</html>'
    return result


def get_platform_issues_home_page(global_config, platform_type, allow_create=False):
 
    session = DbSession.open_db_session(global_config['issues_db_name'])

    result = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
    result += '<html>'
    result += WebCommonUtils.get_html_head('FIRST Team 1073 - %s Issues' % platform_type)
    result += '<body>'
    result += '<h2> Team 1073 %s Issues</h3>' % platform_type
    result += '<hr>'
    result += '<a href="/home"> Home</a>'
    result += '<br>'
    result += '<a href="/issues"> Back</a>'
    result += '<hr>'
    result += '<br>'
    result += '<a href="/debriefs"> MatchDebriefs</a></td>'
    result += '<br>'
    if global_config['issues_db_master'] == 'Yes' and allow_create == True:
        result += '<a href="/newissue/%s"> Create New Issue</a></td>' % platform_type
        result += '<br>'
    result += '<br>'
    result += '<hr>'
    
    #open_issues = IssueTrackerDataModel.getIssuesByPlatform(session, platform_type)
    open_issues = IssueTrackerDataModel.getIssuesByPlatformAndMultipleStatus(session, platform_type, 'Open', 'Working', 
                                                                             order_by_priority=True)
    result += insert_issues_table('Open', open_issues)

    result += '<br>'
    result += '<hr>'
    
    closed_issues = IssueTrackerDataModel.getIssuesByPlatformAndMultipleStatus(session, platform_type, 'Closed', 'Resolved')
    result += insert_issues_table('Closed', closed_issues)

    result += '</body>'
    result += '</html>'
    return result

def delete_comment(global_config, issue_id, tag):
 
    session = DbSession.open_db_session(global_config['issues_db_name'])
    
    IssueTrackerDataModel.deleteIssueCommentsByTag(session, issue_id, tag)
    session.commit()
    return '/issue/%s' % issue_id
