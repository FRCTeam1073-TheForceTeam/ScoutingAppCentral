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
import TbaIntf
import GoogleMapsIntf
import DbSession
import DataModel

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




def get_event_standings_page(global_config, year, event_code):
        
        raise Exception('Not Implemented')
                    
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
            
        url_str = '/api/v2/event/%s%s' % (year,event_code.lower())
        try:
            event_data = TbaIntf.get_from_tba_parsed(url_str)
                        
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
        
        url_str = '/api/v2/district/%s/%s/events' % (type.lower(),year)
        try:
            event_data = TbaIntf.get_from_tba(url_str)
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
        
        url_str = '/api/v2/district/%s/%s/rankings' % (type.lower(),year)

        result = []
        result.append('{ "district" : "%s",\n' % (type.upper()))

        try:
            rankings = TbaIntf.get_from_tba_parsed(url_str)
       
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

            for team_rank in rankings:
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
        
        url_str = '/api/v2/events/%s' % year
        try:
            event_data = TbaIntf.get_from_tba(url_str)
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
    url_str = '/api/v2/event/%s' % (query_str)
    event_data = TbaIntf.get_from_tba_parsed(url_str)
    return event_data

def get_event_json_from_tba( query_str ):
    url_str = '/api/v2/event/%s' % (query_str)
    event_data = TbaIntf.get_from_tba(url_str)
    return event_data


def get_event_info_json(global_config, year, event_code):
        
        global_config['logger'].debug( 'GET Event Info Json' )
            
        event_json = get_event_json_from_tba( '%s%s' % (year,event_code.lower()) )

        return event_json

def get_event_info_dict(global_config, year, event_code):
        
        global_config['logger'].debug( 'GET Event Info Json' )
                    
        event_data = get_event_data_from_tba( '%s%s' % (year,event_code.lower()) )

        return event_data
        
def get_event_standings_json(global_config, year, event_code):
        
    global_config['logger'].debug( 'GET Event Rankings Json' )
    
    # derive our competition name from the FIRST event code 
    competition = WebCommonUtils.map_event_code_to_comp(year+event_code)

    #return get_data_from_first(global_config, year, event_code, 'rankings')
    store_data_to_file = False
    result = []
    
    rankings = get_event_data_from_tba( '%s%s/rankings' % (year,event_code.lower()) )

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
    
    rankings = get_event_data_from_tba( '%s%s/rankings' % (year,event_code.lower()) )

    result.append('{ "event" : "%s",\n' % (event_code.lower()))
    
    if len(rankings):
        # rankings is now a list of lists, with the first element of the list being the list of column headings
        # take the list of columngs and apply to each of the subsequent rows to build the json response
        result.append('  "last_updated": "%s",\n' % time.strftime('%c'))
        result.append('  "rankings" : [\n')
        
        for line in rankings[1:]:
            result.append('       { "rank": %s, "team_number": %s, "status": "available" }' % (line[0],line[1]))
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
    
    if team_str is None:
        exp_filename = ''
        event_matches = get_event_data_from_tba( '%s%s/matches' % (year,event_code.lower()) )
    else:
        exp_filename = '_%s' % team_str
        event_matches = WebTeamData.get_team_data_from_tba( team_str, 'event/%s%s/matches' % (year,event_code.lower()) )
        
    if len(event_matches):

        # matches is now a list of lists, with the first element of the list being the list of column headings
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
                try:
                    if global_config['json_no_links'] == 'Yes':
                        result.append( '"%s", ' % str(match['match_number']) )
                    else:
                        raise
                except:
                    result.append( '"%s", ' % get_match_hyperlink(competition, match) )

                # Match start time
                match_epoch_time = int(match['time'])
                time_format_str = '%a %b %d - %I:%M %p'
                match_time_str = datetime.datetime.fromtimestamp(match_epoch_time).strftime(time_format_str)
                result.append( '"%s", ' % match_time_str )
                
                try:
                    if global_config['json_no_links'] == 'Yes':
                        # Red alliance teams
                        result.append( '"%s", ' % str(match['alliances']['red']['teams'][0]).lstrip('frc') )
                        result.append( '"%s", ' % str(match['alliances']['red']['teams'][1]).lstrip('frc') )
                        result.append( '"%s", ' % str(match['alliances']['red']['teams'][2]).lstrip('frc') )
                        
                        # Blue alliance teams
                        result.append( '"%s", ' % str(match['alliances']['blue']['teams'][0]).lstrip('frc') )
                        result.append( '"%s", ' % str(match['alliances']['blue']['teams'][1]).lstrip('frc') )
                        result.append( '"%s", ' % str(match['alliances']['blue']['teams'][2]).lstrip('frc') )
                    else:
                        raise
                except:
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

