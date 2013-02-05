'''
Created on Feb 4, 2012

@author: Ben
'''
import os
import re
import DataModel
import IssueTrackerDataModel
import DebriefDataModel
import FileParser
import AttributeDefinitions
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from optparse import OptionParser

import xlrd
import csv

import socket
from bluetooth import *

global_config = { 'this_competition'   : None, 
                  'other_competitions' : None, 
                  'db_name'            : 'scouting2013', 
                  'issues_db_name'     : 'issues2013', 
                  'team_list'          : None}

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
    return is_processed
                                                 
def get_files(session, db_name, input_dir, pattern, recursive, test_mode):    
    file_list = []    
    
    if recursive:
        for root, dirs, files in os.walk(input_dir):
            print 'Root:', root, ' Dirs: ', dirs, ' Files:', files
            for name in files:
                if pattern.match(name):
                    if((test_mode == True) or (isFileProcessed(session, db_name, os.path.join(root, name))) == False):
                        file_list.append(os.path.join(root, name))
    else:
        files = os.listdir(input_dir)
        print 'Files:', files
        for name in files:
            if pattern.match(name):
                if((test_mode == True) or (isFileProcessed(session, db_name, os.path.join(root, name))) == False):
                    file_list.append(os.path.join(input_dir, name))

    print 'FileList:', file_list
    return file_list

def put_file( path, file_data):
    fullpath = './static/' + path
    fd = open(fullpath, 'w+')
    fd.write(file_data)
    fd.close()
    return '200 OK'
    
def get_file_list( path ):
    fullpath = './static/' + path

    file_list = os.listdir(fullpath)
    return file_list

def dump_database_as_csv_file(session, attr_definitions, competition=None):
    
    if competition == None:
        competition = global_config['this_competition']
    
    # read in the attribute definitions and sort them in the colum order
    attr_dict = attr_definitions.get_definitions()
    attr_order = [{} for i in range(len(attr_dict))]
    for key, value in attr_dict.items():
        attr_order[(int(float(value['Column_Order']))-1)] = value
        #attr_order[(int(value['Column_Order'])-1)] = value

    # open up the output filename that matches the database name
    outputFilename = './static/attr/' + competition + '.csv'
    fo = open(outputFilename, "w+")

    # Write out the column headers
    mystring = 'Team,Score'
    for attr_def in attr_order:
        if attr_def['Database_Store'] == 'Yes':
            mystring += ',' + attr_def['Name']
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
    
        # Loop through the attributes from the data file and post them to the
        # database
        for attribute, value in file_attributes.iteritems():
            if value is None:
                value = ''
            try:
                attr_definition = attr_definitions.get_definition(attribute)
                if attr_definition['Database_Store']=='Yes':
                    try:
                        DataModel.createOrUpdateAttribute(session, team, competition, attribute, value, attr_definition)
                    except Exception, exception:
                        print str(exception)
            except KeyError:
                err_str = 'ERROR: No Attribute Defined For Attribute: %s' % attribute
                print err_str
                # TODO: raise an exception to catch unknown attributes during testing
                
        score = DataModel.calculateTeamScore(session, team, competition, attr_definitions)
        DataModel.setTeamScore(session, team, competition, score)
        # Commit all updates to the database
        session.commit()

def process_issue_files(db_name, input_dir, recursive, test):

    # Initialize the database session connection
    db_connect='sqlite:///%s'%(db_name)
    my_db = create_engine(db_connect)
    Session = sessionmaker(bind=my_db)
    session = Session()
    
    # Create the database if it doesn't already exist
    if not os.path.exists('./' + db_name):    
        IssueTrackerDataModel.create_db_tables(my_db)

    # The following regular expression will select all files that conform to 
    # the file naming format Issue*.txt. Build a list of all datafiles that match
    # the naming format within the directory passed in via command line 
    # arguments.
    file_regex = re.compile('Issue[a-zA-Z0-9_-]+.txt')
    files = get_files(session, db_name, input_dir, file_regex, recursive, test)
    
    # Process data files
    for data_filename in files:
        print 'processing %s'%data_filename
        
        # Initialize the file_attributes dictionary in preparation for the
        # parsing of the data file
        issue_attributes = {}
        
        # Parse the data file, storing all the information in the file_attributes
        # dictionary
        FileParser.FileParser(data_filename).parse(issue_attributes)
        IssueTrackerDataModel.addProcessedFile(session, data_filename)

        IssueTrackerDataModel.addIssueFromAttributes(session, issue_attributes)
        
    
