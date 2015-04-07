'''
Created on March 3, 2013

@author: ksthilaire
'''

import time
import urllib2
import json
import datetime
import web
import WebCommonUtils
import FileSync
import WebTeamData
import CompAlias

from BeautifulSoup import BeautifulSoup
import re
from BeautifulSoup import NavigableString


class ParserBase(object):
    """
    Provides a basic structure for parsing pages.
    Parsers are not allowed to return Model objects, only dictionaries.
    """

    @classmethod
    def parse(self, html):
            """
            Must implement a parse function for each derived class.
            """
            raise 'NOT Implemted!!!'

    @classmethod
    def _recurseUntilString(self, node):
        """
        Digs through HTML that Word made worse.
        Written to deal with http://www2.usfirst.org/2011comp/Events/cmp/matchresults.html
        """
        if node.string is not None:
            return re.sub('\s+', ' ', node.string.replace(u'\xa0', ' ')).strip()  # remove multiple whitespaces
        if isinstance(node, NavigableString):
            return node
        if hasattr(node, 'contents'):
            results = []
            for content in node.contents:
                result = self._recurseUntilString(content)
                if result is not None:
                    result = result.strip().replace('\r', '').replace('\n', '').replace('  ', ' ')
                if result is not None and result != "":
                    results.append(result)
            if results != []:
                return ' '.join(results)
        return None

class RankParser(ParserBase):

    @classmethod
    def parse(self, html, table_index):
            """
            Parse the rankings from USFIRST.
            """
            soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    
            parsed_table = []
            tables = soup.findAll('table')
            table = tables[table_index]
    
            for tr in table.findAll('tr'):
                tds = tr.findAll('td')
                if len(tds) > 1:
                    row = []
                    for td in tds:
                        row.append(str(self._recurseUntilString(td)))
                    parsed_table.append(row)
                    
            return parsed_table, False




def get_events_page(global_config, year):
        
        global_config['logger'].debug( 'GET Events Page' )

        page = ''

        page += '\n<script type="text/javascript" charset="utf-8">\n'
        page += '    $(document).ready(function() {\n'
        page += '        var otable = $(\'#%s\').dataTable({"iDisplayLength": 100});\n' % 'events'
        page += '        otable.fnSort( [ [2,\'asc\'] ]);\n'
        page += '    } );\n'
        page += '</script>\n'
        
        url_str = 'http://www.thebluealliance.com/api/v2/events/%s?X-TBA-App-Id=frc1073:scouting-system:v01' % year
        try:
            events = urllib2.urlopen(url_str).read()
            event_data_list = json.loads(events)
            
            page += '<ul>'
            page += '<table cellpadding="0" cellspacing="0" border="1" class="display" id="events" width="100%">'
            
            page += '<thead>'
            page += '<tr>'
            page += '<th>Event Code</th>'
            page += '<th>Name</th>'
            page += '<th>Start Date</th>'
            page += '<th>End Date</th>'
            page += '</tr>'
            page += '</thead>'
            page += '<tbody>'
            
            for event in event_data_list:
                event_code = event['key'][4:].upper()
                                
                page += '<tr>'
                page += '<td><a href="/eventstandings/%s">%s</a></td>' % (event['key'],event_code)
                page += '<td><a href="/eventstandings/%s">%s</a></td>' % (event['key'],event['name'])
                page += '<td>' + event['start_date'] + '</td>'
                page += '<td>' + event['end_date'] + '</td>'
                page += '</tr>'
            
            page += '</tbody>'    
            page += '</table>'
            page += '</ul>'
        except:
            pass

       
        page += '</body>'
        page += '</html>'
                
        return page




