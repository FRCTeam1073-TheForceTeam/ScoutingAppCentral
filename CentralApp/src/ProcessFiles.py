'''
Created on Feb 4, 2014

@author: ken_sthilaire
'''
import os
import re
import traceback
import time
import datetime
import sys

from optparse import OptionParser

import AttributeDefinitions
import ConfigUtils
import DbSession
import DataModel
import IssueTrackerDataModel
import DebriefDataModel
import FileParser
import Logger
import WebCommonUtils


def log_exception(logger, e):
    logger.debug('Exception Caught Processing Files: %s' % str(e) )
    traceback.print_exc(file=sys.stdout)
    exc_type, exc_value, exc_traceback = sys.exc_info()
    exception_info = traceback.format_exception(exc_type, exc_value,exc_traceback)
    for line in exception_info:
        line = line.replace('\n','')
        logger.debug(line)


'''Get list of files to be processed.

Args:
    input_dir: Directory to search.
    pattern: Regular expression to use to filter files.
    recursive: Whether or not to recurse into input_dir.

Returns:
    A list of files.
'''
def isFileProcessed(global_config, session, db_name, filepath):
    if db_name == (global_config['db_name'] + global_config['this_season']):
        is_processed = DataModel.isFileProcessed(session, filepath)
    elif db_name == (global_config['issues_db_name'] + global_config['this_season']):
        is_processed = IssueTrackerDataModel.isFileProcessed(session, filepath)
    elif db_name == (global_config['debriefs_db_name'] + global_config['this_season']):
        is_processed = DebriefDataModel.isFileProcessed(session, filepath)
        
    return is_processed
                                                 
def get_files(global_config, session, db_name, input_dir, pattern, recursive=True):    
    file_list = []    
        
    if recursive:
        for root, dirs, files in os.walk(input_dir):

            #print 'Root:', root, ' Dirs: ', dirs, ' Files:', files
            for name in files:
                if pattern.match(name):
                    if((isFileProcessed(global_config, session, db_name, os.path.join(root, name))) == False):
                        file_list.append(os.path.join(root, name))

    else:
        files = os.listdir(input_dir)
        #print 'Files:', files
        for name in files:
            if pattern.match(name):
                if((isFileProcessed(global_config, session, db_name, os.path.join(root, name))) == False):
                    file_list.append(os.path.join(input_dir, name))

    if len(file_list) > 0:
        print 'FileList:', file_list
        
    return file_list

  
def process_files(global_config, attr_definitions, input_dir, recursive=True):
    start_time = datetime.datetime.now()
    
    # Initialize the database session connection
    db_name  = global_config['db_name'] + global_config['this_season']
    session  = DbSession.open_db_session(db_name)
 
    some_files_processed = False
    
    # The following regular expression will select all files that conform to 
    # the file naming format Team*.txt. Build a list of all datafiles that match
    # the naming format within the directory passed in via command line 
    # arguments.
    file_regex = re.compile('Team[a-zA-Z0-9_]+.txt')
    files = get_files(global_config, session, db_name, input_dir, file_regex, recursive)
    
    print 'files retrieved, elapsed time - %s' % (str(datetime.datetime.now()-start_time))

    # Process data files
    for data_filename in files:
        try:
            process_file( global_config, session, attr_definitions, data_filename)
        except Exception, e:
            # log the exception but continue processing other files
            log_exception(global_config['logger'], e)

        # add the file to the set of processed files so that we don't process it again. Do it outside the
        # try/except block so that we don't try to process a bogus file over and over again.       
        DataModel.addProcessedFile(session, data_filename)
        some_files_processed = True
        
        # Commit all updates to the database
        session.commit()

    print 'files processed, elapsed time - %s' % (str(datetime.datetime.now()-start_time))
    
    if some_files_processed == True:    
        DataModel.dump_database_as_csv_file(session, global_config, attr_definitions)
    
        print 'database dumped, elapsed time - %s' % (str(datetime.datetime.now()-start_time))
    
    
    session.close()
        