'''
def get_event_matchschedule_json(global_config, year, event_code, team_str = None):
        
    global_config['logger'].debug( 'GET Event Schedule Json' )

    # derive our competition name from the FIRST event code 
    competition = WebCommonUtils.map_event_code_to_comp(year+event_code)

    store_data_to_file = False
    result = []
    
    result.append('{ "event" : "%s",\n' % (event_code.lower()))
    
    if team_str is None:
        exp_filename = ''
        event_matches = get_event_data_from_tba( '%s%s/matches' % (year,event_code.lower()) )
    else:
        exp_filename = '_%s' % team_str
        event_matches = WebTeamData.get_team_data_from_tba( team_str, 'event/%s%s/matches' % (year,event_code.lower()) )
        
    if len(event_matches):

        # matches is now a list of lists, with the first element of the list being the list of column headings
        # take the list of columngs and apply to each of the subsequent rows to build the json response
        
        result.append('  "columns" : [ ')
        result.append('"Round", "Match", "Red_1", "Red_2", "Red_3", "Blue_1", "Blue_2", "Blue_3"')

        result.append(' ],\n')
        result.append('  "matchschedule" : [\n')
    
        # the entire match set is returned from TBA, filter out the matches for the desired round
        for match in event_matches:
            
            result.append('       [ ')
            
            result.append( '"%s", ' % str(match['comp_level']) )
            result.append( '"%s", ' % str(match['match_number']) )

            # Red alliance teams
            result.append( '"%s", ' % str(match['alliances']['red']['teams'][0]).lstrip('frc') )
            result.append( '"%s", ' % str(match['alliances']['red']['teams'][1]).lstrip('frc') )
            result.append( '"%s", ' % str(match['alliances']['red']['teams'][2]).lstrip('frc') )
            
            # Blue alliance teams
            result.append( '"%s", ' % str(match['alliances']['blue']['teams'][0]).lstrip('frc') )
            result.append( '"%s", ' % str(match['alliances']['blue']['teams'][1]).lstrip('frc') )
            result.append( '"%s"' % str(match['alliances']['blue']['teams'][2]).lstrip('frc') )                
            
            result.append(' ],\n')
            store_data_to_file = True

        if store_data_to_file is True:
            result = result[:-1]
            result.append(' ]\n')
            
        result.append(' ]\n')

    else:
        # we were not able to retrieve the data from FIRST, so let's return any stored file with the 
        # information, otherwise we will return an empty json payload
        stored_file_data = FileSync.get( global_config, '%s/EventData/matchschedule%s.json' % (competition,exp_filename) )
        if stored_file_data != '':
            return stored_file_data
    
    result.append(' }\n')
    json_str = ''.join(result)
    if store_data_to_file:
        try:
            FileSync.put( global_config, '%s/EventData/matchschedule%s.json' % (competition,exp_filename), 'text', json_str)
        except:
            raise
    return json_str    
'''

def get_event_matchschedule_json(global_config, year, event_code, team_str = None):
        
    global_config['logger'].debug( 'GET Event Schedule Json' )

    # derive our competition name from the FIRST event code 
    competition = WebCommonUtils.map_event_code_to_comp(year+event_code)

    store_data_to_file = False
    result = []
    
    if team_str is None:
        exp_filename = ''
        event_matches = get_event_data_from_tba( '%s%s/matches' % (year,event_code.lower()) )
    else:
        exp_filename = '_%s' % team_str
        event_matches = WebTeamData.get_team_data_from_tba( team_str, 'event/%s%s/matches' % (year,event_code.lower()) )
        
    match_schedule = dict()
    
    match_schedule['event'] = event_code.lower()
    match_schedule['columns'] = [ 'Round', 'Match', 'Red_1', 'Red_2', 'Red_3', 'Blue_1', 'Blue_2', 'Blue_3' ]
    match_schedule['qualification'] = []
    match_schedule['quarter_finals'] = []
    match_schedule['semi_finals'] = []
    match_schedule['finals'] = []
    if len(event_matches):

        # matches is now a list of lists, with the first element of the list being the list of column headings
        # take the list of columngs and apply to each of the subsequent rows to build the json response
        
        # the entire match set is returned from TBA, filter out the matches for the desired round
        for match in event_matches:
            comp_level = match['comp_level']
            if comp_level in ('qf', 'sf'):
                match_str = '%s-%s' % (match['set_number'],match['match_number'])
            else:
                match_str = str(match['match_number'])
                
            match_entry = [ comp_level, match_str,
                            match['alliances']['red']['teams'][0].lstrip('frc'),
                            match['alliances']['red']['teams'][1].lstrip('frc'),
                            match['alliances']['red']['teams'][2].lstrip('frc'),
                            match['alliances']['blue']['teams'][0].lstrip('frc'),
                            match['alliances']['blue']['teams'][1].lstrip('frc'),
                            match['alliances']['blue']['teams'][2].lstrip('frc') ]
            
            if comp_level == 'qm':
                match_schedule['qualification'].append(match_entry)
            elif comp_level == 'qf':
                match_schedule['quarter_finals'].append(match_entry)
            elif comp_level == 'sf':
                match_schedule['semi_finals'].append(match_entry)
            elif comp_level == 'f':
                match_schedule['finals'].append(match_entry)
                
        store_data_to_file = True
        
        # the qualification match schedule needs to be sorted, the sort will be done by the second
        # element of each row, which is the match number
        match_schedule['qualification'].sort(key=lambda match_list: int(match_list[1]))      
    else:
        # we were not able to retrieve the data from FIRST, so let's return any stored file with the 
        # information, otherwise we will return an empty json payload
        stored_file_data = FileSync.get( global_config, '%s/EventData/matchschedule%s.json' % (competition,exp_filename) )
        if stored_file_data != '':
            return stored_file_data
    
    json_str = json.dumps(match_schedule)
    
    if store_data_to_file:
        try:
            FileSync.put( global_config, '%s/EventData/matchschedule%s.json' % (competition,exp_filename), 'text', json_str)
        except:
            raise
    return json_str    