def get_event_standings_page(global_config, year, event_code):
        
        global_config['logger'].debug( 'GET Event Standings Page' )

        page = ''
            
        url_str = 'http://www.thebluealliance.com/api/v2/event/%s%s?X-TBA-App-Id=frc1073:scouting-system:v01' % (year,event_code.lower())
        try:
            event_data = urllib2.urlopen(url_str).read()
            event_data = json.loads(event_data)
                        
            page += '<ul>'
            page += '<li>Name: %s</li>' % event_data['name']
            page += '<li>Code: %s</li>' % event_data['event_code'].upper()
            page += '<li>Start Date: %s</li>' % event_data['start_date']
            page += '<li>End Date: %s</li>' % event_data['end_date']
            page += '<li>Location: %s</li>' % event_data['location']
            page += '</ul>'
            
            page += '<br>'
            page += '<a href="/eventresults/%s%s">Match Results</a>' % (year,event_code)
            page += '<br>'
            page += '<br>'

            try:        

                page += '\n<script type="text/javascript" charset="utf-8">\n'
                page += '    $(document).ready(function() {\n'
                page += '        var otable = $(\'#%s\').dataTable({"iDisplayLength": 100});\n' % event_code
                page += '        otable.fnSort( [ [0,\'asc\'] ]);\n'
                page += '    } );\n'
                page += '</script>\n'
        
                page += '<table cellpadding="0" cellspacing="0" border="1" class="display" id="' + event_code + '" width="100%">'
                        
                first_url_str = 'http://www2.usfirst.org/%scomp/events/%s/rankings.html' % (year,event_code.upper())
                rank_data = urllib2.urlopen(first_url_str).read()
                
                my_parser = RankParser()
                rankings, _ = my_parser.parse( rank_data, 2 )
                
                first_line = True
                team_column = 0
                for line in rankings:
                    if first_line:
                        index = 0
                        first_line = False
                        page += '<thead>'
                        page += '<tr>'
                        for column in line:
                            page += '<th>%s</th>' % column
                            if column == 'Team':
                                team_column = index
                            index += 1
                        page += '</tr>'
                        page += '</thead>'
                        page += '<tbody>'
                    else:
                        index = 0
                        page += '<tr>'
                        for column in line:
                            if index == team_column:
                                page += '<td><a href="/teamdata/%s">%s</a></td>' % (column,column)
                            else:
                                page += '<td>%s</td>' % column
                            index += 1
                        page += '</tr>'
                page += '</tbody>'
                    
                page += '</table>'
            except:
                page += 'No Results At This Time'
        except:
            pass


        
        page += '</body>'
        page += '</html>'
                
        return page

def insert_results_table(rank_data, event_code, table_index):
    table_id = '%s%d' % (event_code,table_index)          
    page = '\n<script type="text/javascript" charset="utf-8">\n'
    page += '    $(document).ready(function() {\n'
    page += '        var otable = $(\'#%s\').dataTable({"iDisplayLength": 100});\n' % table_id
    page += '        otable.fnSort( [ [1,\'asc\'] ]);\n'
    page += '    } );\n'
    page += '</script>\n'

    page += '<table cellpadding="0" cellspacing="0" border="1" class="display" id="' + table_id + '" width="100%">'
            
    my_parser = RankParser()
    rankings, _ = my_parser.parse( rank_data, table_index )
    
    first_line = True
    for line in rankings:
        if first_line:
            first_line = False
            page += '<thead>'
            page += '<tr>'
            for column in line:
                page += '<th>%s</th>' % column
            page += '</tr>'
            page += '</thead>'
            page += '<tbody>'
        else:
            index = 0
            page += '<tr>'
            for column in line:
                if index > 1 and index < 8:
                    page += '<td><a href="/teamdata/%s">%s</a></td>' % (column,column)
                else:
                    page += '<td>%s</td>' % column
                index += 1
            page += '</tr>'
    page += '</tbody>'
        
    page += '</table>'
    return page
   
def get_event_results_page(global_config, year, event_code):
        
        global_config['logger'].debug( 'GET Event Standings Page' )

        page = ''
            
        url_str = 'http://www.thebluealliance.com/api/v2/event/%s%s?X-TBA-App-Id=frc1073:scouting-system:v01' % (year,event_code.lower())
        try:
            event_data = urllib2.urlopen(url_str).read()
            event_data = json.loads(event_data)
                        
            page += '<ul>'
            page += '<li>Name: %s</li>' % event_data['name']
            page += '<li>Code: %s</li>' % event_data['event_code'].upper()
            page += '<li>Start Date: %s</li>' % event_data['start_date']
            page += '<li>End Date: %s</li>' % event_data['end_date']
            page += '<li>Location: %s</li>' % event_data['location']
            page += '</ul>'
            
            page += '<br>'
            page += '<a href="/eventstandings/%s%s">Rankings</a>' % (year,event_code)
            page += '<br>'

            try:        
                first_url_str = 'http://www2.usfirst.org/%scomp/events/%s/matchresults.html' % (year,event_code.upper())
                rank_data = urllib2.urlopen(first_url_str).read()
                
                page += '<br>Qualification Round Match Results<br><br>'
                page += insert_results_table(rank_data, event_code, 2)
                page += '<br>'
                page += '<br>'
                page += '<br>Elimination Round Match Results<br><br>'
                page += insert_results_table(rank_data, event_code, 3)
                
            except:
                page += 'No Results At This Time'
        except:
            pass
        
        page += '</body>'
        page += '</html>'
                
        return page