def process_file(global_config, session, attr_definitions, data_filename):
    print 'processing %s'%data_filename
    
    # Initialize the file_attributes dictionary in preparation for the
    # parsing of the data file
    file_attributes = {}
    
    # Parse the data file, storing all the information in the file_attributes
    # dictionary
    FileParser.FileParser(data_filename).parse(file_attributes)

    # The team number can be retrieved from the Team attribute, one of the
    # mandatory attributes within the data file
    team = file_attributes['Team']
    
    # Also, extract the competition name, too, if it has been included in
    # the data file
    if file_attributes.has_key('Competition'):
        competition = file_attributes['Competition']
    else:
        competition = global_config['this_competition'] + global_config['this_season']

        if competition == None:
            raise Exception( 'Competition Not Specified!')

    DataModel.addTeamToEvent(session, team, competition)
    
    if file_attributes.has_key('Scouter'):
        scouter = file_attributes['Scouter']
    else:
        scouter = 'Unknown'
        
    if file_attributes.has_key('Match'):
        category = 'Match'
    else:
        if '_Pit_' in data_filename:
            category = 'Pit'
        else:
            category = 'Other'

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
                    DataModel.createOrUpdateAttribute(session, team, competition, category, attribute, value, attr_definition)
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
            
        if category == 'Match':
            try:
                match = file_attributes['Match']
                DataModel.createOrUpdateMatchDataAttribute(session, team, competition, match, scouter, attribute, value)
            except:
                err_str = 'ERROR: Match Data Attribute Could Not Be Processed: %s' % attribute
                traceback.print_exc(file=sys.stdout)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                exception_info = traceback.format_exception(exc_type, exc_value,exc_traceback)
                for line in exception_info:
                    line = line.replace('\n','')
                    global_config['logger'].debug(line)
                print err_str
            
    score = DataModel.calculateTeamScore(session, team, competition, attr_definitions)
    DataModel.setTeamScore(session, team, competition, score)

        
def remove_file_data(global_config, session, attr_definitions, data_filename, remove_from_processed_files=False):
    print 'removing data file: %s'%data_filename
    
    competition = global_config['this_competition'] + global_config['this_season']
    input_dir = './static/data/' + competition + '/ScoutingData/'
    filepath = input_dir+data_filename
    # Initialize the file_attributes dictionary in preparation for the
    # parsing of the data file
    file_attributes = {}
    
    # Parse the data file, removing all the information in the file_attributes
    # dictionary
    try:
        FileParser.FileParser(filepath).parse(file_attributes)
    except:
        raise ValueError('Error Opening File')

    # The team number can be retrieved from the Team attribute, one of the
    # mandatory attributes within the data file
    team = file_attributes['Team']
    
    # Also, extract the competition name, too, if it has been included in
    # the data file
    if file_attributes.has_key('Competition'):
        competition = file_attributes['Competition']
    else:
        competition = global_config['this_competition'] + global_config['this_season']

        if competition == None:
            raise Exception( 'Competition Not Specified!')
    
    # Loop through the attributes from the data file and post them to the
    # database
    for attribute, value in file_attributes.iteritems():
        if value is None:
            value = ''
        attr_definition = attr_definitions.get_definition(attribute)
        if attr_definition == None:
            raise ValueError( 'No Attribute Defined For Attribute: %s' % attribute )
        elif attr_definition['Database_Store']=='Yes':
            DataModel.deleteAttributeValue(session, team, competition, attribute, value, attr_definition, no_throw=True)
            
    if remove_from_processed_files:
        DataModel.deleteProcessedFile(session, filepath)

    score = DataModel.calculateTeamScore(session, team, competition, attr_definitions)
    DataModel.setTeamScore(session, team, competition, score)

