#!/usr/bin/python
'''
Created on Dec 27, 2011

@author: ksthilaire
'''

import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy import schema
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import sessionmaker
from optparse import OptionParser

import urllib2
import json

import DbSession
import AttributeDefinitions




class Base(object):
    '''
    Base class or all objects in the model.

    Provides basic property setting, and object to string conversion.
    Also provides methods for converting objects to json format.

    A little bit of python magic in the base, greatly reduces overall
    amount of code required to implement these features.

    This class extends the declarative_base() class supplied by
    SA ORM. The default constructor of declarative_base() automatically
    assigns instance members based on keyword arguments in the
    constructor. This means all model classes need to be
    instantiated with keywords arguments. (This helps with readability
    in any case.)
    '''

    # Common to all model classes.
    objectId = Column(Integer, primary_key=True)

    def __repr__(self):
        sb = []
        sb.append('<%s('%self.__class__.__name__)
        try:
            for c in self.__table__.columns:
                sb.append('"%s",'%getattr(self, c.name))
        except:
            # If this is a Base class instance, __table__
            # will not exist and we arrive here.
            pass

        sb.append(')>')

        return ''.join(sb)

    def todict(self):
        for x in self.__table__.columns:
            yield (x.name, getattr(self, x.name))

    def __iter__(self):
        return self.todict()

    def json(self):
        mystring = str(dict(self))
        mystring = mystring.replace(": u'", ": '")                
        return mystring


# Augment the sqlalchemy base.
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base(cls=Base)


class TeamRank(Base):
    __tablename__ = 'rankings'

    # Constructor parameters.
    team            = Column(Integer)
    competition     = Column(String(32))
    score           = Column(Float)

class TeamAttribute(Base):
    __tablename__ = 'attributes'

    # Constructor parameters.
    team             = Column(Integer)
    competition      = Column(String(32))
    attr_name        = Column(String(32), nullable=False)
    attr_value       = Column(Float)
    attr_type        = Column(String(32))
    num_occurs       = Column(Integer)
    cumulative_value = Column(Float)
    avg_value        = Column(Float)
    all_values       = Column(String(512))
    
class TeamInfo(Base):
    __tablename__ = 'info'
    
    team            = Column(Integer)
    nickname        = Column(String(64))
    fullname        = Column(String(256))
    rookie_season   = Column(Integer)
    website         = Column(String(64))
    motto           = Column(String(128))
    location        = Column(String(64))

class EventTeamList(Base):
    __tablename__ = 'eventteams'
    
    event           = Column(String(32))
    team            = Column(Integer)
                             
class ProcessedFiles(Base):
    __tablename__ = "processed_files"

    filename = Column(String(256), nullable=False)

class NotesEntry(Base):
    __tablename__ = "team_notes"

    team        = Column(Integer)
    competition = Column(String(32))
    data        = Column(String(1024))
    tag         = Column(String(64))
    
def isFileProcessed(session, filename):
    

    file_list = session.query(ProcessedFiles).filter(ProcessedFiles.filename==filename).all()
    if len(file_list)>0:
        return True
    else:
        return False

def addProcessedFile(session, name):
    file_name = ProcessedFiles(filename=name)
    session.add(file_name)
    
def addNotesEntry(session, teamnum, comp, notes, notestag):
    notes = NotesEntry(team=teamnum, competition=comp, data=notes, tag=notestag)
    session.add(notes)
    
def getTeamNotes(session, teamId, comp):
    notes = session.query(NotesEntry).filter(NotesEntry.team==teamId).\
                                      filter(NotesEntry.competition==comp).all()
    print str(notes)
    return notes
        
def getTeamAttributes(session, teamId, comp):
    attrList = session.query(TeamAttribute).filter(TeamAttribute.team==teamId).\
                                      filter(TeamAttribute.competition==comp).all()
    print str(attrList)
    return attrList

def getTeamAttributesInOrder(session, teamId, comp):
    attrList = session.query(TeamAttribute).\
            filter(TeamAttribute.team==teamId).\
            filter(TeamAttribute.competition==comp).\
            order_by(TeamAttribute.attr_name).all()
    return attrList

