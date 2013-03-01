'''
Created on Feb 4, 2012

@author: Ben
'''
import os
import re
import traceback
import time

import DbSession
import DataModel
import IssueTrackerDataModel
import DebriefDataModel
import FileParser
import FileSync
import AttributeDefinitions

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from optparse import OptionParser

import xlrd
import csv

import socket
from bluetooth import *
import logging.config

logging.config.fileConfig('config/logging.conf')
logger = logging.getLogger('scouting.webapp')

global_config = { 'this_competition'   : None, 
                  'other_competitions' : None, 
                  'db_name'            : 'scouting2013', 
                  'issues_db_name'     : 'issues2013',
                  'issues_db_master'   : 'No',
                  'debriefs_db_name'   : 'debriefs2013',
                  'attr_definitions'   : None,
                  'team_list'          : None,
                  'logger':logger }

def read_config(config_filename):
    cfg_file = open(config_filename, 'r')
    for cfg_line in cfg_file:
        if cfg_line.startswith('#'):
            continue
        cfg_line = cfg_line.rstrip()
        if cfg_line.count('=') > 0:
            (attr,value) = cfg_line.split('=',1)
            global_config[attr] = value
        else:
            # ignore lines that don't have an equal sign in them
            pass   
    cfg_file.close()

class HTTPMessageError(Exception): pass
class HTTPMessageReader(object):
    def __init__(self,sock):
        self.sock = sock
        self.buffer = b''
    def get_until(self,what):
        while what not in self.buffer:
            if not self._fill():
                return b''
        offset = self.buffer.find(what) + len(what)
        data,self.buffer = self.buffer[:offset],self.buffer[offset:]
        return data 
    def get_bytes(self,size):
        while len(self.buffer) < size:
            if not self._fill():
                return b''
        data,self.buffer = self.buffer[:size],self.buffer[size:]
        return data
    def _fill(self):
        data = self.sock.recv(1024)
        if not data:
            if self.buffer:
                raise HTTPMessageError('socket closed with incomplete message')
            return False
        self.buffer += data
        return True
    def get_msg(self):
        is_chunked = False
        header = self.get_until(b'\r\n\r\n')
        print(header.decode('ascii'))

        data = ''
        length_byte = re.search(b'Content-Length: (\d+)', header)
        if length_byte:
            length = int(length_byte.group(1))
            data = self.get_bytes(length)
            
        else:
            chunked = re.search(b'Transfer-Encoding: chunked', header)
            if chunked:
                is_chunked = True
        return header + data, is_chunked
    def get_chunk(self):
        chunk_length_line = self.get_until(b'\r\n')
        chunk_length = int(chunk_length_line, 16)
        chunk_data = self.get_bytes(chunk_length + 2)
        return chunk_length_line + chunk_data, chunk_length

'''Get list of files to be processed.

Args:
    input_dir: Directory to search.
    pattern: Regular expression to use to filter files.
    recursive: Whether or not to recurse into input_dir.

Returns:
    A list of files.
'''
def isFileProcessed(session, db_name, filepath):
    if db_name == global_config['db_name']:
        is_processed = DataModel.isFileProcessed(session, filepath)
    elif db_name == global_config['issues_db_name']:
        is_processed = IssueTrackerDataModel.isFileProcessed(session, filepath)
    elif db_name == global_config['debriefs_db_name']:
        is_processed = DebriefDataModel.isFileProcessed(session, filepath)
        
    return is_processed
                                                 
def get_files(session, db_name, input_dir, pattern, recursive, test_mode):    
    file_list = []    
    
    if recursive:
        for root, dirs, files in os.walk(input_dir):
            #print 'Root:', root, ' Dirs: ', dirs, ' Files:', files
            for name in files:
                if pattern.match(name):
                    if((test_mode == True) or (isFileProcessed(session, db_name, os.path.join(root, name))) == False):
                        file_list.append(os.path.join(root, name))
    else:
        files = os.listdir(input_dir)
        #print 'Files:', files
        for name in files:
            if pattern.match(name):
                if((test_mode == True) or (isFileProcessed(session, db_name, os.path.join(root, name))) == False):
                    file_list.append(os.path.join(input_dir, name))

    if len(file_list) > 0:
        print 'FileList:', file_list
        
    return file_list

