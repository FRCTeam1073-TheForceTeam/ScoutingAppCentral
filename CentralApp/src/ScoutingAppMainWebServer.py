'''
Created on Dec 19, 2011

@author: ksthilaire
'''


import os
import re
import sys
import web
from web import form
import logging
import logging.config
import xlrd

import DataModel
import FileParser
import AttributeDefinitions
import UiGenerator
import AppGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from optparse import OptionParser

render = web.template.render('templates/')

#from sqlalchemy import create_engine

urls = (
    '/home', 'HomePage',    
    '/team/(.*)', 'TeamServer',
    '/score/(.*)', 'TeamScore',
    '/rankings', 'TeamRankings',
    '/test', 'TeamAttributes',
    '/teamdata/(.*)', 'TeamDataFiles',
    '/ScoutingData/(.*)', 'TeamDataFile',
    '/notes/(.*)', 'TeamNotes',
    '/genui', 'GenUi',
    '/config', 'SetConfig'
)


logging.config.fileConfig('config/logging.conf')
logger = logging.getLogger('scouting.webapp')

global_config = {'this_competition':None, 'other_competitions':None, 'db_name': 'scouting2013', \
                 'team_list':None, 'attr_definitions_file':'AttributeDefinitions-reboundrumble.xlsx'}
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

read_config('./config/ScoutingAppConfig.txt')
db_name = global_config['db_name']
attrdef_filename = './config/' + global_config['attr_definitions_file']
attr_definitions = AttributeDefinitions.AttrDefinitions()
   
    
# render = web.template.render('templates/')
webserver_app = web.application(urls, globals())

def get_datafiles(input_dir, pattern, recursive):
    '''Get list of files to be processed.

    Args:
        input_dir: Directory to search.
        pattern: Regular expression to use to filter files.
        recursive: Whether or not to recurse into input_dir.

    Returns:
        A list of files.
    '''
    
    file_list = []    
    
    if recursive:
        for root, dirs, files in os.walk(input_dir):
            logger.debug( 'Root: %s, Dirs: %s, Files: %s', root, dirs, files)
            for name in files:
                if pattern.match(name):
                    file_list.append(os.path.join(root, name))
    else:
        files = os.listdir(input_dir)
        logger.debug('Files: %s', files)
        for name in files:
            if pattern.match(name):
                file_list.append(os.path.join(input_dir, name))

    logger.debug('File List: %s', file_list)
    return file_list


class HomePage(object):

    def GET(self):
        db_connect='sqlite:///%s'%(db_name)
        my_db = create_engine(db_connect)
        Session = sessionmaker(bind=my_db)
        session = Session()
        
        result = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
        result += '<html>'
        result += '<head>'
        result += '<body>'
        result += '<h2> Team 1073 Scouting Application Home Page' + '</h3>'
        result += '<hr>'
        result += '<h3> Team Scoring Summary' + '</h3>'
        result += '<hr>'
        result += '<ul>'
        result += '<li><a href="/static/test/designer.html"> Team Rankings</a></li>'
        
        comp = global_config['this_competition']
        result += '<li><a href="/static/attr/' + comp + '.csv"> ' + comp + '.csv</a></li>'
        other_competitions = global_config['other_competitions'].split(',')
        for comp in other_competitions:
            if comp != global_config['this_competition']:
                result += '<li><a href="/static/attr/' + comp + '.csv"> ' + comp + '.csv</a></li>'
        result += '</ul>'
        result += '<hr>'
        result += '<h3> Team Links' + '</h3>'
        result += '<hr>'
        result += '<ul>'
        
        team_list_str = global_config['team_list']
        if team_list_str.count(',') > 0:
            team_list = team_list_str.split(',')
            #team_list.sort()
            for team in team_list:
                result += '<li><a href="/teamdata/' + team + '">' + 'Team ' + team + '</a></li>'
        elif team_list_str != None:
            result += '<li><a href="/teamdata/' + team_list_str + '">' + 'Team ' + team_list_str + '</a></li>'
        else:
            team_list = DataModel.getTeamsInNumericOrder(session, comp)
            for entry in team_list:
                result += '<li><a href="/teamdata/' + str(entry.team) + '">' + 'Team ' + str(entry.team) + '</a></li>'
        result += '</ul>'
        result += '</body>'
        result += '</html>'
        return result