def getTeamAttribute(session, team, comp, name):
    attrList = session.query(TeamAttribute).filter(TeamAttribute.team==team).\
                                            filter(TeamAttribute.competition==comp).\
                                            filter(TeamAttribute.attr_name==name)
    return attrList.first()

def getTeamsInRankOrder(session, comp, max_teams=100):
    teamList = session.query(TeamRank).\
            filter(TeamRank.competition==comp).\
            order_by(TeamRank.score.desc()).\
            all()    
    return teamList

def getTeamsInNumericOrder(session, max_teams=100):
    teamList = session.query(TeamRank).\
            order_by(TeamRank.team).\
            all()    
    return teamList

def getTeamScore(session, teamId, comp):
    return session.query(TeamRank).filter(TeamRank.team==teamId).\
                                   filter(TeamRank.competition==comp).all()
        
def calculateTeamScore(session, teamId, comp, attr_defs):
    attributes = session.query(TeamAttribute).filter(TeamAttribute.team==teamId).\
                                              filter(TeamAttribute.competition==comp).all()
    total = 0.0
    for item in attributes:
        item_def = attr_defs.get_definition(item.attr_name)
        if item_def:
            weight = item_def['Weight']
            if not weight:
                weight = '0.0'
            # only include attributes with statistics types other than 'None'
            if item_def['Statistic_Type'] == 'Average':
                total += float(weight)*item.avg_value
            elif item_def['Statistic_Type'] == 'Total':
                total += float(weight)*item.cumulative_value

    return total
    
def setTeamScore(session, teamId, comp, score):
    teamList = session.query(TeamRank).filter(TeamRank.team==teamId).\
                                       filter(TeamRank.competition==comp).all()    
    if len(teamList)>0:
        team = teamList[0]
        team.team=teamId
        team.score=score
        print team.json()
    else:
        team = TeamRank(team=teamId, competition=comp, score=score)
        session.add(team)

def mapValueFromString(string_value, map_values):
    mapped_value = None
    values = string_value.split(',')
    for value in values:
        tokens = map_values.split(':')
        for token in tokens:
            name, token_val = token.split('=')
            if name == value:
                mapped_value = token_val
                break
    if mapped_value == None:
        raise Exception('ERROR: No Mapping For Value: %s' % value)
    return mapped_value

def mapValueToString(value, all_values, attr_def, need_quote=False):
    if attr_def['Type'] == 'Map_Integer':
        value_list = all_values.split(':')
        unique_values = []
        for item in value_list:
            single_value_list = item.split(',')
            for single_item in single_value_list:
                if len(unique_values) == 0:
                    unique_values.append( single_item )
                else:
                    found_match = False
                    for value in unique_values:
                        if ( value == single_item ):
                            found_match = True
                    if found_match == False:
                        unique_values.append( single_item )
        value_string = ''
        if ( need_quote == True ):
            value_string = "'"
        for index in range(len(unique_values)):
            if index == 0:
                value_string += unique_values[index]
            else:
                value_string += '-' + unique_values[index]
        if ( need_quote == True ):
            value_string += "'"
        return value_string
    else:
        return str(value)
    
        
def createOrUpdateAttribute(session, team, comp, name, value, attribute_def):
    attrList = session.query(TeamAttribute).filter(TeamAttribute.team==team).\
                                            filter(TeamAttribute.competition==comp).\
                                            filter(TeamAttribute.attr_name==name)
    attr = attrList.first()
    attr_type = attribute_def['Type']
    date = datetime.datetime.now(); #gets the current date and time down to the microsecond
    
    if attribute_def['Name'] == 'Notes':
        addNotesEntry(session, team, comp, value, date)
    else:
        attr_value = convertValues(attr_type, value, attribute_def)
    
        if attr:
            attr.attr_value = attr_value
            attr.num_occurs+=1
            attr.cumulative_value += attr_value
            attr.avg_value = attr.cumulative_value / attr.num_occurs
            attr.all_values += ':' + value
            print attr.json()
        else:
            attr = TeamAttribute(team=team, competition=comp, attr_name=name, 
                                 attr_type=attr_type, num_occurs=1,
                                 attr_value=attr_value, cumulative_value=attr_value, 
                                 avg_value=attr_value, all_values=value)
            session.add(attr)
            print attr.json()

