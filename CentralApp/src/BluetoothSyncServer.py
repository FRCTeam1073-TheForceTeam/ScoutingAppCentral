'''
Created on Feb 5, 2014

@author: ken_sthilaire
'''

from threading import Thread
from bluetooth import *
import FileSync

class BluetoothSyncServer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.shutdown = False
    
    def shutdown(self):
        self.shutdown = True
        
    def run(self):
        server_sock=BluetoothSocket( RFCOMM )
        server_sock.bind(("",PORT_ANY))
        server_sock.listen(1)
        
        port = server_sock.getsockname()[1]
        
        uuid = "00001073-0000-1000-8000-00805F9B34F7"
        
        advertise_service( server_sock, "TTTService",
                           service_id = uuid,
                           service_classes = [ uuid, SERIAL_PORT_CLASS ],
                           profiles = [ SERIAL_PORT_PROFILE ] )
                           
        while not self.shutdown:
            
            print "Waiting for connection on RFCOMM channel %d" % port
        
            client_sock, client_info = server_sock.accept()
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
                    
                    if request_type == "PUT":
                        fullpath = './static/data/' + request_path
                        response_code = FileSync.put_file(fullpath, content_type, msg_body)
                        client_sock.send('HTTP/1.1 ' + response_code + '\r\n')
                        files_received += 1
                    elif request_type == "GET":
                        
                        fullpath = './static/data/' + request_path
                        if os.path.isdir(fullpath):
                            file_list = FileSync.get_file_list(fullpath)
                            response_body = ''
                            for file_name in file_list:
                                response_body += file_name + '\n'
                            client_sock.send('HTTP/1.1 ' + '200 OK' + '\r\n\r\n')
                            client_sock.send(response_body + '\r\n')
                        else:
                            response_body = FileSync.get_file(fullpath)
                            if response_body != '':
                                client_sock.send('HTTP/1.1 ' + '200 OK' + '\r\n\r\n')
                                client_sock.send(response_body + '\r\n\r\n')
                            else:
                                client_sock.send('HTTP/1.1 ' + '404 Not Found' + '\r\n\r\n')
                                    
                    print "Request Complete\n"
         
            except IOError:
                pass
        
            print "disconnected"
        
            client_sock.close()
            
        server_sock.close()
        print "Bluetooth Sync Server Terminated"

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