def get_district_events_json(global_config, year, type):
        
        global_config['logger'].debug( 'GET District Event Info Json' )    
        
        url_str = 'http://www.thebluealliance.com/api/v2/district/%s/%s/events?X-TBA-App-Id=frc1073:scouting-system:v02' % (type.lower(),year)
        try:
            event_data = urllib2.urlopen(url_str).read()
            if type != None:
                event_json = json.loads(event_data)
                result = []
                result.append('[')
                for event in event_json:
                    result.append(json.dumps(event))
                    result.append(',')
                if result[-1] == ',':
                    result = result[:-1]
                result.append(']\n')
                event_data = ''.join(result)
        except:
            event_data = ''
            pass
        return event_data

def get_district_rankings_json(global_config, year, type):
        
        global_config['logger'].debug( 'GET District Rankings Json' )
        
        competition = global_config['this_competition']+year
        
        url_str = 'http://www.thebluealliance.com/api/v2/district/%s/%s/rankings?X-TBA-App-Id=frc1073:scouting-system:v02' % (type.lower(),year)

        result = []
        result.append('{ "district" : "%s",\n' % (type.upper()))

        try:
            rankings_data = urllib2.urlopen(url_str).read()
            rankings_json = json.loads(rankings_data)
       
            # rankings is now a list of lists, with the first element of the list being the list of column headings
            # take the list of columngs and apply to each of the subsequent rows to build the json response
            result.append('  "last_updated": "%s",\n' % time.strftime('%c'))
            headings = [ 'Rank', 'Points', 'Team', 'Event 1', 'Event 2', 'Age Points' ]
    
            result.append('  "columns" : [\n')

            for heading in headings:
                result.append('    { "sTitle": "%s" }' % heading)
                result.append(',\n')
            if len(headings)>0:
                result = result[:-1]
            result.append(' ],\n')
            result.append('  "rankings" : [\n')

            for team_rank in rankings_json:
                result.append('       [ ')
                result.append( '"%s", ' % str(team_rank['rank']) )
                result.append( '"%s", ' % str(team_rank['point_total']) )
                result.append( '"%s", ' % get_team_hyperlink( competition, str(team_rank['team_key']).lstrip('frc') ) )
                                                            
                for event, totals in team_rank['event_points'].iteritems():
                    result.append( '"%s", ' % str(totals['total']) )
                    
                if len(team_rank['event_points']) == 1:
                    result.append( '"-", ' )
                elif len(team_rank['event_points']) == 0:
                    result.append( '"-", "-", ' )
                    
                result.append( '"%s" ' % str(team_rank['rookie_bonus']) )
                result.append('],\n')

            if result[-1] == '],\n':
                result = result[:-1]
            result.append(']\n')
            result.append('] }\n')
            rank_data = ''.join(result)
        except:
            rank_data = ''
            pass
        return rank_data

def get_events_json(global_config, year, type=None):
        
        global_config['logger'].debug( 'GET Event Info Json' )    
        
        url_str = 'http://www.thebluealliance.com/api/v2/events/%s?X-TBA-App-Id=frc1073:scouting-system:v01' % year
        try:
            event_data = urllib2.urlopen(url_str).read()
            if type != None:
                event_json = json.loads(event_data)
                result = []
                result.append('[')
                for event in event_json:
                    event_name = event['name']
                    event_type_words = type.split(' ')
                    type_match = False
                    for word in event_type_words:
                        if event_name.find(word) != -1:
                            type_match = True
                        else:
                            type_match = False
                            break
                    if type_match == True:
                        result.append(json.dumps(event))
                        result.append(',')
                if result[-1] == ',':
                    result = result[:-1]
                result.append(']\n')
                event_data = ''.join(result)
        except:
            event_data = ''
            pass
        return event_data

