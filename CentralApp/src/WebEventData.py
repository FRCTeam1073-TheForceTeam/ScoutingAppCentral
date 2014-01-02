'''
Created on March 3, 2013

@author: ksthilaire
'''

import urllib2
import json
import WebCommonUtils


def get_events_page(global_config):
        
        global_config['logger'].debug( 'GET Events Page' )

        page = ''

        url_str = 'http://thefirstalliance.org/api/api.json.php?action=list-events'
        try:
            events_data = urllib2.urlopen(url_str).read()
            events_data_dict = json.loads(events_data)
            if events_data_dict['result'] == True:
                event_list = events_data_dict['data']
                
                page += '<ul>'
                page += '<table border="1" cellspacing="5">'
            
                page += '<tr>'
                page += '<th>Event Code</th>'
                page += '<th>Name</th>'
                page += '<th>Start Date</th>'
                page += '<th>End Date</th>'
                page += '</tr>'
            
                for event in event_list:
                    page += '<tr>'
                    page += '<td><a href="/eventstandings/%s">%s</a></td>' % (event['api_name'],event['api_name'])
                    page += '<td><a href="/eventstandings/%s">%s</a></td>' % (event['api_name'],event['name'])
                    page += '<td>' + event['start_date'] + '</td>'
                    page += '<td>' + event['end_date'] + '</td>'
                    page += '</tr>'
                
                page += '</table>'
                page += '</ul>'
        except:
            pass

        page += '</body>'
        page += '</html>'
                
        return page

def get_event_standings_page(global_config, event_code):
        
        global_config['logger'].debug( 'GET Event Standings Page' )

        page = ''
            
        url_str = 'http://thefirstalliance.org/api/api.json.php?action=event-details&event-code=%s' % event_code
        try:
            event_data = urllib2.urlopen(url_str).read()
            event_data_dict = json.loads(event_data)
            if event_data_dict['result'] == True:
                event = event_data_dict['data']
                rankings = event['rankings']
            
                page += '<ul>'
                page += '<li>Name: %s</li>' % event['name']
                page += '<li>Code: %s</li>' % event['api_name']
                page += '<li>Start Date: %s</li>' % event['start_date']
                page += '<li>End Date: %s</li>' % event['end_date']
                page += '</ul>'
            
                page += '<br>'
            
                page += '<ul>'
                page += '<table border="1" cellspacing="5">'
            
                page += '<tr>'
                page += '<th>Team</th>'
                page += '<th>Rank</th>'
                page += '<th>Record (W-L-T)</th>'
                page += '<th>Played</th>'
                page += '<th>TP</th>'
                page += '<th>CP</th>'
                page += '<th>QS</th>'
                page += '<th>BP</th>'
                page += '<th>HP</th>'
                page += '<th>DQ</th>'
                page += '</tr>'
            
                for team in rankings:
                    page += '<tr>'
                    page += '<td><a href="/teamdata/%s">%s</a></td>' % (team['Team'],team['Team'])
                    page += '<td>%s</td>' % str(team['Rank'])
                    page += '<td>%s</td>' % str(team['Record (W-L-T)'])
                    page += '<td>%s</td>' % str(team['Played'])
                    page += '<td>%s</td>' % str(team['TP'])
                    page += '<td>%s</td>' % str(team['CP'])
                    page += '<td>%s</td>' % str(team['QS'])
                    page += '<td>%s</td>' % str(team['BP'])
                    page += '<td>%s</td>' % str(team['HP'])
                    page += '<td>%s</td>' % str(team['DQ'])
                    page += '</tr>'
                
                page += '</table>'
                page += '</ul>'
        except:
            pass

        page += '</body>'
        page += '</html>'
                
        return page

def getMatchResults(results, match_type):
    
    page = '<ul>'
    '''
    page += '<li>Name: %s</li>' % event['name']
    page += '<li>Code: %s</li>' % event['api_name']
    page += '<li>Start Date: %s</li>' % event['start_date']
    page += '<li>End Date: %s</li>' % event['end_date']
    '''
    
    page += '<table border="1" cellspacing="5">'
    
    page += '<tr>'
    page += '<th>Match</th>'
    page += '<th>Red #1</th>'
    page += '<th>Red #2</th>'
    page += '<th>Red #3</th>'
    page += '<th>Blue #1</th>'
    page += '<th>Blue #2</th>'
    page += '<th>Blue #3</th>'
    page += '<th>Red Score</th>'
    page += '<th>Blue Score</th>'
    page += '<th>Timestamp</th>'
    page += '<th>Match Description</th>'
    page += '</tr>'
    
    for match in results:
        if match['match_type'] == match_type:
            if match['red_score'] != None and match['blue_score'] != None:
                page += '<tr>'
                page += '<td>' + match['match_number'] + '</td>'
                page += '<td><a href="/teamdata/%s">%s</a></td>' % (match['red_1_num'],match['red_1_num'])
                page += '<td><a href="/teamdata/%s">%s</a></td>' % (match['red_2_num'],match['red_2_num'])
                page += '<td><a href="/teamdata/%s">%s</a></td>' % (match['red_3_num'],match['red_3_num'])
                page += '<td><a href="/teamdata/%s">%s</a></td>' % (match['blue_1_num'],match['blue_1_num'])
                page += '<td><a href="/teamdata/%s">%s</a></td>' % (match['blue_2_num'],match['blue_2_num'])
                page += '<td><a href="/teamdata/%s">%s</a></td>' % (match['blue_3_num'],match['blue_3_num'])
                if match['red_score'] is None:
                    page += '<td>' + '' + '</td>'
                else:
                    page += '<td>' + match['red_score'] + '</td>'
                if match['blue_score'] is None:
                    page += '<td>' + '' + '</td>'
                else:
                    page += '<td>' + match['blue_score'] + '</td>'
                page += '<td>' + match['timestamp'] + '</td>'
                if match['description'] is None:
                    page += '<td>' + '' + '</td>'
                else:
                    page += '<td>' + match['description'] + '</td>'
                page += '</tr>'
        
    page += '</table>'
    page += '</ul>'
    return page

def get_event_results_page(global_config, event_code):
        
        global_config['logger'].debug( 'GET Event Results Page' )

        page = ''

        url_str = 'http://thefirstalliance.org/api/api.json.php?action=event-matches&event-code=%s' % event_code
        try:
            event_data = urllib2.urlopen(url_str).read()
            event_data_dict = json.loads(event_data)
            if event_data_dict['result'] == True:
                results = event_data_dict['data']
            
            
                page += '<h3>Qualification Round Matches:</h3>'
                page += getMatchResults( results, '1')
                page += '<h3>Elimination Round Matches:</h3>'
                page += getMatchResults( results, '2')
            
        except:
            pass

        page += '</body>'
        page += '</html>'
                
        return page