def dump_database_as_csv_file(session, attr_definitions, competition=None):
    
    if competition == None:
        competition = global_config['this_competition']
    
    # read in the attribute definitions and sort them in the colum order
    attr_dict = attr_definitions.get_definitions()
    attr_order = [{} for i in range(len(attr_dict))]
    
    try:
        for key, value in attr_dict.items():
            attr_order[(int(float(value['Column_Order']))-1)] = value
            #attr_order[(int(value['Column_Order'])-1)] = value
    except Exception, e:
        print 'Exception: %s' % str(e)

    # open up the output filename that matches the database name
    path = './static/attr'
    if not os.path.exists(path):
        os.makedirs(path)
    outputFilename = path + '/' + competition + '.csv'
    fo = open(outputFilename, "w+")

    # Write out the column headers
    mystring = 'Team,Score'
    try:
        for attr_def in attr_order:
            if attr_def['Database_Store'] == 'Yes':
                mystring += ',' + attr_def['Name']
    except Exception, e:
        print 'Exception: %s' % str(e)

    mystring += '\n'
    fo.write( mystring )
    
    # Get the list of teams in rank order, then loop through teams and dump their stored
    # attribute values
    team_rankings = DataModel.getTeamsInRankOrder(session, competition)
    for team_entry in team_rankings:
        mystring = str(team_entry.team) + ',' + str(team_entry.score)
        # retrieve each attribute from the database in the proper order
        for attr_def in attr_order:
            if attr_def['Database_Store'] == 'Yes':
                attribute = DataModel.getTeamAttribute(session, team_entry.team, competition, attr_def['Name'])
                # if the attribute doesn't exist, just put in an empty field so that the columns
                # stay aligned
                if attribute == None:
                    mystring += ','
                elif ( attr_def['Statistic_Type'] == 'Total'):
                    #mystring += ',' + str(attribute.cumulative_value)
                    mystring += ',' + DataModel.mapValueToString(attribute.cumulative_value, attribute.all_values, attr_def)
                elif ( attr_def['Statistic_Type'] == 'Average'):
                    #mystring += ',' + str(attribute.avg_value)
                    mystring += ',' + DataModel.mapValueToString(attribute.avg_value, attribute.all_values, attr_def)
                else:
                    #mystring += ',' + str(attribute.attr_value)
                    mystring += ',' + DataModel.mapValueToString(attribute.attr_value, attribute.all_values, attr_def)

        mystring += '\n'
        fo.write( mystring )
    fo.close()

  
def process_files(session, db_name, attr_definitions, input_dir, recursive, test):
    # The following regular expression will select all files that conform to 
    # the file naming format Team*.txt. Build a list of all datafiles that match
    # the naming format within the directory passed in via command line 
    # arguments.
    file_regex = re.compile('Team[a-zA-Z0-9_]+.txt')
    files = get_files(session, db_name, input_dir, file_regex, recursive, test)
    
    # Process data files
    for data_filename in files:
        process_file( session, attr_definitions, data_filename)
        
def process_file(session, attr_definitions, data_filename):
    print 'processing %s'%data_filename
    
    # Initialize the file_attributes dictionary in preparation for the
    # parsing of the data file
    file_attributes = {}
    
    # Parse the data file, storing all the information in the file_attributes
    # dictionary
    FileParser.FileParser(data_filename).parse(file_attributes)
    DataModel.addProcessedFile(session, data_filename)

    # The team number can be retrieved from the Team attribute, one of the
    # mandatory attributes within the data file
    team = file_attributes['Team']
    
    # Also, extract the competition name, too, if it has been included in
    # the data file
    if file_attributes.has_key('Competition'):
        competition = file_attributes['Competition']
    else:
        competition = global_config['this_competition']
        if competition == None:
            raise Exception( 'Competition Not Specified!')

    DataModel.addTeamToEvent(session, team, competition)
    
    # Loop through the attributes from the data file and post them to the
    # database
    for attribute, value in file_attributes.iteritems():
        if value is None:
            value = ''
        try:
            attr_definition = attr_definitions.get_definition(attribute)
            if attr_definition == None:
                err_str = 'ERROR: No Attribute Defined For Attribute: %s' % attribute
                print err_str
            elif attr_definition['Database_Store']=='Yes':
                try:
                    DataModel.createOrUpdateAttribute(session, team, competition, attribute, value, attr_definition)
                except Exception, exception:
                    traceback.print_exc(file=sys.stdout)
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    exception_info = traceback.format_exception(exc_type, exc_value,exc_traceback)
                    for line in exception_info:
                        line = line.replace('\n','')
                        global_config['logger'].debug(line)
        except Exception:
            err_str = 'ERROR: Attribute Could Not Be Processed: %s' % attribute
            traceback.print_exc(file=sys.stdout)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            exception_info = traceback.format_exception(exc_type, exc_value,exc_traceback)
            for line in exception_info:
                line = line.replace('\n','')
                global_config['logger'].debug(line)
            print err_str
            
    score = DataModel.calculateTeamScore(session, team, competition, attr_definitions)
    DataModel.setTeamScore(session, team, competition, score)
    # Commit all updates to the database
    session.commit()