def get_event_data_from_tba( query_str ):
    
    url_str = 'http://www.thebluealliance.com/api/v2/event/%s?X-TBA-App-Id=frc1073:scouting-system:v01' % (query_str)
    try:
        event_data = urllib2.urlopen(url_str).read()
        if event_data == 'null':
            event_data = ''
    except:
        event_data = ''
        pass
    return event_data


def get_event_info_json(global_config, year, event_code):
        
        global_config['logger'].debug( 'GET Event Info Json' )
            
        return get_event_data_from_tba( '%s%s' % (year,event_code.lower()) )

def get_event_info_dict(global_config, year, event_code):
        
        global_config['logger'].debug( 'GET Event Info Json' )
                    
        event_data = get_event_data_from_tba( '%s%s' % (year,event_code.lower()) )
        if event_data != '':
            event_data = json.loads(event_data)
        else:
            event_data = None
        return event_data
        
def get_event_standings_json(global_config, year, event_code):
        
    global_config['logger'].debug( 'GET Event Rankings Json' )
    
    # derive our competition name from the FIRST event code 
    competition = WebCommonUtils.map_event_code_to_comp(year+event_code)

    #return get_data_from_first(global_config, year, event_code, 'rankings')
    store_data_to_file = False
    result = []
    
    rankings = ''
    json_data = get_event_data_from_tba( '%s%s/rankings' % (year,event_code.lower()) )
    if json_data != '':
        rankings = json.loads(json_data)

    result.append('{ "event" : "%s",\n' % (event_code.lower()))
    
    if rankings:
        # rankings is now a list of lists, with the first element of the list being the list of column headings
        # take the list of columngs and apply to each of the subsequent rows to build the json response
        result.append('  "last_updated": "%s",\n' % time.strftime('%c'))
        headings = rankings[0]
        result.append('  "columns" : [\n')

        for heading in headings:
            result.append('    { "sTitle": "%s" }' % heading)
            result.append(',\n')
        if len(headings)>0:
            result = result[:-1]
        result.append(' ],\n')
        result.append('  "rankings" : [\n')
        
        for line in rankings[1:]:
            result.append('       [ ')
            for i in range(0,len(headings)):
                if need_team_hyperlink(headings[i]):
                    #result.append('"%s"' % (line[i]))
                    result.append(('"<a href=\\"/teamdata/%s/'% competition)+str(line[i])+'\\">'+str(line[i])+'</a>"')
                else:
                    #result.append('"%s": "%s"' % (headings[i].title(),line[i]))
                    result.append('"%s"' % (str(line[i])))
                    
                result.append(', ')
            if len(line) > 0:         
                result = result[:-1]
            result.append(' ],\n')
                
        if len(rankings) > 1:         
            result = result[:-1]
        result.append(' ]\n')
        store_data_to_file = True
        result.append(' ]\n')        
    else:
        # we were not able to retrieve the data from FIRST, so let's return any stored file with the 
        # information, otherwise we will return an empty json payload
        stored_file_data = FileSync.get( global_config, '%s/EventData/rankings.json' % (competition) )
        if stored_file_data != '':
            return stored_file_data
        else:
            # no stored data either, so let's just return a formatted, but empty payload
            result.append('  "last_updated": "%s",\n' % time.strftime('%c'))
            result.append('  "columns" : [],\n')
            result.append('  "rankings" : []\n')        

    result.append(' }\n')
    json_str = ''.join(result)
    if store_data_to_file:
        try:
            FileSync.put( global_config, '%s/EventData/rankings.json' % (competition), 'text', json_str)
        except:
            raise
    return json_str
              
