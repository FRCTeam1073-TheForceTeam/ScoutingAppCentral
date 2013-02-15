'''
Created on Feb 7, 2013

@author: ksthilaire
'''

import DbSession
import DataModel

def get_page(global_config):
    global_config['logger'].debug( 'GET Home Page' )
    
    session = DbSession.open_db_session(global_config['db_name'])
            
    page = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
    page += '<html>'
    page += '<head>'
    page += '<body>'
    if global_config.has_key('my_team'):
        page += '<h2> Team ' + global_config['my_team'] + ' Scouting Application Home Page' + '</h3>'
    else:
        page += '<h2> Team 1073 Scouting Application Home Page' + '</h3>'
    page += '<hr>'
    page += '<br>'
    page += '<a href="/issues"> IssueTracker</a></td>'
    page += '<br>'
    page += '<a href="/debriefs"> MatchDebriefs</a></td>'
    page += '<br>'
    page += '<br>'
    page += '<hr>'
    page += '<h3> Team Scoring Summary' + '</h3>'
    page += '<hr>'
    page += '<ul>'
    page += '<li><a href="/static/test/designer.html"> Team Rankings</a></li>'
    
    comp = global_config['this_competition']
    page += '<li><a href="/static/attr/' + comp + '.csv"> ' + comp + '.csv</a></li>'
    other_competitions = global_config['other_competitions'].split(',')
    for comp in other_competitions:
        if comp and comp != global_config['this_competition']:
            page += '<li><a href="/static/attr/' + comp + '.csv"> ' + comp + '.csv</a></li>'
    page += '</ul>'
    page += '<hr>'
    page += '<h3> Team Links' + '</h3>'
    page += '<hr>'
    page += '<ul>'
    
    team_list_str = global_config['team_list']
    if team_list_str.count(',') > 0:
        team_list = team_list_str.split(',')
        #team_list.sort()
        for team in team_list:
            page += '<li><a href="/teamdata/' + team + '">' + 'Team ' + team + '</a></li>'
    elif team_list_str != None:
        page += '<li><a href="/teamdata/' + team_list_str + '">' + 'Team ' + team_list_str + '</a></li>'
    else:
        team_list = DataModel.getTeamsInNumericOrder(session, comp)
        for entry in team_list:
            page += '<li><a href="/teamdata/' + str(entry.team) + '">' + 'Team ' + str(entry.team) + '</a></li>'
    page += '</ul>'
    page += '</body>'
    page += '</html>'
    return page