class TeamServer(object):

    def GET(self, name):
        logger.debug( 'GET Team Server: %s', name )

        db_connect='sqlite:///%s'%(db_name)
        my_db = create_engine(db_connect)
        Session = sessionmaker(bind=my_db)
        session = Session()
        
        web.header('Content-Type', 'application/json')
        result = []
        result.append('{ attributes: [\n')
        comp = global_config['this_competition']
        team_attributes = DataModel.getTeamAttributes(session, name, comp)
        for attribute in team_attributes:
            result.append(attribute.json())
            result.append(',\n')
        if len(team_attributes) > 0:
            result = result[:-1]
        result.append(']}')
        return ''.join(result)

class TeamScore(object):

    def GET(self, name):
        logger.debug( 'GET Team Score: %s', name )

        db_connect='sqlite:///%s'%(db_name)
        my_db = create_engine(db_connect)
        Session = sessionmaker(bind=my_db)
        session = Session()
        
        web.header('Content-Type', 'application/json')
        result = []
        result.append('{ score: [')
        comp = global_config['this_competition']
        team_score = DataModel.getTeamScore(session, name, comp)
        for score in team_score:
            result.append(score.json())
            result.append(',\n')
        if len(team_score) > 0:
            result = result[:-1]
        result.append(']}')
        return ''.join(result)

class TeamNotes(object):

    def GET(self, name):
        logger.debug( 'GET Team Notes: %s', name )

        db_connect='sqlite:///%s'%(db_name)
        my_db = create_engine(db_connect)
        Session = sessionmaker(bind=my_db)
        session = Session()
        
        #web.header('Content-Type', 'application/json')
        notes_string = ''
        comp = global_config['this_competition']
        team_notes = DataModel.getTeamNotes(session, name)
        for note in team_notes:
            notes_string += note.data + '\n'
        return notes_string

class TeamRankings(object):

    def GET(self):
        db_connect='sqlite:///%s'%(db_name)
        my_db = create_engine(db_connect)
        Session = sessionmaker(bind=my_db)
        session = Session()
        
        web.header('Content-Type', 'application/json')
        result = []
        result.append('{ rankings: [\n')
        comp = global_config['this_competition']        
        team_rankings = DataModel.getTeamsInRankOrder(session, comp)
        for team in team_rankings:
            result.append(team.json())
            result.append(',\n')
        if len(team_rankings) > 0:
            result = result[:-1]
        result.append(']}')
        return ''.join(result)

class TeamAttributes(object):

    def GET(self):
        db_connect='sqlite:///%s'%(db_name)
        my_db = create_engine(db_connect)
        Session = sessionmaker(bind=my_db)
        session = Session()

        attr_definitions.parse(attrdef_filename)
        
        web.header('Content-Type', 'application/json')
        result = []
        result.append('{ attributes: [\n')
        comp = global_config['this_competition']        
        team_rankings = DataModel.getTeamsInRankOrder(session, comp)
        for team_entry in team_rankings:
            result.append("{ 'Team': " + str(team_entry.team))
            result.append(", 'Score': " + str(team_entry.score))
            team_attributes = DataModel.getTeamAttributesInOrder(session, team_entry.team, comp)
            for attribute in team_attributes:
                attr_def = attr_definitions.get_definition( attribute.attr_name )
                if ( attr_def['Include_In_Report'] == 'Yes'):
                    result.append( ", '" + attribute.attr_name + "': ")
                    if ( attr_def['Statistic_Type'] == 'Total'):
                        #result.append( str(attribute.cumulative_value) )
                        result.append( DataModel.mapValueToString(attribute.cumulative_value, attribute.all_values, attr_def, True) )
                    elif ( attr_def['Statistic_Type'] == 'Average'):
                        #result.append( str(attribute.avg_value) )
                        result.append( DataModel.mapValueToString(attribute.avg_value, attribute.all_values, attr_def, True) )
                    else:
                        #result.append( str(attribute.attr_value) )
                        result.append( DataModel.mapValueToString(attribute.attr_value, attribute.all_values, attr_def, True) )
                        
            result.append(' }')
            result.append(',\n')
        if len(team_rankings) > 0:
            result = result[:-1]
            result.append('\n')
        result.append(']}')
        return ''.join(result)

   