def get_event_rank_list_json(global_config, year, event_code):
        
    global_config['logger'].debug( 'GET Event Rank List Json' )
    
    # derive our competition name from the FIRST event code 
    competition = WebCommonUtils.map_event_code_to_comp(year+event_code)

    #return get_data_from_first(global_config, year, event_code, 'rankings')
    store_data_to_file = False
    result = []
    
    rankings = ''
    json_data = get_event_data_from_tba( '%s%s/rankings' % (year,event_code.lower()) )
    if json_data != '':
        rankings = json.loads(json_data)

    result.append('{ "event" : "%s",\n' % (event_code.lower()))
    
    if rankings:
        # rankings is now a list of lists, with the first element of the list being the list of column headings
        # take the list of columngs and apply to each of the subsequent rows to build the json response
        result.append('  "last_updated": "%s",\n' % time.strftime('%c'))
        result.append('  "rankings" : [\n')
        
        for line in rankings[1:]:
            result.append('       { "rank": %d, "team_number": %d, "status": "available" }' % (line[0],line[1]))
            result.append(',\n')
                
        if len(rankings) > 1:         
            result = result[:-1]
        result.append(' ]\n')
        store_data_to_file = True
    else:
        # we were not able to retrieve the data from FIRST, so let's return any stored file with the 
        # information, otherwise we will return an empty json payload
        stored_file_data = FileSync.get( global_config, '%s/EventData/ranklist.json' % (competition) )
        if stored_file_data != '':
            return stored_file_data
        else:
            # no stored data either, so let's just return a formatted, but empty payload
            result.append('  "last_updated": "%s",\n' % time.strftime('%c'))
            result.append('  "rankings" : []\n')        

    result.append(' }\n')
    json_str = ''.join(result)
    if store_data_to_file:
        try:
            FileSync.put( global_config, '%s/EventData/ranklist.json' % (competition), 'text', json_str)
        except:
            raise
    return json_str



def get_event_matchresults_json(global_config, year, event_code, round_str, team_str = None):
        
    global_config['logger'].debug( 'GET Event Results Json' )

    if round_str == 'qual':
        match_selector = 'qm'
    elif round_str == 'quarters':
        match_selector = 'qf'
    elif round_str == 'semis':
        match_selector = 'sf'
    elif round_str == 'finals':
        match_selector = 'f'
        
    # derive our competition name from the FIRST event code 
    competition = WebCommonUtils.map_event_code_to_comp(year+event_code)

    store_data_to_file = False
    result = []
    
    result.append('{ "event" : "%s",\n' % (event_code.lower()))
    
    event_matches = ''
    if team_str is None:
        exp_filename = ''
        json_data = get_event_data_from_tba( '%s%s/matches' % (year,event_code.lower()) )
    else:
        exp_filename = '_%s' % team_str
        json_data = WebTeamData.get_team_data_from_tba( team_str, 'event/%s%s/matches' % (year,event_code.lower()) )
        
    if json_data != '':
        event_matches = json.loads(json_data)

        # rankings is now a list of lists, with the first element of the list being the list of column headings
        # take the list of columngs and apply to each of the subsequent rows to build the json response
        result.append('  "last_updated": "%s",\n' % time.strftime('%c'))
        headings = [ 'Match', 'Start Time', 'Red 1', 'Red 2', 'Red 3', 'Blue 1', 'Blue 2', 'Blue 3', 'Red Score', 'Blue Score' ]
        
        result.append('  "columns" : [\n')

        for heading in headings:
            result.append('    { "sTitle": "%s" }' % heading)
            result.append(',\n')
        if len(headings)>0:
            result = result[:-1]
        result.append(' ],\n')
        result.append('  "matchresults" : [\n')
    
        # the entire match set is returned from TBA, filter out the matches for the desired round
        for match in event_matches:
            
            if str(match['comp_level']) == match_selector:
                result.append('       [ ')
                
                # Match number
                result.append( '"%s", ' % str(match['match_number']) )

                # Match start time
                match_epoch_time = int(match['time'])
                time_format_str = '%a %b %d - %I:%M %p'
                match_time_str = datetime.datetime.fromtimestamp(match_epoch_time).strftime(time_format_str)
                result.append( '"%s", ' % match_time_str )
                
                # Red alliance teams
                result.append( '"%s", ' % get_team_hyperlink( competition, str(match['alliances']['red']['teams'][0]).lstrip('frc') ) )
                result.append( '"%s", ' % get_team_hyperlink( competition, str(match['alliances']['red']['teams'][1]).lstrip('frc') ) )
                result.append( '"%s", ' % get_team_hyperlink( competition, str(match['alliances']['red']['teams'][2]).lstrip('frc') ) )
                
                # Blue alliance teams
                result.append( '"%s", ' % get_team_hyperlink( competition, str(match['alliances']['blue']['teams'][0]).lstrip('frc') ) )
                result.append( '"%s", ' % get_team_hyperlink( competition, str(match['alliances']['blue']['teams'][1]).lstrip('frc') ) )
                result.append( '"%s", ' % get_team_hyperlink( competition, str(match['alliances']['blue']['teams'][2]).lstrip('frc') ) )
                
                # Red alliance score
                
                score = str(match['alliances']['red']['score'])
                if score == '-1':
                    score = '-'
                result.append( '"%s", ' % score )
                
                # Blue alliance score
                score = str(match['alliances']['blue']['score'])
                if score == '-1':
                    score = '-'
                result.append( '"%s" ' % score )
                
                
                result.append(' ],\n')
                store_data_to_file = True

        if store_data_to_file is True:
            result = result[:-1]
            result.append(' ]\n')
            
        result.append(' ]\n')

    else:
        # we were not able to retrieve the data from FIRST, so let's return any stored file with the 
        # information, otherwise we will return an empty json payload
        stored_file_data = FileSync.get( global_config, '%s/EventData/matchresults_%s%s.json' % (competition,round_str,exp_filename) )
        if stored_file_data != '':
            return stored_file_data
    
    result.append(' }\n')
    json_str = ''.join(result)
    if store_data_to_file:
        try:
            FileSync.put( global_config, '%s/EventData/matchresults_%s%s.json' % (competition,round_str,exp_filename), 'text', json_str)
        except:
            raise
    return json_str    
    #return get_data_from_first(global_config, year, event_code, 'matchresults', round_str, table_to_parse)

