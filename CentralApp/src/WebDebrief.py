'''
Created on Feb 7, 2013

@author: ksthilaire
'''

from web import form
from myform import pureform as pureform

import time

import DbSession
import IssueTrackerDataModel
import DebriefDataModel
import WebCommonUtils

match_comment_label = 'Comment:'

commentform = pureform( 
    form.Textarea(match_comment_label, size=1024))

def get_match_comment_form(global_config, competition, match_str):
    global_config['logger'].debug( 'GET match Comment Form, Issue: %s:%s', (competition,match_str) )

    form = commentform()

    return form

def process_match_comment_form(global_config, form, competition, match_str, username):
    global_config['logger'].debug( 'Process Match Comment Form: %s:%s', (competition,match_str) )
    
    session = DbSession.open_db_session(global_config['debriefs_db_name'])                   
    comment = form[match_comment_label].value
    timestamp = str(int(time.time()))
    
    DebriefDataModel.addOrUpdateDebriefComment(session, int(match_str),
                                               competition, 
                                               username, timestamp,
                                               comment)
    session.commit()
    return '/debrief/%s' % match_str            


def get_debrief_page(global_config, competition, match_str, allow_update=False):
    
    session = DbSession.open_db_session(global_config['debriefs_db_name'])
    debrief = DebriefDataModel.getDebrief(session, competition, int(match_str))
    debrief_issues = DebriefDataModel.getDebriefIssues(session, competition, int(match_str))
    issues_session = DbSession.open_db_session(global_config['issues_db_name'])
    
    if debrief != None:
        result = ''
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
        result += '<a href="/debriefcomment/' + competition + '/' + match_str + '"> Comment On This Match</a></td>'
        result += '<br>'
        result += '<hr>'
        result += '<h3>Comments</h3>'
        
        comments = DebriefDataModel.getDebriefComments(session, competition, int(match_str))
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
                if allow_update == True:
                    table_str += '<td><a href="/deletecomment/debrief/' + competition + '/' + match_str + '/' + comment.tag + '">Delete</a></td>'
                table_str += '</tr>'
            table_str += '</table>'
            table_str += '</ul>'
        
            result += table_str    
        result += '<hr>'
    
        return result
    else:
        return None
    
def insert_debrief_table(debriefs,competition):
    table_str = ''
    table_str += '<ul>'
    
    table_str += '<table border="1" cellspacing="5">'
    
    table_str += '<tr>'
    table_str += '<th>Match</th>'
    table_str += '<th>Summary</th>'
    table_str += '<th>Description</th>'
    table_str += '</tr>'
    
    for debrief in debriefs:
        table_str += '<tr>'
        if competition != None:
            table_str += '<td><a href="/debrief/' + competition + '/'+ str(debrief.match_id) + '">' + 'Match ' + str(debrief.match_id) + '</a></td>'
        else:
            table_str += '<td><a href="/debrief/' + str(debrief.match_id) + '">' + 'Match ' + str(debrief.match_id) + '</a></td>'
        table_str += '<td>' + debrief.summary + '</td>'
        table_str += '<td>' + debrief.description + '</td>'
        table_str += '</tr>'
    table_str += '</table>'
    table_str += '</ul>'
    return table_str

def get_debriefs_home_page(global_config, competition):
 
    session = DbSession.open_db_session(global_config['debriefs_db_name'])

    result = ''
    result += '<hr>'
    
    match_debriefs = DebriefDataModel.getDebriefsInNumericOrder(session,competition)
    result += insert_debrief_table(match_debriefs,competition)
    
    return result

def delete_comment(global_config, competition, match_str, tag):
 
    session = DbSession.open_db_session(global_config['debriefs_db_name'])
    
    DebriefDataModel.deleteDebriefCommentsByTag(session, competition, match_str, tag)
    session.commit()
    return '/debrief/%s/%s' % (competition,match_str)