class TeamDataFiles(object):

    def GET(self, name):
        logger.debug( 'GET Team Data Files: %s', name )
        
        result = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
        result += '<html>'
        result += '<head>'
        result += '<body>'
        result += '<li><a href="/home">Home</a></li>'
        result += '<h2> Scouting Data File listing for Team ' + name + '</h2>'
        
        other_competitions_str = global_config['other_competitions']
        if other_competitions_str.count(',') > 0:
            other_competitions = other_competitions_str.split(',')
        else:
            other_competitions = (other_competitions_str)
            
        for comp in other_competitions:
            
            input_dir = './static/' + comp + '/ScoutingData/'
            pattern = 'Team' + name + '_' + '[a-zA-Z0-9_]*.txt'
            #file_regex = re.compile(pattern)
            datafiles = get_datafiles(input_dir, re.compile(pattern), False)
            
            input_dir = './static/' + comp + '/ScoutingPictures/'
            pattern = 'Team' + name + '_' + '[a-zA-Z0-9_]*.jpg|mp4'
            mediafiles = get_datafiles(input_dir, re.compile(pattern), False)
                        
            if len(datafiles) == 0 and len(mediafiles) == 0:
                continue
            
            result += '<h3> ' + comp + '</h3>'

            if len(datafiles) > 0:         
                result += '<hr>'
                result += '<ul>'
                result += '<h3>Pit and Match Data:</h3>'
                result += '<ul>'
                for filename in datafiles:
                    segments = filename.split('/')
                    basefile = segments[-1]
                    result += '<li><a href="' + filename.lstrip('.') + '">' + basefile + '</a></li>'
                result += '</ul>'
                #result += '<hr>'

            if len(mediafiles) > 0:         
                result += '<h3>Pictures and Videos:</h3>'
                result += '<ul>'
                for filename in mediafiles:
                    segments = filename.split('/')
                    basefile = segments[-1]
                    result += '<li><a href="' + filename.lstrip('.') + '">' + basefile + '</a></li>'
                result += '</ul>'
            result += '</ul>'
            
        result += '<h3> Notes for Team ' + name + '</h3>'
        result += '<hr>'
        result += '<ul>'
            
        db_connect='sqlite:///%s'%(db_name)
        my_db = create_engine(db_connect)
        Session = sessionmaker(bind=my_db)
        session = Session()
        comp = global_config['this_competition']        
        team_notes = DataModel.getTeamNotes(session, name, comp)
        for note in team_notes:
            result += '<li>' + note.data + '</li>'
        
        result += '</ul>'
        result += '</body>'
        result += '</html>'
        return result

class TeamDataFile(object):

    def GET(self, name):
        logger.debug( 'GET Team Data File: %s', name )
        
        filename = './static/' + global_config['this_competition'] + '/ScoutingData/' + name
        
        datafile = open( filename, "r" )
        result = datafile.read()
        
        return result

# Form definition and callback class for the user interface code generator
base_dir_label = "Base Project Directory:"
base_project_label = "Base Project Name:"
dest_dir_label = "Destination Project Directory:"
dest_project_label = "Destination Project Name:"
app_name_label = "Application Name:"
app_title_label = "Application Title:"
sheet_type_label = "Sheet Type:"
attr_defs_label = "Attributes Definition File:"
gen_action_label = 'Generate:'
myform = form.Form( 
    form.Textbox(base_dir_label, size=60),
    form.Textbox(base_project_label, size=60),
    form.Textbox(dest_dir_label, size=60),
    form.Textbox(dest_project_label, size=60),
    form.Textbox(app_name_label, size=60),
    form.Textbox(app_title_label, size=60),
    form.Dropdown(sheet_type_label, ['Pit', 'Match', 'Demo']), 
    form.Textbox(attr_defs_label,form.notnull,form.regexp('[\w_-]+\.xlsx', 'Must be .xlsx file'),size=60),
    form.Dropdown(gen_action_label, ['Complete App', 'UI Components', 'Base App']),
    form.Checkbox('mycheckbox', value='ischecked', checked=False)) 