def process_issue_files(global_config, input_dir, recursive, test):

    # Initialize the database session connection
    issues_db_name  = global_config['issues_db_name']
    debrief_db_name = global_config['debriefs_db_name']
    debrief_session = DbSession.open_db_session(debrief_db_name)
    issues_session  = DbSession.open_db_session(issues_db_name)

    # The following regular expression will select all files that conform to 
    # the file naming format Issue*.txt. Build a list of all datafiles that match
    # the naming format within the directory passed in via command line 
    # arguments.
    file_regex = re.compile('Issue[a-zA-Z0-9_-]+.txt')
    files = get_files(issues_session, issues_db_name, input_dir, file_regex, recursive, test)
    
    files.sort()
    
    # Process data files
    for data_filename in files:
        print 'processing %s'%data_filename
        
        # Initialize the file_attributes dictionary in preparation for the
        # parsing of the data file
        issue_attributes = {}
        
        # Parse the data file, storing all the information in the file_attributes
        # dictionary
        FileParser.FileParser(data_filename).parse(issue_attributes)
        IssueTrackerDataModel.addProcessedFile(issues_session, data_filename)

        issue = IssueTrackerDataModel.addIssueFromAttributes(issues_session, issue_attributes)
        if issue.debrief_key != None:
            match_str, issue_key = issue.debrief_key.split('_')
            DebriefDataModel.addOrUpdateDebriefIssue(debrief_session, int(match_str), 
                                                     global_config['this_competition'],
                                                     issue.issue_id, issue_key)
            
    debrief_session.commit()
    issues_session.commit()
        
    