def process_debrief_files(db_name, input_dir, recursive, test):

    # Initialize the database session connection
    db_connect='sqlite:///%s'%(db_name)
    my_db = create_engine(db_connect)
    Session = sessionmaker(bind=my_db)
    session = Session()
    
    # Create the database if it doesn't already exist
    if not os.path.exists('./' + db_name):    
        DebriefDataModel.create_db_tables(my_db)

    # The following regular expression will select all files that conform to 
    # the file naming format Issue*.txt. Build a list of all datafiles that match
    # the naming format within the directory passed in via command line 
    # arguments.
    file_regex = re.compile('Debrief[a-zA-Z0-9_-]+.txt')
    files = get_files(session, db_name, input_dir, file_regex, recursive, test)
    
    # Process data files
    for data_filename in files:
        print 'processing %s'%data_filename
        
        # Initialize the file_attributes dictionary in preparation for the
        # parsing of the data file
        issue_attributes = {}
        
        # Parse the data file, storing all the information in the file_attributes
        # dictionary
        FileParser.FileParser(data_filename).parse(issue_attributes)
        DebriefDataModel.addProcessedFile(session, data_filename)

        DebriefDataModel.addIssueFromAttributes(session, issue_attributes)




  
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
        "-c","--create",action="store_true", dest="create", default=False,
        help='Create database schema')
    parser.add_option(
        "-D","--drop",action="store_true", dest="drop", default=False,
        help='Drop database schema')
    parser.add_option(
        "-r","--recalculate",action="store_true", dest="recalculate", default=False,
        help='Recalculate Team Scores')
    parser.add_option(
        "-p","--processfiles",action="store_true", dest="processfiles", default=False,
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

    # Create the database if requested through the command option    
    if options.create:
        DataModel.create_db_tables(my_db)

    # Dump the contents of the database if requested through the command option
    if options.drop:
        DataModel.dump_db_tables(my_db)

    #testfile = 'AttributeDefinitions-reboundrumble.xlsx'
    #testoutfile = 'attr2.csv'
    #AttributeDefinitions.xls_to_csv( testfile, testoutfile )
                
    # Build the attribute definition dictionary from the definitions csv file
    #attrdef_filename = './config/' + 'AttributeDefinitions-reboundrumble.csv'    
    attrdef_filename = './config/' + 'AttributeDefinitions-reboundrumble-clear.xlsx'    
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)


    if options.processfiles:
        competition = global_config['this_competition']
        process_files(session, db_name, attr_definitions, input_dir, options.recursive, options.test)
        dump_database_as_csv_file(session, attr_definitions, competition)
        
    if options.processissues:
        # process any accumulated issues files
        issues_db_name = global_config['issues_db_name']
        issues_input_dir = './static/Issues/'
        process_issue_files(issues_db_name, issues_input_dir, options.recursive, options.test)
        
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
                        response_code = put_file(request_path, msg_body)
                        client_sock.send('HTTP/1.1 ' + response_code + '\n')
                        files_received += 1
                    elif request_type == "GET":
                        file_list = get_file_list(request_path)
                        response_body = ''
                        for file_name in file_list:
                            response_body += file_name + '\n'
                        client_sock.send('HTTP/1.1 ' + '200 OK' + '\n\n')
                        client_sock.send(response_body + '\n')
        
                    print "Request Complete\n"
        
                    
            except IOError:
                pass
        
            print "disconnected"
        
            client_sock.close()
            
            # if we received files from the client, then go ahead and process them to keep
            # the database up to date in real time
            if files_received > 0:
                process_files(session, attr_definitions, input_dir, options.recursive, options.test)
                dump_database_as_csv_file(session, attr_definitions)

                process_issue_files(issues_db_name, issues_input_dir, options.recursive, options.test)


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
        
        
        