def process_issue_files(global_config, input_dir, recursive=True):

    # Initialize the database session connection
    issues_db_name  = global_config['issues_db_name'] + global_config['this_season']
    debrief_db_name = global_config['debriefs_db_name'] + global_config['this_season']
    debrief_session = DbSession.open_db_session(debrief_db_name)
    issues_session  = DbSession.open_db_session(issues_db_name)

    # The following regular expression will select all files that conform to 
    # the file naming format Issue*.txt. Build a list of all datafiles that match
    # the naming format within the directory passed in via command line 
    # arguments.
    file_regex = re.compile('Issue[a-zA-Z0-9_-]+.txt')
    files = get_files(global_config, issues_session, issues_db_name, input_dir, file_regex, recursive)
    
    files.sort()
    
    # Process data files
    for data_filename in files:
        print 'processing %s'%data_filename
        try:
            # Initialize the file_attributes dictionary in preparation for the
            # parsing of the data file
            issue_attributes = {}
            
            # Parse the data file, storing all the information in the file_attributes
            # dictionary
            FileParser.FileParser(data_filename).parse(issue_attributes)
    
            issue = IssueTrackerDataModel.addIssueFromAttributes(issues_session, issue_attributes)
            if issue.debrief_key != None:
                match_str, issue_key = issue.debrief_key.split('_')
                competition = global_config['this_competition'] + global_config['this_season']

                DebriefDataModel.addOrUpdateDebriefIssue(debrief_session, int(match_str), 
                                                         competition,
                                                         issue.issue_id, issue_key)
        except Exception, e:
            # log the exception but continue processing other files
            log_exception(global_config['logger'], e)

        # add the file to the set of processed files so that we don't process it again. Do it outside the
        # try/except block so that we don't try to process a bogus file over and over again.       
        IssueTrackerDataModel.addProcessedFile(issues_session, data_filename)
            
    debrief_session.commit()
    issues_session.commit()
    debrief_session.close()
    issues_session.close()
    
    