def process_debrief_files(global_config, input_dir, recursive, test):

    # Initialize the database session connections
    issues_db_name  = global_config['issues_db_name']
    debrief_db_name = global_config['debriefs_db_name']
    debrief_session = DbSession.open_db_session(debrief_db_name)
    issues_session  = DbSession.open_db_session(issues_db_name)
    
    # Create the database if it doesn't already exist
    #if not os.path.exists('./' + db_name):    
    #   DebriefDataModel.create_db_tables(my_db)

    # The following regular expression will select all files that conform to 
    # the file naming format Debrief*.txt. Build a list of all datafiles that match
    # the naming format within the directory passed in via command line 
    # arguments.
    file_regex = re.compile('Debrief[a-zA-Z0-9_-]+.txt')
    files = get_files(debrief_session, debrief_db_name, input_dir, file_regex, recursive, test)
    
    # Process data files
    for data_filename in files:
        print 'processing %s'%data_filename
        
        # Initialize the debrief_attributes dictionary in preparation for the
        # parsing of the data file
        debrief_attributes = {}
        
        # Parse the data file, storing all the information in the attributes
        # dictionary
        FileParser.FileParser(data_filename).parse(debrief_attributes)
        DebriefDataModel.addDebriefFromAttributes(debrief_session, debrief_attributes)
        DebriefDataModel.addProcessedFile(debrief_session, data_filename)
        
        # Also, extract the competition name, too, if it has been included in
        # the data file
        if debrief_attributes.has_key('Competition'):
            competition = debrief_attributes['Competition']
        else:
            competition = global_config['this_competition']
            if competition == None:
                raise Exception( 'Competition Not Specified!')

        # At competition, we will likely have multiple laptops manging the data, but we want
        # only one machine to be responsible for the issues database. In all likelihood,
        # that machine will be the one in the pits, or possibly the application running
        # in the cloud.
        if global_config['issues_db_master'] == 'Yes':
            match_id = debrief_attributes['Match']
            submitter = debrief_attributes['Scouter']
            timestamp = str(int(time.time()))
            subgroup = 'Unassigned'
            status = 'Open'
            owner = 'Unassigned'
            
            if debrief_attributes.has_key('Issue1_Summary'):
                # look to see if there is already a debrief issue, and if so, do not attempt to create/update
                # an issue, as there are already other issue files that would then conflict with this one
                issue_key = 'Issue1'
                if DebriefDataModel.getDebriefIssue(debrief_session, match_id, issue_key) == None:
                    summary = debrief_attributes['Issue1_Summary']
                    if debrief_attributes.has_key('Issue1_Priority'):
                        priority = debrief_attributes['Issue1_Priority']
                    else:
                        priority = 'Priority_3'
                    if debrief_attributes.has_key('Issue1_Taskgroup'):
                        component = debrief_attributes['Issue1_Taskgroup']
                    else:
                        component = ''
                    if debrief_attributes.has_key('Issue1_Description'):
                        description = debrief_attributes['Issue1_Description']
                    else:
                        description = ''
                    debrief_key = str(match_id) + '_' + issue_key
                
                    issue_id = IssueTrackerDataModel.getIssueId(issues_session, 'Robot')
                    issue = IssueTrackerDataModel.addOrUpdateIssue(issues_session, issue_id, summary, status, priority, 
                             subgroup, component, submitter, owner, description, timestamp, debrief_key)
                    if issue != None:
                        issue.create_file('./static/%s/ScoutingData' % competition)
                    DebriefDataModel.addOrUpdateDebriefIssue(debrief_session, match_id, competition, issue_id, issue_key)
                
            if debrief_attributes.has_key('Issue2_Summary'):
                issue_key = 'Issue2'
                if DebriefDataModel.getDebriefIssue(debrief_session, match_id, issue_key) == None:
                    summary = debrief_attributes['Issue2_Summary']
                    if debrief_attributes.has_key('Issue2_Priority'):
                        priority = debrief_attributes['Issue2_Priority']
                    else:
                        priority = 'Priority_3'
                    if debrief_attributes.has_key('Issue2_Taskgroup'):
                        component = debrief_attributes['Issue2_Taskgroup']
                    else:
                        component = ''
                    if debrief_attributes.has_key('Issue3_Description'):
                        description = debrief_attributes['Issue3_Description']
                    else:
                        description = ''
                    debrief_key = str(match_id) + '_' + issue_key
                    
                    issue_id = IssueTrackerDataModel.getIssueId(issues_session, 'Robot')
                    issue = IssueTrackerDataModel.addOrUpdateIssue(issues_session, issue_id, summary, status, priority, 
                             subgroup, component, submitter, owner, description, timestamp, debrief_key)
                    if issue != None:
                        issue.create_file('./static/%s/ScoutingData' % competition)
                    DebriefDataModel.addOrUpdateDebriefIssue(debrief_session, match_id, competition, issue_id, issue_key)
                
            if debrief_attributes.has_key('Issue3_Summary'):
                issue_key = 'Issue3'
                if DebriefDataModel.getDebriefIssue(debrief_session, match_id, issue_key) == None:
                    summary = debrief_attributes['Issue3_Summary']
                    if debrief_attributes.has_key('Issue3_Priority'):
                        priority = debrief_attributes['Issue3_Priority']
                    else:
                        priority = 'Priority_3'
                    if debrief_attributes.has_key('Issue3_Taskgroup'):
                        component = debrief_attributes['Issue3_Taskgroup']
                    else:
                        component = ''
                    if debrief_attributes.has_key('Issue3_Description'):
                        description = debrief_attributes['Issue3_Description']
                    else:
                        description = ''
                    debrief_key = str(match_id) + '_' + issue_key
                
                    issue_id = IssueTrackerDataModel.getIssueId(issues_session, 'Robot')
                    issue = IssueTrackerDataModel.addOrUpdateIssue(issues_session, issue_id, summary, status, priority, 
                             subgroup, component, submitter, owner, description, timestamp, debrief_key)
                    if issue != None:
                        issue.create_file('./static/%s/ScoutingData' % competition)
                    DebriefDataModel.addOrUpdateDebriefIssue(debrief_session, match_id, competition, issue_id, issue_key)
            
    issues_session.commit()
    debrief_session.commit()
        
