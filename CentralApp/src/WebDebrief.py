'''
Created on Feb 7, 2013

@author: ksthilaire
'''

from web import form
import time

import DbSession
import IssueTrackerDataModel
import DebriefDataModel

match_comment_label = 'Comment:'

commentform = form.Form( 
    form.Textarea(match_comment_label, size=1024))

def get_match_comment_form(global_config, match_str):
    global_config['logger'].debug( 'GET match Comment Form, Issue: %s', match_str )

    form = commentform()

    return form

def process_match_comment_form(global_config, form, match_str, username):
    global_config['logger'].debug( 'Process Match Comment Form: %s', match_str )
    
    session = DbSession.open_db_session(global_config['debriefs_db_name'])                   
    comment = form[match_comment_label].value
    timestamp = str(int(time.time()))
    competition = global_config['this_competition']
    
    DebriefDataModel.addOrUpdateDebriefComment(session, int(match_str),
                                               competition, 
                                               username, timestamp,
                                               comment)
    session.commit()
    return '/debrief/%s' % match_str            


def get_debrief_page(global_config, match_str):
    
    session = DbSession.open_db_session(global_config['debriefs_db_name'])
    debrief = DebriefDataModel.getDebrief(session, int(match_str))
    debrief_issues = DebriefDataModel.getDebriefIssues(session, int(match_str))
    issues_session = DbSession.open_db_session(global_config['issues_db_name'])
    
    if debrief != None:
        result = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
        result += '<html>'
        result += '<head>'
        result += '<body>'
        result += '<h2> Team 1073 Debrief For Match ' + match_str + '</h3>'
        result += '<hr>'
        result += '<a href="/home"> Home</a></td>'
        result += '<hr>'
        result += '<br>'
        result += '<a href="/issues"> IssueTracker</a></td>'
        result += '<br>'
        result += '<a href="/debriefs"> Match Debriefs</a></td>'
        result += '<br>'
        result += '<br>'
        result += '<hr>'
        
        
        table_str = '<h4>Match Info</h4>'
        table_str += '<ul>'
        table_str += '<table border="1" cellspacing="5">'
        table_str += '<tr>'
        table_str += '<td>Summary</td>'
        table_str += '<td>' + debrief.summary + '</td>'
        table_str += '</tr>'
    
        table_str += '<tr>'
        table_str += '<td>Description</td>'
        table_str += '<td>' + debrief.description + '</td>'
        table_str += '</tr>'
        table_str += '</table>'
        table_str += '</ul>'
        
        table_str += '<h4>Reported Issues From Match</h4>'
        table_str += '<ul>'
        table_str += '<table border="1" cellspacing="5">'
        for issue in debrief_issues:
            table_str += '<tr>'
            table_str += '<td>' + issue.priority + '</td>'
            table_str += '<td><a href="/issue/' + str(issue.issue_id) + '">' + str(issue.issue_id) + '</a></td>'
            issue = IssueTrackerDataModel.getIssue(issues_session, issue.issue_id)
            if issue:
                table_str += '<td>' + issue.summary + '</td>'
                
            table_str += '</tr>'
        table_str += '</table>'
        table_str += '</ul>'
    
        result += table_str

        result += '<br>'
        result += '<hr>'
        result += '<a href="/debriefcomment/' + match_str + '"> Comment On This Match</a></td>'
        result += '<br>'
        result += '<hr>'
        result += '<h3>Comments</h3>'
        
        comments = DebriefDataModel.getDebriefComments(session, int(match_str))
        if len(comments) > 0:
            table_str = '<ul>'
            table_str += '<table border="1" cellspacing="5">'
            table_str += '<tr>'
            table_str += '<th>Timestamp</th>'
            table_str += '<th>Commented By</th>'
            table_str += '<th>Comment</th>'
            table_str += '</tr>'
            for comment in comments:      
                table_str += '<tr>'
                table_str += '<td>' + time.strftime('%b %d, %Y %I:%M:%S %p', time.localtime(float(comment.tag))) + '</td>'
                table_str += '<td>' + comment.submitter + '</td>'
                table_str += '<td>' + comment.data + '</td>'
                table_str += '</tr>'
            table_str += '</table>'
            table_str += '</ul>'
        
            result += table_str    
        result += '<hr>'
    
        return result
    else:
        return None
    
def insert_debrief_table(debriefs):
    table_str = '<h3>' + 'Match Debrief Summary' + '</h3>'
    table_str += '<hr>'
    table_str += '<ul>'
    
    table_str += '<table border="1" cellspacing="5">'
    
    table_str += '<tr>'
    table_str += '<th>Match</th>'
    table_str += '<th>Summary</th>'
    table_str += '<th>Description</th>'
    table_str += '</tr>'
    
    for debrief in debriefs:
        table_str += '<tr>'
        table_str += '<td><a href="/debrief/' + str(debrief.match_id) + '">' + 'Match ' + str(debrief.match_id) + '</a></td>'
        table_str += '<td>' + debrief.summary + '</td>'
        table_str += '<td>' + debrief.description + '</td>'
        table_str += '</tr>'
    table_str += '</table>'
    table_str += '</ul>'
    return table_str

def get_debriefs_home_page(global_config):
 
    session = DbSession.open_db_session(global_config['debriefs_db_name'])

    result = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
    result += '<html>'
    result += '<head>'
    result += '<body>'
    result += '<h2> Team 1073 Match Debrief Home Page' + '</h3>'
    result += '<hr>'
    result += '<a href="/home">Home</a></td>'
    result += '<hr>'
    result += '<br>'
    result += '<a href="/issues">IssueTracker</a></td>'
    result += '<br>'
    result += '<br>'
    result += '<hr>'
    
    match_debriefs = DebriefDataModel.getDebriefsInNumericOrder(session)
    result += insert_debrief_table(match_debriefs)
    
    result += '</body>'
    result += '</html>'
    return result

