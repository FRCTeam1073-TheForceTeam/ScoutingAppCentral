'''
Created on Feb 5, 2014

@author: ken_sthilaire
'''

from threading import Thread

'''
    Attempt to import the bluetooth drivers, allow the import
    to be unsuccessful
'''
try:
    import lightblue
except:
    try:
        from bluetooth import *
    except:
        print "Bluetooth drivers NOT installed"
        pass

import FileSync
import WebCommonUtils
import WebEventData
import WebTeamData
import WebAttributeDefinitions
 
class ClientThread(Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        Thread.__init__(self)
 
    def run(self):
        self._target(*self._args)
 
class BluetoothSyncServer(Thread):
    def __init__(self, global_config):
        Thread.__init__(self)
        self.shutdown = False
        self.global_config = global_config
    
    def terminate(self):
        self.shutdown = True
        
    def run(self):
        
        '''
        server_sock=BluetoothSocket( RFCOMM )
        server_sock.bind(("",PORT_ANY))
        server_sock.listen(1)
        
        port = server_sock.getsockname()[1]
        
        uuid = "00001073-0000-1000-8000-00805F9B34F7"
        
        advertise_service( server_sock, "TTTService",
                           service_id = uuid,
                           service_classes = [ uuid, SERIAL_PORT_CLASS ],
                           profiles = [ SERIAL_PORT_PROFILE ] )
        '''
        
        server_sock = lightblue.socket()
        server_sock.bind(("", 0))    # bind to 0 to bind to a dynamically assigned channel
        server_sock.listen(1)
        lightblue.advertise("TTTService", server_sock, lightblue.RFCOMM)
        port = server_sock.getsockname()[1]
        print "Advertised and listening on channel %d..." % server_sock.getsockname()[1]
        
                           
        while not self.shutdown:
            
            print "Waiting for connection on RFCOMM channel %d" % port
        
            client_sock, client_info = server_sock.accept()
            
            client_thread = ClientThread(self.processClientConnection, client_sock, client_info)
            client_thread.start()
            #client_thread.join()

        server_sock.close()
        print "Bluetooth Sync Server Terminated"


    def processClientConnection( self, client_sock, client_info ):            
            print "Accepted connection from ", client_info
    
            files_received = 0
        
            try:
                while True:                  
                    msg_header, msg_body, content_type = self.read_request( client_sock )
                    if len(msg_header) == 0:
                        break
                    
                    print "Message Header: %s" % msg_header
                    print "Message Body Length: %d" % len(msg_body)
                        
                    msg_header_lines = msg_header.splitlines()
                    request_type, request_path = msg_header_lines[0].split(' ',1)
                    
                    print "Request Type: %s" % request_type
                    print "Request Path: %s" % request_path
    
                    request_complete = False
                    
                    # retrieve any params attached to the requested entity
                    params_offset = request_path.find('?')
                    if params_offset != -1:
                        request_params = request_path[params_offset:]
                        request_params = request_params.lstrip('?')
                        request_path = request_path[0:params_offset]
                    
                    request_path = request_path.lstrip('/')
    
                    # if the requested path starts with 'static', then let's assume that
                    # the request knows the full path that it's looking for, otherwise, 
                    # we will prepend the path with the path to the data directory
                    if request_path.startswith('static'):
                        fullpath = './' + request_path
                    else:                                        
                        fullpath = './static/data/' + request_path
                                        
                    if request_type == "PUT":
                        
                        # make sure that the destination directory exists
                        if not os.path.exists(os.path.dirname(fullpath)):
                            os.makedirs(os.path.dirname(fullpath))
                            
                        response_code = FileSync.put_file(fullpath, content_type, msg_body)
                        client_sock.send('HTTP/1.1 ' + response_code + '\r\n')
                        files_received += 1
                        
                    elif request_type == "POST":
                            
                        response_code = "400 Bad Request"
                        path_elems = request_path.split('/')
                        if len(path_elems) >= 2:
                            comp_season_list = WebCommonUtils.split_comp_str(path_elems[0])
                            if comp_season_list != None:
                                result = False
                                error = False
                                
                                # for the sync of event and team data, the URI path is of the following
                                # format /Sync/<comp>/EventData/[TeamData/]. if just EventData is provided,
                                # then the event data is regenerated, if TeamData is provided, then both
                                # the event data and team data is regenerated
                                if len(path_elems) >= 2 and path_elems[1] == 'EventData':
                                    result = WebEventData.update_event_data_files( self.global_config,  
                                                                                   comp_season_list[1], 
                                                                                   comp_season_list[0], 
                                                                                   path_elems[1] )
                                    if result == True:
                                        result = WebTeamData.update_team_event_files( self.global_config,  
                                                                                   comp_season_list[1], 
                                                                                   comp_season_list[0], 
                                                                                   path_elems[1] )
                                    if result == True:
                                        result = WebAttributeDefinitions.update_event_data_files( self.global_config,  
                                                                                   path_elems[1] )
                                    if result == False:
                                        error = True
                                        
                                if len(path_elems) >= 3 and path_elems[2] == 'TeamData' and error is False:
                                    try:
                                        team = path_elems[3]
                                        if team == '':
                                            team = None
                                    except:
                                        team = None
                                        
                                    result = WebTeamData.update_team_data_files( self.global_config,  
                                                                               comp_season_list[1], 
                                                                               comp_season_list[0], 
                                                                               path_elems[2], team )
                                    
                                if result == True:
                                    response_code = "200 OK"
    
                        client_sock.send('HTTP/1.1 ' + response_code + '\r\n')
                        
                    elif request_type == "GET":
                                                
                        # Parse any params attached to this GET request
                        params = request_params.split(';')
                        for param in params:
                            # split the parameter into the tag and value
                            parsed_param = param.split('=')
                            tag = parsed_param[0]
                            value = parsed_param[1]
                            
                            # process the parameter
                        
                        # check to see if the requested path exists. We may need to handle that
                        # condition separately, treating non-existent directories as empty (as
                        # opposed to sending a 404 not found.
                        # TODO: update the client side to handle the 404 not found as an empty directory
                        #       and then update this block to send the 404 in all cases.
                        if not os.path.exists(fullpath):
                            if request_path[-1] == '/':
                                # if the requested path refers to a directory, let's return an empty
                                # response indicating that there are no files in that directory
                                client_sock.send('HTTP/1.1 ' + '200 OK' + '\r\n')
                                client_sock.send('Content-Length: 0\r\n')
                                client_sock.send('\r\n\r\n')
                            else:
                                client_sock.send('HTTP/1.1 ' + '404 Not Found' + '\r\n\r\n')
                            request_complete = True
                                
                        if not request_complete:
                            if os.path.isdir(fullpath):
                                file_list = FileSync.get_file_list(fullpath)
                                response_body = ''
                                for file_name in file_list:
                                    response_body += file_name + '\n'
                                client_sock.send('HTTP/1.1 ' + '200 OK' + '\r\n')
                                client_sock.send('Content-Length: %d\r\n' % len(response_body))
                                client_sock.send('\r\n')
                                client_sock.send(response_body + '\r\n')
                            else:
                                response_body = FileSync.get_file(fullpath)
                                if response_body != '':
                                    client_sock.send('HTTP/1.1 ' + '200 OK' + '\r\n')
                                    client_sock.send('Content-Length: %d\r\n' % len(response_body))
                                    client_sock.send('\r\n')
                                    client_sock.send(response_body + '\r\n')
                                else:
                                    client_sock.send('HTTP/1.1 ' + '404 Not Found' + '\r\n\r\n')
                                    
                    print "Request Complete\n"
         
            except IOError:
                pass
        
            print "disconnected"
        
            client_sock.close()
    
    
    def read_request(self, client_sock):
        content_length = 0
        content_type = 'unknown'
        msg_header = ''
        msg_body = ''
        
        # loop here until we receive a request, or the connection gets closed
        connection_closed = False
        while not connection_closed and msg_header == '':
            # do an initial read, which will contain the request headers, then process the headers to 
            # determine the content type and length for the request
            msg_request = client_sock.recv(8192)
            if len(msg_request) == 0:
                connection_closed = True
            else:
                try:
                    # split the msg_request to separate the headers and the first part of the msg body
                    # we'll then scan the headers for the content length and type
                    msg_header, msg_body = msg_request.split('\r\n\r\n', 1)
                    msg_header_lines = msg_header.splitlines()
                    for line in msg_header_lines:
                        if line.startswith('Content-Length'):
                            content_length = int(line.split(' ', 1)[1])
                        if line.startswith('Content-Type'):
                            content_type = line.split(' ', 1)[1]
                except:
                    msg_header = ''
                    msg_body = ''
                    
        if content_length > 0:
            # read in the rest of the message body based on the content_length
            done = False
            while not done:
                if len(msg_body) < content_length:
                    buf = client_sock.recv(8192)
                    if len(buf) > 0:
                        msg_body += buf
                    else:
                        done = True
                else:
                    done = True
            
            # strip off any trailing empty lines
            if msg_body.endswith('\r\n\r\n'):
                msg_body = msg_body.replace('\r\n\r\n', '\r\n')        
            if msg_body.endswith('\n\r\n'):
                msg_body = msg_body.replace('\n\r\n', '\n')        
    
            # make sure that we received the entire file
            if len(msg_body) != content_length:
                print 'Expected %d bytes, Received %d bytes' % (content_length, len(msg_body))
            
        return msg_header, msg_body, content_type