class GenUi(object):
    def GET(self):
        
        form = myform()
        # make sure you create a copy of the form by calling it (line above)
        # Otherwise changes will appear globally
        return render.formtest(form)

    def POST(self):
        form = myform()
        
        if not form.validates(): 
            return render.formtest(form)
        else:
            # form.d.boe and form['boe'].value are equivalent ways of
            # extracting the validated arguments from the form.
            workspace_dir = 'D:\Documents and Settings\ksthilaire\Workspace'
            base_project_path = os.path.join(workspace_dir, form[base_dir_label].value)
            base_projectname = form[base_project_label].value
            dest_project_path = os.path.join(workspace_dir, form[dest_dir_label].value)
            dest_projectname = form[dest_project_label].value
            dest_activity_prefix = form[sheet_type_label].value
            dest_app_label = form[app_name_label].value
            dest_app_name = form[app_title_label].value
            attr_defs_file = './config/' + form[attr_defs_label].value
            
            generated_code_fragments = UiGenerator.gen_ui(attr_defs_file, \
                                                          dest_activity_prefix, \
                                                          create_fragment_file=True)
            
            AppGenerator.prepare_destination_project( base_project_path, base_projectname, dest_project_path, dest_projectname, \
                                 dest_activity_prefix, dest_app_name, dest_app_label )
    
            AppGenerator.update_generated_xml_code(dest_project_path, generated_code_fragments)
    
            AppGenerator.update_generated_java_code(base_projectname, dest_project_path, dest_activity_prefix, generated_code_fragments)

            
            return "User Interface Generated!\n\tSource Directory: %s\n\tDestination Directory: %s\n\tSheet Type: %s\n\tAttribute Definitions File: %s\n\tGenerate Action: %s" % \
                (form[base_dir_label].value, \
                 form[dest_dir_label].value, \
                 form[sheet_type_label].value, \
                 form[attr_defs_label].value, \
                 form[gen_action_label].value)    
            
# Form definition and callback class for the application configuration settings
cfg_this_comp_label = "Competition:"
cfg_attr_defs_label = "Attributes Definitions File:"
cfgform = form.Form( 
    form.Textbox(cfg_this_comp_label, size=60),
    form.Textbox(cfg_attr_defs_label, size=60))

class SetConfig(object):
    def GET(self):
        
        form = cfgform()
        # make sure you create a copy of the form by calling it (line above)
        # Otherwise changes will appear globally
        return render.cfg_form(form)

    def POST(self):
        form = cfgform()
        
        if not form.validates(): 
            return render.cfg_form_done(form)
        else:
            # form.d.boe and form['boe'].value are equivalent ways of
            # extracting the validated arguments from the form.
            global_config['this_competition'] = form[cfg_this_comp_label].value
            global_config['attr_definitions_file'] = form[cfg_attr_defs_label].value
            
            return render.cfg_form_done(form)

