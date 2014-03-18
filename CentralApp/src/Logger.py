'''
Created on Feb 5, 2014

@author: ken_sthilaire
'''
import os
import logging.config

def create_default_logging_config(config_file_path, logfilename):
    fd = open(config_file_path, 'w')
    fd.write('#\n# Scouting App logging configuration file\n#\n')
    fd.write('\n')
    fd.write('[loggers]\nkeys=root,scoutingwebapp,scoutingapp,fileproc\n')
    fd.write('\n')
    fd.write('[handlers]\nkeys=logs,console,fileproclogs\n')
    fd.write('\n')
    fd.write('[formatters]\nkeys=normal\n')
    fd.write('\n')
    fd.write('[logger_root]\nlevel=DEBUG\nhandlers=console\n')
    fd.write('\n')
    fd.write('[logger_scoutingwebapp]\nlevel=DEBUG\nqualname=scouting.webapp\nhandlers=logs\npropagate=0\n')
    fd.write('\n')
    fd.write('[logger_scoutingapp]\nlevel=DEBUG\nqualname=scouting.app\nhandlers=logs\npropagate=0\n')
    fd.write('\n')
    fd.write('[logger_fileproc]\nlevel=DEBUG\nqualname=scouting.fileproc\nhandlers=fileproclogs\npropagate=0\n')
    fd.write('\n')
    fd.write('[handler_console]\nclass=StreamHandler\nlevel=DEBUG\nformatter=normal\nargs=(sys.stderr,)\n')
    fd.write('\n')
    fd.write('[handler_logs]\nclass=handlers.RotatingFileHandler\nargs=(\'%s\', \'a\', 100000000, 5)\nlevel=DEBUG\nformatter=normal\n' % logfilename)
    fd.write('\n')
    fd.write('[handler_fileproclogs]\nclass=handlers.RotatingFileHandler\nargs=(\'%s\', \'a\', 100000000, 5)\nlevel=DEBUG\nformatter=normal\n' % './logs/scouting_fileproc.log')
    fd.write('\n')
    fd.write('[formatter_normal]\nformat=%(asctime)s %(levelname)s %(message)s\n')
    fd.close()
    return

def init_logger(config_path, config_file, logger_name, logfilename='scouting.log'):
    config_file_path = config_path + '/' + config_file
    
    # make sure that the logging and config directories exist
    try: 
        os.makedirs(config_path)
    except OSError:
        if not os.path.isdir(config_path):
            raise

    logdir = './logs'
    try: 
        os.makedirs(logdir)
    except OSError:
        if not os.path.isdir(logdir):
            raise
    
    # create a default config file for the logger if none exists
    if not os.path.exists(config_file_path):
        create_default_logging_config(config_file_path, (logdir + '/' + logfilename))

    # create the logger
    logging.config.fileConfig(config_file_path)
    logger = logging.getLogger(logger_name)
    
    return logger

def get_logger(config_path, config_file, logger_name):
    config_file_path = config_path + '/' + config_file
    
    # make sure that the logging and config directories exist
    try: 
        os.makedirs(config_path)
    except OSError:
        if not os.path.isdir(config_path):
            raise

    logdir = './logs'
    try: 
        os.makedirs(logdir)
    except OSError:
        if not os.path.isdir(logdir):
            raise
    
    # create the logger
    logging.config.fileConfig(config_file_path)
    logger = logging.getLogger(logger_name)
    
    return logger