def process_debrief_files(global_config, input_dir, recursive=True):

    # Initialize the database session connections
    issues_db_name  = global_config['issues_db_name'] + global_config['this_season']
    debrief_db_name = global_config['debriefs_db_name'] + global_config['this_season']
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
    files = get_files(global_config, debrief_session, debrief_db_name, input_dir, file_regex, recursive)
    
    # Process data files
    for data_filename in files:
        print 'processing %s'%data_filename
        try:
            # Initialize the debrief_attributes dictionary in preparation for the
            # parsing of the data file
            debrief_attributes = {}
            
            # Parse the data file, storing all the information in the attributes
            # dictionary
            FileParser.FileParser(data_filename).parse(debrief_attributes)
            DebriefDataModel.addDebriefFromAttributes(debrief_session, debrief_attributes)
            
            # Also, extract the competition name, too, if it has been included in
            # the data file
            
            if debrief_attributes.has_key('Competition'):
                competition = debrief_attributes['Competition']
                issue_base_name = WebCommonUtils.split_comp_str(competition)[0]
            else:
                competition = global_config['this_competition'] + global_config['this_season']
                issue_base_name = global_config['this_competition']

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
                
                if debrief_attributes.has_key('Issue1_Summary') or debrief_attributes.has_key('Issue1_Description'):
                    # look to see if there is already a debrief issue, and if so, do not attempt to create/update
                    # an issue, as there are already other issue files that would then conflict with this one
                    issue_key = 'Issue1'
                    if DebriefDataModel.getDebriefIssue(debrief_session, competition, match_id, issue_key) == None:
                        # if no summary is provided, then use the description as the summary. Likewise, if no description
                        # is provided then use the summary as the description. Keep in mind that we need at least the
                        # summary or description to be provided.
                        if debrief_attributes.has_key('Issue1_Summary'):
                            summary = debrief_attributes['Issue1_Summary']
                        else:
                            summary = debrief_attributes['Issue1_Description']
                        if debrief_attributes.has_key('Issue1_Description'):
                            description = debrief_attributes['Issue1_Description']
                        else:
                            description = debrief_attributes['Issue1_Summary']
                            
                        if debrief_attributes.has_key('Issue1_Priority'):
                            priority = debrief_attributes['Issue1_Priority']
                        else:
                            priority = 'Priority_3'
                            
                        if debrief_attributes.has_key('Issue1_Taskgroup'):
                            component = debrief_attributes['Issue1_Taskgroup']
                        else:
                            component = ''
                            
                        debrief_key = str(match_id) + '_' + issue_key
                    
                        issue_id = IssueTrackerDataModel.getIssueId(issues_session, issue_base_name)
                        issue = IssueTrackerDataModel.addOrUpdateIssue(issues_session, issue_id, summary, status, priority, 
                                 subgroup, component, submitter, owner, description, timestamp, debrief_key)
                        if issue != None:
                            issue.create_file('./static/data/%s/ScoutingData' % competition)
                        DebriefDataModel.addOrUpdateDebriefIssue(debrief_session, match_id, competition, issue_id, issue_key)
                    
                if debrief_attributes.has_key('Issue2_Summary') or debrief_attributes.has_key('Issue2_Description'):
                    # look to see if there is already a debrief issue, and if so, do not attempt to create/update
                    # an issue, as there are already other issue files that would then conflict with this one
                    issue_key = 'Issue2'
                    if DebriefDataModel.getDebriefIssue(debrief_session, competition, match_id, issue_key) == None:
                        # if no summary is provided, then use the description as the summary. Likewise, if no description
                        # is provided then use the summary as the description. Keep in mind that we need at least the
                        # summary or description to be provided.
                        if debrief_attributes.has_key('Issue2_Summary'):
                            summary = debrief_attributes['Issue2_Summary']
                        else:
                            summary = debrief_attributes['Issue2_Description']
                        if debrief_attributes.has_key('Issue2_Description'):
                            description = debrief_attributes['Issue2_Description']
                        else:
                            description = debrief_attributes['Issue2_Summary']
                            
                        if debrief_attributes.has_key('Issue2_Priority'):
                            priority = debrief_attributes['Issue2_Priority']
                        else:
                            priority = 'Priority_3'
                            
                        if debrief_attributes.has_key('Issue2_Taskgroup'):
                            component = debrief_attributes['Issue2_Taskgroup']
                        else:
                            component = ''

                        debrief_key = str(match_id) + '_' + issue_key
                        
                        issue_id = IssueTrackerDataModel.getIssueId(issues_session, issue_base_name)
                        issue = IssueTrackerDataModel.addOrUpdateIssue(issues_session, issue_id, summary, status, priority, 
                                 subgroup, component, submitter, owner, description, timestamp, debrief_key)
                        if issue != None:
                            issue.create_file('./static/data/%s/ScoutingData' % competition)
                        DebriefDataModel.addOrUpdateDebriefIssue(debrief_session, match_id, competition, issue_id, issue_key)
                    
                if debrief_attributes.has_key('Issue3_Summary') or debrief_attributes.has_key('Issue3_Description'):
                    # look to see if there is already a debrief issue, and if so, do not attempt to create/update
                    # an issue, as there are already other issue files that would then conflict with this one
                    issue_key = 'Issue3'
                    if DebriefDataModel.getDebriefIssue(debrief_session, competition, match_id, issue_key) == None:
                        # if no summary is provided, then use the description as the summary. Likewise, if no description
                        # is provided then use the summary as the description. Keep in mind that we need at least the
                        # summary or description to be provided.
                        if debrief_attributes.has_key('Issue3_Summary'):
                            summary = debrief_attributes['Issue3_Summary']
                        else:
                            summary = debrief_attributes['Issue3_Description']
                        if debrief_attributes.has_key('Issue3_Description'):
                            description = debrief_attributes['Issue3_Description']
                        else:
                            description = debrief_attributes['Issue3_Summary']
                            
                        if debrief_attributes.has_key('Issue3_Priority'):
                            priority = debrief_attributes['Issue3_Priority']
                        else:
                            priority = 'Priority_3'
                            
                        if debrief_attributes.has_key('Issue3_Taskgroup'):
                            component = debrief_attributes['Issue3_Taskgroup']
                        else:
                            component = ''

                        debrief_key = str(match_id) + '_' + issue_key
                    
                        issue_id = IssueTrackerDataModel.getIssueId(issues_session, issue_base_name)
                        issue = IssueTrackerDataModel.addOrUpdateIssue(issues_session, issue_id, summary, status, priority, 
                                 subgroup, component, submitter, owner, description, timestamp, debrief_key)
                        if issue != None:
                            issue.create_file('./static/data/%s/ScoutingData' % competition)
                        DebriefDataModel.addOrUpdateDebriefIssue(debrief_session, match_id, competition, issue_id, issue_key)
        except Exception, e:
            # log the exception but continue processing other files
            log_exception(global_config['logger'], e)

        # add the file to the set of processed files so that we don't process it again. Do it outside the
        # try/except block so that we don't try to process a bogus file over and over again.       
        DebriefDataModel.addProcessedFile(debrief_session, data_filename)
    
    issues_session.commit()
    debrief_session.commit()
    debrief_session.close()
    issues_session.close()