def generate_js_store_files():
    js_store_fragment_start = "Ext.define('MyApp.store.MyJsonStore', {\n" + \
                              "    extend: 'Ext.data.Store',\n" +\
                              "\n" +\
                              "    constructor: function(cfg) {\n" +\
                              "        var me = this;\n" +\
                              "        cfg = cfg || {};\n" +\
                              "        me.callParent([Ext.apply({\n" + \
                              "            autoLoad: true,\n" + \
                              "            storeId: 'MyJsonStore',\n" + \
                              "            proxy: {\n" + \
                              "                type: 'ajax',\n" + \
                              "                url: '/test',\n" + \
                              "                reader: {\n" + \
                              "                    type: 'json',\n" + \
                              "                    root: 'attributes'\n" + \
                              "                }\n" + \
                              "            },\n" + \
                              "            fields: [\n" + \
                              "                {\n" + \
                              "                    name: 'Team'\n" + \
                              "                },\n" + \
                              "                {\n" + \
                              "                    name: 'Score'\n" + \
                              "                }"

    js_store_fragment_end = "            ]\n" + \
                            "        }, cfg)]);\n" + \
                            "    }\n" + \
                            "});\n"

    js_panel_fragment_start="Ext.define('MyApp.view.ui.MyTabPanel1', {\n" + \
                            "    extend: 'Ext.panel.Panel',\n" + \
                            "\n" + \
                            "    height: 700,\n" + \
                            "    width: 1200,\n" + \
                            "\n" + \
                            "    initComponent: function() {\n" + \
                            "        var me = this;\n" + \
                            "\n" + \
                            "        Ext.applyIf(me, {\n" + \
                            "            items: [\n" + \
                            "                {\n" + \
                            "                    xtype: 'panel',\n" + \
                            "                    title: 'Scouting Application',\n" + \
                            "                    items: [\n" + \
                            "                        {\n" + \
                            "                            xtype: 'gridpanel',\n" + \
                            "                            height: 666,\n" + \
                            "                            width: 1200,\n" + \
                            "                            autoScroll: true,\n" + \
                            "                            title: 'Team Attributes',\n" + \
                            "                            store: 'MyJsonStore',\n" + \
                            "                            features: [\n" + \
                            "                                {\n" + \
                            "                                    ftype: 'grouping'\n" + \
                            "                                }\n" + \
                            "                            ],\n" + \
                            "                            columns: [\n" + \
                            "                                {\n" + \
                            "                                    dataIndex: 'Team',\n" + \
                            "                                    text: 'Team'\n" + \
                            "                                },\n" + \
                            "                                {\n" + \
                            "                                    dataIndex: 'Score',\n" + \
                            "                                    text: 'Score'\n" + \
                            "                                }"



    js_panel_fragment_end = "                            ],\n" + \
                            "                            viewConfig: {\n" + \
                            "\n" + \
                            "                            }\n" + \
                            "                        }\n" + \
                            "                    ]\n" + \
                            "                },\n" + \
                            "                {\n" + \
                            "                    xtype: 'panel',\n" + \
                            "                    title: 'Tab 2'\n" + \
                            "                },\n" + \
                            "                {\n" + \
                            "                    xtype: 'panel',\n" + \
                            "                    title: 'Tab 3'\n" + \
                            "                }\n" + \
                            "            ]\n" + \
                            "        });\n" + \
                            "\n" + \
                            "        me.callParent(arguments);\n" + \
                            "    }\n" + \
                            "});\n"
    
    attr_dict = attr_definitions.get_definitions()
    attr_order = [{} for i in range(len(attr_dict))]
    for key, value in attr_dict.items():
        offset = value['Column_Order']
        offset1 = float(offset)
        offset2 = int(offset1)
        
        attr_order[(int(float(value['Column_Order']))-1)] = value

    js_store_string = js_store_fragment_start
    js_panel_string = js_panel_fragment_start
    for attr_def in attr_order:
        if ( attr_def['Include_In_Report'] == 'Yes'):
            js_store_string += ",\n                {\n"
            js_store_string += "                    name: '" + attr_def['Name'] + "'\n"
            js_store_string += "                }"

            js_panel_string += ",\n                                {\n"
            js_panel_string += "                                    dataIndex: '" + attr_def['Name'] + "',\n"
            js_panel_string += "                                    text: '" + attr_def['Name'] + "'\n"
            js_panel_string += "                                }"
                        
            
    js_store_string += "\n"
    js_store_string += js_store_fragment_end
    js_panel_string += "\n"
    js_panel_string += js_panel_fragment_end
    
    outputFilename = './static/test/app/store/MyJsonStore.js'
    fo = open(outputFilename, "w+")
    fo.write( js_store_string )
    fo.close()

    outputFilename = './static/test/app/view/ui/MyTabPanel1.js'
    fo = open(outputFilename, "w+")
    fo.write( js_panel_string )
    fo.close()

    
if __name__ == "__main__":

    # command line options handling
    parser = OptionParser()
    
    parser.add_option(
        "-t","--test",action="store_true",dest="test",default=False,
        help="Processed test toggle")
    parser.add_option(
        "-u","--user",dest="user", default='root', 
        help='Database user name')
    parser.add_option(
        "-d","--db",dest="db_name", default='scouting2013', 
        help='Database name')
    parser.add_option(
        "-p","--password",dest="password", default='team1073',
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
   
    # Parse the command line arguments
    (options,args) = parser.parse_args()

    logger.debug("Running the Scouting App Web Server")

    # Determine which database type to initialize based on the passed in command
    # arguments    
    if options.dbtype == 'sqlite':
        db_connect='sqlite:///%s'%(options.db_name)
    elif options.dbtype == 'mysql':
        db_connect='mysql://%s:%s@localhost/%s'%(options.user, options.password, options.db_name)
    else:
        raise Exception("No Database Type Defined!")

    # Build the attribute definition dictionary from the definitions csv file
    attrdef_filename = './config/' + global_config['attr_definitions_file']
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)

    generate_js_store_files()
    
    webserver_app.run()