if __name__ == '__main__':
        
    # command line options handling
    parser = OptionParser()
    
    parser.add_option(
        "-t","--test",action="store_true",dest="test",default=False,
        help="Processed test toggle")
    parser.add_option(
        "-R","--recurse",action="store_true", dest="recursive", default=True, 
        help='Recursion toggle')
    parser.add_option(
        "-f","--cfgfile",dest="cfg_filename", default="./config/ScoutingAppConfig.txt", 
        help='Application config filename')
    parser.add_option(
        "-u","--user",dest="user", default='root', 
        help='Database user name')
    parser.add_option(
        "-d","--db",dest="db", default='scouting2013', 
        help='Database name')
    parser.add_option(
        "-P","--password",dest="password", default='team1073',
        help='Database password')
    parser.add_option(
        "-b","--dbtype",dest="dbtype", default='sqlite',
        help='Select database type (mysql or sqlite')
    parser.add_option(
        "-r","--recalculate",action="store_true", dest="recalculate", default=False,
        help='Recalculate Team Scores')
    parser.add_option(
        "-p","--processfiles",action="store_true", dest="processfiles", default=False,
        help='Process Team Files')
    parser.add_option(
        "-l","--processloop",action="store_true", dest="processloop", default=False,
        help='Process Team Files')
    parser.add_option(
        "-i","--processissues",action="store_true", dest="processissues", default=False,
        help='Process Issues Files')
    parser.add_option(
        "-z","--bluetooth",action="store_true", dest="bluetoothServer", default=False,
        help='Run Bluetooth Server')
    parser.add_option(
        "-y","--bluetooth-proxy",action="store_true", dest="bluetoothProxy", default=False,
        help='Run Bluetooth Proxy')
   
    # Parse the command line arguments
    (options,args) = parser.parse_args()
    
    # read in the configuration file containing data related to this competition
    read_config(options.cfg_filename)
    input_dir = './static/' + global_config['this_competition'] + '/ScoutingData/'
    
    db_name = global_config['db_name']
    issues_db_name = global_config['issues_db_name']
    debriefs_db_name = global_config['debriefs_db_name']
    '''    
    # Determine which database type to initialize based on the passed in command
    # arguments    
    if options.dbtype == 'sqlite':
        db_connect='sqlite:///%s'%(db_name)
    elif options.dbtype == 'mysql':
        db_connect='mysql://%s:%s@localhost/%s'%(options.user, options.password, db_name)
    else:
        raise Exception("No Database Type Defined!")

    # Initialize the database session connection
    my_db = create_engine(db_connect)
    Session = sessionmaker(bind=my_db)
    session = Session()

    # Create the database if it doesn't already exist
    if not os.path.exists('./' + db_name):    
        DataModel.create_db_tables(my_db)

    # Create the database if it doesn't already exist
    if not os.path.exists('./' + issues_db_name):    
        IssueTrackerDataModel.create_db_tables(my_db)

    # Create the database if it doesn't already exist
    if not os.path.exists('./' + debriefs_db_name):    
        DebriefDataModel.create_db_tables(my_db)
    '''

    session         = DbSession.open_db_session(db_name, DataModel)
    issues_session  = DbSession.open_db_session(issues_db_name, IssueTrackerDataModel)
    debrief_session = DbSession.open_db_session(debriefs_db_name, DebriefDataModel)
        
    # Build the attribute definition dictionary from the definitions csv file
    #attrdef_filename = './config/' + 'AttributeDefinitions-reboundrumble.csv'    
    attrdef_filename = './config/' + global_config['attr_definitions']    
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)

    if options.processfiles:
        competition = global_config['this_competition']
        try:
            process_files(session, db_name, attr_definitions, input_dir, options.recursive, options.test)
            dump_database_as_csv_file(session, attr_definitions, competition)
        except Exception, e:
            global_config['logger'].debug('Exception Caught Processing Files: %s' % str(e) )
            traceback.print_exc(file=sys.stdout)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            exception_info = traceback.format_exception(exc_type, exc_value,exc_traceback)
            for line in exception_info:
                line = line.replace('\n','')
                global_config['logger'].debug(line)
    
            print 'Program terminated, press <CTRL-C> to exit'
            data = sys.stdin.readlines()          
        
    if options.processissues:
        # process any accumulated issues files
        process_issue_files(global_config, input_dir, options.recursive, options.test)
        
    # recalculate the team scores 
    if options.recalculate:
        competition = global_config['this_competition']
        if competition == None:
            raise Exception( 'Competition Not Specified!')

        team_rankings = DataModel.getTeamsInRankOrder(session, competition)
        for team_entry in team_rankings:
            score = DataModel.calculateTeamScore(session, team_entry.team, competition, attr_definitions)
            DataModel.setTeamScore(session, team_entry.team, competition, score)
        session.commit()
        dump_database_as_csv_file(session, attr_definitions, competition)

    if options.bluetoothServer:
        server_sock=BluetoothSocket( RFCOMM )
        server_sock.bind(("",PORT_ANY))
        server_sock.listen(1)
        
        port = server_sock.getsockname()[1]
        
        uuid = "00001073-0000-1000-8000-00805F9B34F7"
        
        advertise_service( server_sock, "TTTService",
                           service_id = uuid,
                           service_classes = [ uuid, SERIAL_PORT_CLASS ],
                           profiles = [ SERIAL_PORT_PROFILE ], 
        #                   protocols = [ OBEX_UUID ] 
                            )
                           
        while True:
            
            print "Waiting for connection on RFCOMM channel %d" % port
        
            client_sock, client_info = server_sock.accept()
            print "Accepted connection from ", client_info

            files_received = 0
        
            try:
                while True:
                    msg_request_complete = False
                    msg_request = ''
                    while msg_request_complete == False:
                        msg_request += client_sock.recv(8192)
                        if len(msg_request) == 0:
                            msg_request_complete = True
                        else:
                            msg_request_complete = msg_request.endswith('\n\n')
                            
                    if len(msg_request) == 0: break
                    
                    num_msg_parts = msg_request.count('\n\n')
                    if num_msg_parts == 1:
                        msg_header, msg_body = msg_request.split('\n\n')
                    elif num_msg_parts == 2:
                        msg_header, msg_body, msg_term = msg_request.split('\n\n')
                    else: 
                        print "Num Msg Parts: %d" % num_msg_parts
                        break
        
                    print "Message Header: %s" % msg_header
                    print "Message Body: %s" % msg_body
                    print "Message Body Length: %d" % len(msg_body)
                        
                    msg_header_lines = msg_header.splitlines()
                    request_type, request_path = msg_header_lines[0].split()
                    
                    print "Request Type: %s" % request_type
                    print "Request Path: %s" % request_path
                    
                    if request_type == "PUT":
                        fullpath = './static/' + request_path
                        response_code = FileSync.put_file(fullpath, msg_body)
                        client_sock.send('HTTP/1.1 ' + response_code + '\n')
                        files_received += 1
                    elif request_type == "GET":
                        
                        fullpath = './static/' + request_path
                        if os.path.isdir(fullpath):
                            file_list = FileSync.get_file_list(fullpath)
                            response_body = ''
                            for file_name in file_list:
                                response_body += file_name + '\n'
                            client_sock.send('HTTP/1.1 ' + '200 OK' + '\n\n')
                            client_sock.send(response_body + '\n')
                        else:
                            response_body = FileSync.get_file(fullpath)
                            if response_body != '':
                                client_sock.send('HTTP/1.1 ' + '200 OK' + '\n\n')
                                client_sock.send(response_body + '\n\n')
                            else:
                                client_sock.send('HTTP/1.1 ' + '404 Not Found' + '\n\n')
                                    
                    print "Request Complete\n"
        
                    
            except IOError:
                pass
        
            print "disconnected"
        
            client_sock.close()
            
            # if we received files from the client, then go ahead and process them to keep
            # the database up to date in real time
            if files_received > 0:
                try:
                    process_files(session, db_name, attr_definitions, input_dir, options.recursive, options.test)
                    process_issue_files(global_config, input_dir, options.recursive, options.test)
                    process_debrief_files(global_config, input_dir, options.recursive, options.test)
                    dump_database_as_csv_file(session, attr_definitions)
                except Exception, e:
                    global_config['logger'].debug('Exception Caught Processing Files: %s' % str(e) )
                    traceback.print_exc(file=sys.stdout)
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    exception_info = traceback.format_exception(exc_type, exc_value,exc_traceback)
                    for line in exception_info:
                        line = line.replace('\n','')
                        global_config['logger'].debug(line)
            
                    print 'Program terminated, press <CTRL-C> to exit'
                    data = sys.stdin.readlines()


        server_sock.close()
        print "all done"
        
    if options.bluetoothProxy:
        print "Starting bluetooth proxy"
        bt_server_sock=BluetoothSocket( RFCOMM )
        bt_server_sock.bind(("",PORT_ANY))
        bt_server_sock.listen(1)
        
        port = bt_server_sock.getsockname()[1]
        
        uuid = "00001073-9000-1000-8000-00805F9B34F7"
        
        advertise_service( bt_server_sock, "ProxyService",
                           service_id = uuid,
                           service_classes = [ uuid, SERIAL_PORT_CLASS ],
                           profiles = [ SERIAL_PORT_PROFILE ], 
        #                   protocols = [ OBEX_UUID ] 
                            )
                           
        while True:
            
            print "Waiting for connection on RFCOMM channel %d" % port
        
            bt_client_socket, bt_client_info = bt_server_sock.accept()
            print "Accepted connection from ", bt_client_info
        
            try:
                while True:
                    
                    request_reader = HTTPMessageReader(bt_client_socket)
                    msg_request, is_chunked = request_reader.get_msg()
                    
                    #msg_request = bt_client_sock.recv(8192)
                    #if msg_request.find('content-length') != None:
                        # There is a body to this request, so go find the
                        # content length and read in the rest
                    #    headers = msg_request.splitlines()
                        
                        #for header in headers:
                            
                    tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp_client_socket.connect(("localhost", 80))
                    tcp_client_socket.send(msg_request)
        
                    response_reader = HTTPMessageReader(tcp_client_socket)
                    msg_response, is_chunked = response_reader.get_msg()
                    
                    # now write the response back out to the bluetooth socket
                    bt_client_socket.send(msg_response)
                    
                    # if the response contains a chunked body, then transfer the
                    # chunks as well
                    if is_chunked == True:
                        done = False
                        while done == False:
                            msg_chunk, chunk_length = response_reader.get_chunk()
                            if chunk_length == 0:
                                done = True                                
                            bt_client_socket.send(msg_chunk)
                    
                    #tcp_client_socket.recv(8192)
                    # need to read the entire response from the web server
                    #msg_response += tcp_client_socket.recv(8192)
                    
                    tcp_client_socket.close()
                    
                    print "Request Complete\n"
                          
            except IOError:
                pass
        
            print "bluetooth connection closed"
            bt_client_socket.close()
            
        bt_server_sock.close()
        print "all done"
    
    if options.processloop:
        terminate = False
        while not terminate:
            try:
                print 'Scanning for new files to process'
                process_files(session, db_name, attr_definitions, input_dir, options.recursive, options.test)
                process_issue_files(global_config, input_dir, options.recursive, options.test)
                process_debrief_files(global_config, input_dir, options.recursive, options.test)
                dump_database_as_csv_file(session, attr_definitions)
                print 'Scan complete'
            except Exception, e:
                global_config['logger'].debug('Exception Caught Processing Files: %s' % str(e) )
                traceback.print_exc(file=sys.stdout)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                exception_info = traceback.format_exception(exc_type, exc_value,exc_traceback)
                for line in exception_info:
                    line = line.replace('\n','')
                    global_config['logger'].debug(line)
        
                print 'Program terminated, press <CTRL-C> to exit'
                data = sys.stdin.readlines()
                
            time.sleep(30)

            
        
        

