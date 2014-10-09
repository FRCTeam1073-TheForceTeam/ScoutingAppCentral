'''
Created on March 3, 2013

@author: ksthilaire
'''

import urllib2
import json
import web
import WebCommonUtils

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
        
        url_str = 'http://www.thebluealliance.com/api/v1/events/list?year=%s&X-TBA-App-Id=frc1073:scouting-system:v01' % year
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
            
        url_str = 'http://www.thebluealliance.com/api/v1/event/details?event=%s%s&X-TBA-App-Id=frc1073:scouting-system:v01' % (year,event_code.lower())
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
            
        url_str = 'http://www.thebluealliance.com/api/v1/event/details?event=%s%s&X-TBA-App-Id=frc1073:scouting-system:v01' % (year,event_code.lower())
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

def get_events_json(global_config, year, type=None):
        
        global_config['logger'].debug( 'GET Event Info Json' )    
        
        url_str = 'http://www.thebluealliance.com/api/v1/events/list?year=%s&X-TBA-App-Id=frc1073:scouting-system:v01' % year
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

def get_event_info_json(global_config, year, event_code):
        
        global_config['logger'].debug( 'GET Event Info Json' )
            
        url_str = 'http://www.thebluealliance.com/api/v1/event/details?event=%s%s&X-TBA-App-Id=frc1073:scouting-system:v01' % (year,event_code.lower())
        try:
            event_data = urllib2.urlopen(url_str).read()
        except:
            event_data = ''
            pass
        return event_data

def get_event_info_dict(global_config, year, event_code):
        
        global_config['logger'].debug( 'GET Event Info Json' )
            
        url_str = 'http://www.thebluealliance.com/api/v1/event/details?event=%s%s&X-TBA-App-Id=frc1073:scouting-system:v01' % (year,event_code.lower())
        try:
            event_data = urllib2.urlopen(url_str).read()
            event_data = json.loads(event_data)
        except:
            event_data = None
            pass
        return event_data
        
def get_event_standings_json(global_config, year, event_code):
        
    global_config['logger'].debug( 'GET Event Rankings Json' )
    
    return get_data_from_first(global_config, year, event_code, 'rankings')

def get_event_matchresults_json(global_config, year, event_code, table_to_parse):
        
    global_config['logger'].debug( 'GET Event Results Json' )

    return get_data_from_first(global_config, year, event_code, 'matchresults', table_to_parse)

def need_team_hyperlink(heading):
    if (heading.find('Team') != -1) or \
       ((heading.find('Red') != -1) and heading.find('Score') == -1) or \
       ((heading.find('Blue') != -1) and heading.find('Score') == -1) :
        need_hyperlink = True
    else:
        need_hyperlink = False
    return need_hyperlink

def get_data_from_first(global_config, year, event_code, query_str, table_to_parse=2):

    web.header('Content-Type', 'application/json')
    result = []

    result.append('{ "event" : "%s",\n' % (event_code.lower()))
    
    try:
        first_url_str = 'http://www2.usfirst.org/%scomp/events/%s/%s.html' % (year,event_code.upper(),query_str)
        rank_data = urllib2.urlopen(first_url_str).read()
                
        my_parser = RankParser()
        rankings, _ = my_parser.parse( rank_data, table_to_parse )
        
        # derive our competition name from the FIRST event code 
        competition = WebCommonUtils.map_event_code_to_comp(year+event_code)
        
        # rankings is now a list of lists, with the first element of the list being the list of column headings
        # take the list of columngs and apply to each of the subsequent rows to build the json response
        
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
    except:
        pass
    
    result.append(' ] }\n')
    return ''.join(result)
        
