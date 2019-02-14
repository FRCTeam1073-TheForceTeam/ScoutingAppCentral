'''
Created on Feb 22, 2013

@author: Ken
'''
import os
import hashlib

def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.digest()

def strip_non_ascii(file_data):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in file_data if 0 < ord(c) < 127)
    return ''.join(stripped)

def get_file_checksum( filepath, hasher ):
    blocksize = 65536
    fd = open(filepath, 'rb')
    buf = fd.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fd.read(blocksize)
    return hasher.hexdigest()
    
def put_file( path, content_type, file_data):
    if content_type.find('text') == -1:
        mode = 'wb+'
    else:
        mode = 'w+'
    fd = open(path, mode)
    
    try:
        fd.write(file_data)
    except UnicodeEncodeError:
        # if writing a text file, try again stripping out any non-ascii characters
        if mode == 'w+':
            print 'Retrying after stripping non-ascii characters'
            fd.write(strip_non_ascii(file_data))
        else:
            raise
    fd.close()
    return '200 OK'

def get_file_list( path, ext=None, recurse=False, with_checksum=False ):
    files = []
    if recurse is False:
        dir_list = os.listdir(path)
        for file_name in dir_list:
            if not os.path.isdir(path + file_name):
                if with_checksum is True:
                    file_checksum = get_file_checksum( path + file_name, hashlib.md5() )
                else:
                    file_checksum = None
                if ext != None:
                    if file_name.endswith(ext):
                        if file_checksum is not None:
                            files.append(file_name + ':' + str(file_checksum))
                        else:
                            files.append(file_name)
                else:
                    if file_checksum is not None:
                        files.append(file_name + ':' + str(file_checksum))
                    else:
                        files.append(file_name)
    else:
        for dir_name, subdir_list, file_list in os.walk(path):
            dir_segments = dir_name.split('/')
            num_dir_segments = len(dir_segments)
            if num_dir_segments > 1 and dir_segments[-1].startswith('.'):
                continue
            for file_name in file_list:
                if file_name.startswith('.'):
                    continue
                file_path = os.path.join(dir_name, file_name).replace(path,'')
                # print('\t%s' % file_path)
                if with_checksum is True:
                    file_checksum = get_file_checksum( file_path, hashlib.md5() )
                else:
                    file_checksum = None
                if ext != None:
                    if file_name.endswith(ext):
                        if file_checksum is not None:
                            files.append(file_path + ':' + str(file_checksum))
                        else:
                            files.append(file_path)
                else:
                    if file_checksum is not None:
                        files.append(file_path + ':' + str(file_checksum))
                    else:
                        files.append(file_path)
    return files

def get_file(path):
    file_data = ''
    try:
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
    except:
        pass
    return file_data
    
def get(global_config, path, recurse=False, with_checksum=False):
    
    # if the requested path starts with 'static', then let's assume that
    # the request knows the full path that it's looking for, otherwise, 
    # we will prepend the path with the path to the data directory
    if path.startswith('static'):
        fullpath = './' + path
    else:                                        
        fullpath = './static/data/' + path
    
    # if the path refers to a directory, then return the list of files in the directory
    # otherwise, return the contents of the file
    if os.path.isdir(fullpath):
        file_list = get_file_list(fullpath, recurse=recurse, with_checksum=with_checksum)
        response_body = ''
        for file_name in file_list:
            response_body += file_name + '\n'
    else:
        response_body = get_file(fullpath)
    return response_body

def put(global_config, path, content_type, msg_body):
    
    # if the requested path starts with 'static', then let's assume that
    # the request knows the full path that it's looking for, otherwise, 
    # we will prepend the path with the path to the data directory
    if path.startswith('static'):
        fullpath = './' + path
    else:                                        
        fullpath = './static/data/' + path

    # make sure that the destination directory exists
    if not os.path.exists(os.path.dirname(fullpath)):
        os.makedirs(os.path.dirname(fullpath))
                            
    put_file(fullpath, content_type, msg_body)


