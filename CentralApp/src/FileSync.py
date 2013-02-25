'''
Created on Feb 22, 2013

@author: Ken
'''
import os

def put_file( path, file_data):
    fd = open(path, 'w+')
    fd.write(file_data)
    fd.close()
    return '200 OK'
    
def get_file_list( path ):
    file_list = os.listdir(path)
    return file_list

def get_file(path):
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

def put(global_config, path, msg_body):
    fullpath = './static/' + path
    put_file(fullpath, msg_body)