def addOrUpdateTeamInfo(session, team, nickname, fullname, rookie_season, 
                        motto, location, website):
    
    team_list = session.query(TeamInfo).filter(TeamInfo.team==team)
    
    # should only be one team in the list
    team = team_list.first()
    if team:
        # team exists, so update it
        team.nickname = nickname
        team.fullname = fullname
        team.rookie_season = rookie_season
        team.motto = motto
        team.location = location
        team.website = website
    else:
        team = TeamInfo(team=team, nickname=nickname, fullname=fullname,
                        rookie_season=rookie_season, motto=motto,
                        location=location, website=website)
        session.add(team)
    session.commit()
    return team
        
def getTeamInfo(session, team):
    team_list = session.query(TeamInfo).filter(TeamInfo.team==team)
    
    # should only be one team in the list
    team_info = team_list.first()
    if not team_info:
        url_str = 'http://thefirstalliance.org/api/api.json.php?action=team-details&team-number=%s' % team
        try:
            team_data = urllib2.urlopen(url_str).read()
            team_data_dict = json.loads(team_data)
            team_data = team_data_dict['data']['data']
    
            if team_data.has_key('Team Nickname'):
                nickname=team_data['Team Nickname']
            else:
                nickname='None'
            if team_data.has_key('Team Name'):
                fullname=team_data['Team Name']
            else:
                fullname='None'
            if team_data.has_key('Rookie Season'):
                rookie_season=int(team_data['Rookie Season'])
            else:
                rookie_season=2013
            if team_data.has_key('Team Location'):
                location=team_data['Team Location']
            else:
                location='Unknown'
            if team_data.has_key('Team Motto'):
                motto=team_data['Team Motto']
            else:
                motto='None'
            if team_data.has_key('Team Website'):
                website=team_data['Team Website']
            else:
                website='None'
                
            team_info = addOrUpdateTeamInfo(session, team, 
                                nickname, fullname, rookie_season,
                                motto, location, website)
        except:
            team_info = None
            
    return team_info

def addTeamToEvent(session, event, team, commit=False):
    entry = None
    entry_list = session.query(EventTeamList).filter(EventTeamList.event==event).\
                                              filter(EventTeamList.team==team)
    team_entry = entry_list.first()
    if not team_entry:
        entry = EventTeamList(event=event, team=team)
        session.add(entry)
        if commit == True:
            session.commit()
    return entry
        
def getTeamList(session, event):
    team_list = session.query(EventTeamList).filter(EventTeamList.event==event).all()
    team_list.sort()
    return team_list
            
def convertValues(attr_type, value, attribute_def):
    if attr_type == 'Float':
        attr_value = float(value)
    elif attr_type == 'Integer':
        attr_value = float(value)
    elif attr_type == 'Map_Integer':
        attr_value = float(mapValueFromString(value, attribute_def['Map_Values']))
    return attr_value

def deleteAllProcessedFiles(session):
    p_list = session.query(ProcessedFiles).all()
    for item in p_list:
        session.delete(item)
    session.flush()
    
def deleteAllTeamAttributes(session):
    a_list = session.query(TeamAttribute).all()
    for item in a_list:
        session.delete(item)
    session.flush()

def deleteAllTeamNotes(session):
    n_list = session.query(NotesEntry).all()
    for item in n_list:
        session.delete(item)
    session.flush()
    
def deleteAllTeamRanks(session):
    r_list = session.query(TeamRank).all()
    for item in r_list:
        session.delete(item)
    session.flush()
    
def create_db_tables(my_db):
    Base.metadata.create_all(my_db)

def dump_db_tables(my_db):
    meta = schema.MetaData(my_db)
    meta.reflect()
    meta.drop_all()

