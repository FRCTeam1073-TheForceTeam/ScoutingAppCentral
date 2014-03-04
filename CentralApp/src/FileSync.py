'''
Created on Feb 22, 2013

@author: Ken
'''
import os

def put_file( path, content_type, file_data):
    if content_type.find('text') == -1:
        mode = 'wb+'
    else:
        mode = 'w+'
    fd = open(path, mode)
    fd.write(file_data)
    fd.close()
    return '200 OK'
    
def get_file_list( path ):
    file_list = os.listdir(path)
    return file_list

def get_file(path):
    if path.find('.jpg') != -1:
        fd = open(path, 'rb')
        file_data = fd.read()
    elif path.find('.apk') != -1:
        fd = open(path, 'rb')
        file_data = fd.read()
    else:
        file_data = ''
        fd = open(path, 'r')
        for line in fd:
            file_data += line
    fd.close()
    return file_data
    
def get(global_config, path):
    fullpath = './static/' + path
    # if the path refers to a directory, then return the list of files in the directory
    # otherwise, return the contents of the file
    if os.path.isdir(fullpath):
        file_list = get_file_list(fullpath)
        response_body = ''
        for file_name in file_list:
            response_body += file_name + '\n'
    else:
        response_body = get_file(fullpath)
    return response_body

def put(global_config, path, content_type, msg_body):
    fullpath = './static/' + path
    put_file(fullpath, content_type, msg_body)