def get_event_stats_json(global_config, year, event_code, stat_type):
        
    global_config['logger'].debug( 'GET Event Results Json' )
        
    # derive our competition name from the FIRST event code 
    competition = WebCommonUtils.map_event_code_to_comp(year+event_code)

    store_data_to_file = False
    result = []
    
    result.append('{ "event" : "%s",\n' % (event_code.lower()))
    
    event_stats = get_event_data_from_tba( '%s%s/stats' % (year,event_code.lower()) )
    if len(event_stats):

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
    
        try:
            stats_dict = event_stats[stat_type]
            
            for key, value in stats_dict.iteritems():
                result.append( '       ["%s", %.2f' % (get_team_hyperlink( competition, key ),value) )
                result.append(' ],\n')
                store_data_to_file = True
    
            if store_data_to_file is True:
                result = result[:-1]
                result.append(' ]\n')
        except:
            global_config['logger'].debug( 'No Statistics Data For %s' % stat_type )
            
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

def get_match_hyperlink( competition, match ):
    red_alliance =   'red=%s+%s+%s' % (str(match['alliances']['red']['teams'][0]).lstrip('frc'),\
                                       str(match['alliances']['red']['teams'][1]).lstrip('frc'),\
                                       str(match['alliances']['red']['teams'][2]).lstrip('frc'))
    blue_alliance = 'blue=%s+%s+%s' % (str(match['alliances']['blue']['teams'][0]).lstrip('frc'),\
                                       str(match['alliances']['blue']['teams'][1]).lstrip('frc'),\
                                       str(match['alliances']['blue']['teams'][2]).lstrip('frc'))
    filter_name = 'Scouting_Brief'
    match_number = str(match['match_number'])
    
    match_hyperlink = '<a href=\\"/matchbrief/%s/%s?%s&%s&%s\\">%s </a>' % \
        (competition,match_number,red_alliance,blue_alliance,filter_name,match_number)
        
    return match_hyperlink

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
        get_event_rank_list_json( global_config, year, event_code )
        get_event_stats_json( global_config, year, event_code, 'oprs' )
        get_event_matchresults_json(global_config, year, event_code, 'qual')
        get_event_matchresults_json(global_config, year, event_code, 'quarters')
        get_event_matchresults_json(global_config, year, event_code, 'semis')
        get_event_matchresults_json(global_config, year, event_code, 'finals')
        get_event_matchresults_json(global_config, year, event_code, 'qual', my_team)
        get_event_matchresults_json(global_config, year, event_code, 'quarters', my_team)
        get_event_matchresults_json(global_config, year, event_code, 'semis', my_team)
        get_event_matchresults_json(global_config, year, event_code, 'finals', my_team)
        get_event_matchschedule_json(global_config, year, event_code, my_team)
        get_event_matchschedule_json(global_config, year, event_code)
        
        result = True
        
    return result
        
def load_event_info(global_config, year_str):
    
    session = DbSession.open_db_session(global_config['db_name'] + global_config['this_season'])
    
    if year_str.lower() == 'all':
        # get all events since the beginning of time
        year = 1992
        done = False
        while not done: 
            url_str = '/api/v2/events/%d' % year
            events_data = TbaIntf.get_from_tba_parsed(url_str)
            
            if len(events_data) == 0:
                done = True
            else:
                for event_data in events_data:
                    #print 'Event: %s' % event_data['key']
                    DataModel.addOrUpdateEventInfo(session, event_data)
                year += 1
    else:
        url_str = '/api/v2/events/%s' % year_str
        events_data = TbaIntf.get_from_tba_parsed(url_str)
        
        for event_data in events_data:
            print 'Event: %s' % event_data['key']
            DataModel.addOrUpdateEventInfo(session, event_data)
            
    session.commit()

def get_event_geo_location(global_config, event_key=None):
    
    session = DbSession.open_db_session(global_config['db_name'] + global_config['this_season'])
    
    DataModel.setEventsGeoLocation(session, event_key)
               