def recalculate_scoring(global_config):
    session = DbSession.open_db_session(global_config['db_name'])
    competition = global_config['this_competition']
    if competition == None:
        raise Exception( 'Competition Not Specified!')

    # Build the attribute definition dictionary from the definitions csv file
    #attrdef_filename = './config/' + 'AttributeDefinitions-reboundrumble.csv'    
    attrdef_filename = './config/' + global_config['attr_definitions']    
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)

    team_rankings = getTeamsInRankOrder(session, competition)
    for team_entry in team_rankings:
        score = calculateTeamScore(session, team_entry.team, competition, attr_definitions)
        setTeamScore(session, team_entry.team, competition, score)
    session.commit()
    dump_database_as_csv_file(session, global_config, attr_definitions, competition)

def dump_database_as_csv_file(session, global_config, attr_definitions, competition=None):
    
    if competition == None:
        competition = global_config['this_competition']
    
    # read in the attribute definitions and sort them in the colum order
    attr_dict = attr_definitions.get_definitions()
    attr_order = [{} for i in range(len(attr_dict))]
    
    try:
        for key, value in attr_dict.items():
            attr_order[(int(float(value['Column_Order']))-1)] = value
            #attr_order[(int(value['Column_Order'])-1)] = value
    except Exception, e:
        print 'Exception: %s' % str(e)

    # open up the output filename that matches the database name
    path = './static/attr'
    if not os.path.exists(path):
        os.makedirs(path)
    outputFilename = path + '/' + competition + '.csv'
    fo = open(outputFilename, "w+")

    # Write out the column headers
    mystring = 'Team,Score'
    try:
        for attr_def in attr_order:
            if attr_def['Database_Store'] == 'Yes':
                mystring += ',' + attr_def['Name']
    except Exception, e:
        print 'Exception: %s' % str(e)

    mystring += '\n'
    fo.write( mystring )
    
    # Get the list of teams in rank order, then loop through teams and dump their stored
    # attribute values
    team_rankings = getTeamsInRankOrder(session, competition)
    for team_entry in team_rankings:
        mystring = str(team_entry.team) + ',' + str(team_entry.score)
        # retrieve each attribute from the database in the proper order
        for attr_def in attr_order:
            if attr_def['Database_Store'] == 'Yes':
                attribute = getTeamAttribute(session, team_entry.team, competition, attr_def['Name'])
                # if the attribute doesn't exist, just put in an empty field so that the columns
                # stay aligned
                if attribute == None:
                    mystring += ','
                elif ( attr_def['Statistic_Type'] == 'Total'):
                    #mystring += ',' + str(attribute.cumulative_value)
                    mystring += ',' + mapValueToString(attribute.cumulative_value, attribute.all_values, attr_def)
                elif ( attr_def['Statistic_Type'] == 'Average'):
                    #mystring += ',' + str(attribute.avg_value)
                    mystring += ',' + mapValueToString(attribute.avg_value, attribute.all_values, attr_def)
                else:
                    #mystring += ',' + str(attribute.attr_value)
                    mystring += ',' + mapValueToString(attribute.attr_value, attribute.all_values, attr_def)

        mystring += '\n'
        fo.write( mystring )
    fo.close()