def get_event_stats_json(global_config, year, event_code, stat_type):
        
    global_config['logger'].debug( 'GET Event Results Json' )
        
    # derive our competition name from the FIRST event code 
    competition = WebCommonUtils.map_event_code_to_comp(year+event_code)

    store_data_to_file = False
    result = []
    
    result.append('{ "event" : "%s",\n' % (event_code.lower()))
    
    event_stats = ''
    json_data = get_event_data_from_tba( '%s%s/stats' % (year,event_code.lower()) )
    if json_data != '':
        event_stats = json.loads(json_data)

        # rankings is now a list of lists, with the first element of the list being the list of column headings
        # take the list of columngs and apply to each of the subsequent rows to build the json response
        result.append('  "last_updated": "%s",\n' % time.strftime('%c'))
        headings = [ 'Team', 'OPR' ]
        
        result.append('  "columns" : [\n')

        for heading in headings:
            result.append('    { "sTitle": "%s" }' % heading)
            result.append(',\n')
        if len(headings)>0:
            result = result[:-1]
        result.append(' ],\n')
        result.append('  "stats" : [\n')
    
        stats_dict = event_stats[stat_type]
        
        for key, value in stats_dict.iteritems():
            result.append( '       ["%s", %.2f' % (get_team_hyperlink( competition, key ),value) )
            result.append(' ],\n')
            store_data_to_file = True

        if store_data_to_file is True:
            result = result[:-1]
            result.append(' ]\n')
            
        result.append(' ]\n')

    else:
        # we were not able to retrieve the data from FIRST, so let's return any stored file with the 
        # information, otherwise we will return an empty json payload
        stored_file_data = FileSync.get( global_config, '%s/EventData/eventstats_%s.json' % (competition,stat_type) )
        if stored_file_data != '':
            return stored_file_data
    
    result.append(' }\n')
    json_str = ''.join(result)
    if store_data_to_file:
        try:
            FileSync.put( global_config, '%s/EventData/eventstats_%s.json' % (competition,stat_type), 'text', json_str)
        except:
            raise
    return json_str    

def get_team_hyperlink( competition, team ):
    team_hyperlink = '<a href=\\"/teamdata/%s/%s\\">%s</a>' % (competition,team,team)
    return team_hyperlink

def get_event_matchschedule_json(global_config, year, event_code, round_str):
        
    global_config['logger'].debug( 'GET Event Results Json - %s' % round_str )
    
    if round_str == 'qual':
        round_str = 'qualifications'
    elif round_str == 'elim':
        round_str = 'playoffs'

    #return get_data_from_first(global_config, year, event_code, round_str )
    return ''

def need_team_hyperlink(heading):
    if (heading.find('Team') != -1) or \
       ((heading.find('Red') != -1) and heading.find('Score') == -1) or \
       ((heading.find('Blue') != -1) and heading.find('Score') == -1) :
        need_hyperlink = True
    else:
        need_hyperlink = False
    return need_hyperlink

