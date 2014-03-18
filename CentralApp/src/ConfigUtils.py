'''
Created on Mar 16, 2014

@author: ken_sthilaire
'''

import os

def read_config(config_dict, config_filename):
    if os.path.exists(config_filename):
        cfg_file = open(config_filename, 'r')
        for cfg_line in cfg_file:
            if cfg_line.startswith('#'):
                continue
            cfg_line = cfg_line.rstrip()
            if cfg_line.count('=') > 0:
                (attr,value) = cfg_line.split('=',1)
                config_dict[attr] = value
            else:
                # ignore lines that don't have an equal sign in them
                pass   
        cfg_file.close()

def write_config(config_dict, config_filename):
    cfg_file = open(config_filename, 'w+')
    for key, value in config_dict.iteritems():
        line = '%s=%s\n' % (key,value)
        cfg_file.write(line)
    cfg_file.close()