if __name__ == "__main__":

    # command line options handling
    parser = OptionParser()
    
    parser.add_option(
        "-l","--processloop",dest="processloop", default='0',
        help='Process Team Files')
    
    # Parse the command line arguments
    (options,args) = parser.parse_args()

    global_config = {}
    
    ConfigUtils.read_config(global_config, './config/ScoutingAppConfig.txt')

    logger = Logger.get_logger('./config', 'logging.conf', 'scouting.fileproc')
    global_config['logger'] = logger

    session = DbSession.open_db_session((global_config['db_name'] + global_config['this_season']), DataModel)

    counter = 0
    done = False

    while not done:
        try:
            global_config['logger'].debug( 'Scanning for new files to process' )
            print 'Scanning for new files to process'
            start_time = datetime.datetime.now()
            
            competition = global_config['this_competition'] + global_config['this_season']
            input_dir = './static/data/' + competition + '/ScoutingData/'
    
            if global_config['attr_definitions'] == None:
                global_config['logger'].debug( 'No Attribute Definitions, Skipping Process Files' )
                print 'No Attribute Definitions, Skipping Process Files'
            else:
                attrdef_filename = './config/' + global_config['attr_definitions']
                if os.path.exists(attrdef_filename):
                    attr_definitions = AttributeDefinitions.AttrDefinitions()
                    attr_definitions.parse(attrdef_filename)
                    
                    process_files(global_config, attr_definitions, input_dir)
                    process_issue_files(global_config, input_dir)
                    process_debrief_files(global_config, input_dir)
                    global_config['logger'].debug( 'Scan complete, elapsed time - %s' % (str(datetime.datetime.now()-start_time)) )
                    print 'Scan complete, elapsed time - %s' % (str(datetime.datetime.now()-start_time))
                else:
                    global_config['logger'].debug( 'Attribute File %s Does Not Exist' % attrdef_filename )
                    print 'Attribute File %s Does Not Exist' % attrdef_filename
        except Exception, e:
            global_config['logger'].debug('Exception Caught Processing Files: %s' % str(e) )
            print 'Exception Caught Processing Files: %s' % str(e)
            traceback.print_exc(file=sys.stdout)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            exception_info = traceback.format_exception(exc_type, exc_value,exc_traceback)
            for line in exception_info:
                line = line.replace('\n','')
                global_config['logger'].debug(line)
                print line
        
        if int(options.processloop) > 0:
            time.sleep(int(options.processloop))
        else:
            done = True




    