def get_data_from_first(global_config, year, event_code, query_str, round_str = '', table_to_parse=2):

    result = []
    store_data_to_file = False

    # derive our competition name from the FIRST event code 
    competition = WebCommonUtils.map_event_code_to_comp(year+event_code)
        
    result.append('{ "event" : "%s",\n' % (event_code.lower()))
    
    try:
        
        opener = urllib2.build_opener()
        opener.addheaders = [('Authorization', 'Basic a3N0aGlsYWlyZTozMDMyRTUxRS1CNkFBLTQ2QzgtOEY5Qy05QzdGM0EzM0Q4RjI='),('Accept','application/json')]
                
        #first_url_str = 'http://frc-events.usfirst.org/%s/%s/%s' % (year,event_code.upper(),query_str)
        first_url_str = 'https://frc-api.usfirst.org/api/v1.0/rankings/%s/%s' % (year,event_code.upper())
        
        print 'GET - %s' % first_url_str
        rank_data = opener.open(first_url_str)
                
        my_parser = RankParser()
        rankings, _ = my_parser.parse( rank_data, table_to_parse )
        
        # rankings is now a list of lists, with the first element of the list being the list of column headings
        # take the list of columngs and apply to each of the subsequent rows to build the json response
        
        result.append('  "last_updated": "%s",\n' % time.strftime('%c'))
        headings = rankings[0]
        result.append('  "columns" : [\n')

        for heading in headings:
            result.append('    { "sTitle": "%s" }' % heading)
            result.append(',\n')
        if len(headings)>0:
            result = result[:-1]
        result.append(' ],\n')
        result.append('  "%s" : [\n' % (query_str))
        
        for line in rankings[1:]:
            result.append('       [ ')
            for i in range(0,len(headings)):
                if need_team_hyperlink(headings[i]):
                    #result.append('"%s"' % (line[i]))
                    result.append(('"<a href=\\"/teamdata/%s/'% competition)+line[i]+'\\">'+line[i]+'</a>"')
                else:
                    #result.append('"%s": "%s"' % (headings[i].title(),line[i]))
                    result.append('"%s"' % (line[i]))
                    
                result.append(', ')
            if len(line) > 0:         
                result = result[:-1]
            result.append(' ],\n')
                
        if len(rankings) > 1:         
            result = result[:-1]
        result.append(' ]\n')
        store_data_to_file = True
    except Exception, err:
        print 'Caught exception:', err
    except:
        # we were not able to retrieve the data from FIRST, so let's return any stored file with the 
        # information, otherwise we will return an empty json payload
        stored_file_data = FileSync.get( global_config, '%s/EventData/%s%s.json' % (competition,query_str,round_str) )
        if stored_file_data != '':
            return stored_file_data
    
    result.append(' ] }\n')
    json_str = ''.join(result)
    if store_data_to_file:
        try:
            FileSync.put( global_config, '%s/EventData/%s%s.json' % (competition,query_str,round_str), 'text', json_str)
        except:
            raise
    return json_str

        
def update_event_data_files( global_config, year, event, directory ):
    
    result = False
    
    event_code = CompAlias.get_eventcode_by_alias(event)
    
    my_team = global_config['my_team']
    # for now, we only support updating files in the EventData directory, so only continue if that's the 
    # directory that was specified.
    if directory.upper() == 'EVENTDATA':
        # call each of the get_event_xxx() functions to attempt to retrieve the json data. This action
        # will also store the json payload to the EventData directory completing the desired 
        # operation
        get_event_standings_json( global_config, year, event_code )
        get_event_stats_json( global_config, year, event_code, 'oprs' )
        get_event_matchresults_json(global_config, year, event_code, 'qual')
        get_event_matchresults_json(global_config, year, event_code, 'quarters')
        get_event_matchresults_json(global_config, year, event_code, 'semis')
        get_event_matchresults_json(global_config, year, event_code, 'finals')
        get_event_matchresults_json(global_config, year, event_code, 'qual', my_team)
        get_event_matchresults_json(global_config, year, event_code, 'quarters', my_team)
        get_event_matchresults_json(global_config, year, event_code, 'semis', my_team)
        get_event_matchresults_json(global_config, year, event_code, 'finals', my_team)
        
        result = True
        
    return result
        