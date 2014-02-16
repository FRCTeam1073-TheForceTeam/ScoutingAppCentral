'''
Created on Feb 7, 2013

@author: ksthilaire
'''

import DbSession
import DataModel
import WebCommonUtils

def get_page(global_config, access_level):
    global_config['logger'].debug( 'GET Home Page' )
    
    session = DbSession.open_db_session(global_config['db_name'])
    page = ''
            
    page += '<hr>'
    
    comp = global_config['this_competition']
    
    page += '<h3>FIRST FRC Competition Data' + '</h3>'
    page += '<hr>'
    page += '<ul>'
    page += '<li><a href="/events">FRC Events List</a></li>'
    if global_config.has_key('event_code'):
        event_code = global_config['event_code']
        page += '<li><a href="/eventstandings/%s">%s Info</a></li>' % (event_code,comp)
    page += '</ul>'
    page += '<hr>'
    page += '<h3> Team Scoring Summary' + '</h3>'
    page += '<hr>'
    page += '<ul>'
    page += '<li><a href="/rankchart">Team Rankings</a></li>'
    page += '<li><a href="/recalculaterankings">Recalculate Team Rankings</a></li>'
    
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
    if team_list_str != None and team_list_str != '':
        if team_list_str.count(',') > 0:
            team_list = team_list_str.split(',')
            #team_list.sort()
            for team in team_list:
                page += '<li><a href="/teamdata/' + team + '">' + 'Team ' + team + '</a></li>'
        else:
            page += '<li><a href="/teamdata/' + team_list_str + '">' + 'Team ' + team_list_str + '</a></li>'
    else:
        comp = global_config['this_competition']
        team_list = DataModel.getTeamsInNumericOrder(session, comp)
        for entry in team_list:
            page += '<li><a href="/teamdata/' + str(entry.team) + '">' + 'Team ' + str(entry.team) + '</a></li>'
    page += '</ul>'
    return page