# The run_test method contains just a bunch of little operations to test out how the various
# database mechanisms work...    
def run_test():
    Session = sessionmaker(bind=my_db)
    session = Session()
    
    myteam=1075
    mycomp='TestComp'
    myattr='Teleop_Points'
    myvalue='42'

    # Build the attribute definition dictionary from the definitions csv file
    attrdef_filename = 'AttributeDefinitions-reboundrumble.xlsx'    
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    attr_definitions.parse(attrdef_filename)
    attr_definition = attr_definitions.get_definition(myattr)
    attr_type = attr_definition['Type']
    attr_value = convertValues(attr_type, myvalue, attr_definition)

    # create a query that will search the database for all records that match the specified
    # team
    q1 = session.query(TeamRank).filter(TeamRank.team==myteam).filter(TeamRank.competition==mycomp)
    if q1:
        a = q1.first()
        # retrieve the first element that matches the team number. If there is one,
        # then we'll just print it out. If not, then we'll create an instance and 
        # add it to the database
        if a: 
            print str(a)
            print a.json()
        else:
            a1 = TeamRank(team=myteam, competition=mycomp, score=42.0)
            print str(a1)
            print a1.json()
            session.add(a1)

    # create a query that retrieves the first record that matches the team and attribute
    # if the attribure is found, then modify it in some way and store the new values
    # if the attribute is not found, then create an instance and add it to the
    # database
    q2 = session.query(TeamAttribute).filter(TeamAttribute.team==myteam and TeamAttribute.competition==mycomp and TeamAttribute.attr_name==myattr)
    if q2:
        b = q2.first()
        if b:
            b.attr_value+=5
            b.num_occurs+=1
            print str(b)
            print b.json()
        else:
            b1 = TeamAttribute(team=myteam, competition=mycomp, attr_name=myattr, attr_value=attr_value, 
                               cumulative_value=attr_value, attr_type=attr_type, num_occurs=1, avg_value=attr_value,
                               all_values=myvalue)
            print str(b1)
            print b1.json()
            session.add(b1)

    # retrieve a list of all the attributes from the database for the specified team using a 
    # utility method and print them out          
    myteam=1073
    allAttr = getTeamAttributes( session, myteam, mycomp )
    for d in allAttr:
        print d.json()        

    # given that same list, find a specific attribute in the list and update it
    # this loop construct is a nested for loop in one line...
    attr = next((i for i in allAttr if i.attr_name == myattr), None)
    if attr is not None:
        # attribute is found, so update the attribute with the new values
        attr.attr_value+=5
        attr.num_occurs+=1
        print attr.json()
    else:
        # attribute is not found, so create a new instance and add it to the database
        attr = TeamAttribute(team=myteam, competition=mycomp, attr_name=myattr, attr_value=attr_value, 
                             cumulative_value=attr_value, attr_type=attr_type, num_occurs=1, avg_value=attr_value,
                             all_values=myvalue)
        session.add(attr)
        print attr.json()
        
    # retrieve an ordered list of all teams in descending order (#1 team is first)
    rankList = getTeamsInRankOrder(session, mycomp)      
    for t in rankList:
        print t.json()        
    
    # exercise the attribute create/update utility method
    if (attr_definition['Database_Store']=='Yes'):
        createOrUpdateAttribute(session, myteam, mycomp, myattr, myvalue, attr_definition)
                    
    session.commit()


if __name__ == '__main__':

    parser = OptionParser()

    # db options.
    parser.add_option(
        "-u","--user",dest="user", default='root', help='Database user name')
    parser.add_option(
        "-d","--db",dest="db", default='test', help='Database name')
    parser.add_option(
        "-p","--password",dest="password", default='team1073',
        help='Database password')

    # action options.
    parser.add_option(
        "-t","--test",action="store_true", dest="test", default=False,
        help='Run simple tests')
    parser.add_option(
        "-b","--dbtype",dest="dbtype", default='sqlite',
        help='Select database type (mysql or sqlite')
    parser.add_option(
        "-c","--create",action="store_true", dest="create", default=False,
        help='Create database schema')
    parser.add_option(
        "-D","--drop",action="store_true", dest="drop", default=False,
        help='Drop database schema')
   
    # parse command line.
    (options,args) = parser.parse_args()

    # run!
    if options.dbtype == 'sqlite':
        db_connect='sqlite:///%s'%(options.db)
    elif options.dbtype == 'mysql':
        db_connect='mysql://%s:%s@localhost/%s'%(options.user, options.password, options.db)
    else:
        raise Exception("No Database Type Defined!")

    my_db = create_engine(db_connect)

    if options.create:
        Base.metadata.create_all(my_db)

    # Dump the contents of the database if requested through the command option
    if options.drop:
        dump_db_tables(my_db)

    if options.test:
        run_test()


