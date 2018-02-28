#!/usr/bin/python
'''
Created on Dec 27, 2011

@author: ksthilaire
'''

import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy import schema
from sqlalchemy import func
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import sessionmaker
from optparse import OptionParser

import json
import time
import DbSession
import AttributeDefinitions
import TbaIntf
import GoogleMapsIntf
import WebCommonUtils




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
        mystring = json.dumps(dict(self))
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

    team             = Column(Integer)
    competition      = Column(String(32))
    category         = Column(String(32))
    attr_name        = Column(String(32), nullable=False)
    attr_value       = Column(Float)
    attr_type        = Column(String(32))
    num_occurs       = Column(Integer)
    cumulative_value = Column(Float)
    avg_value        = Column(Float)
    all_values       = Column(String(8192))
    
class TeamInfo(Base):
    __tablename__ = 'info'
    
    team            = Column(Integer)
    nickname        = Column(String(64))
    fullname        = Column(String(256))
    rookie_season   = Column(Integer)
    website         = Column(String(64))
    motto           = Column(String(128))
    location        = Column(String(64))
    geo_location    = Column(String(128))
    first_competed  = Column(Integer)
    last_competed   = Column(Integer)

class MatchData(Base):
    __tablename__ = 'match_data'
    
    team             = Column(Integer)
    competition      = Column(String(32))
    match            = Column(String(32))
    scouter          = Column(String(32))
    attr_name        = Column(String(32), nullable=False)
    attr_value       = Column(String(64))
    
    
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
    
class EventInfo(Base):
    __tablename__ = 'eventinfo'
    
    event_key       = Column(String(16))
    event_code      = Column(String(16))
    name            = Column(String(128))
    short_name      = Column(String(64))
    alias           = Column(String(64))
    event_year      = Column(Integer)
    event_type      = Column(String(32))
    district_name   = Column(String(64))
    start_date      = Column(String(16))
    end_date        = Column(String(16))
    location        = Column(String(64))
    geo_location    = Column(String(128))
    

def isFileProcessed(session, filename):
    

    file_list = session.query(ProcessedFiles).filter(ProcessedFiles.filename==filename).all()
    if len(file_list)>0:
        return True
    else:
        return False

def addProcessedFile(session, name):
    file_name = ProcessedFiles(filename=name)
    session.add(file_name)
    
def deleteProcessedFile(session, name):
    result = session.query(ProcessedFiles).filter(ProcessedFiles.filename==name).all()
    for file_entry in result:
        session.delete(file_entry)
    
def addNotesEntry(session, teamnum, comp, notes, notestag):
    notes = NotesEntry(team=teamnum, competition=comp, data=notes, tag=notestag)
    session.add(notes)
    
def modifyNotesEntry(session, teamnum, comp, old_notes, new_notes, notestag):
    notes = session.query(NotesEntry).filter(NotesEntry.team==teamnum).\
                                      filter(func.lower(NotesEntry.competition)==func.lower(comp)).\
                                      filter(NotesEntry.data==old_notes)
    if notes:
        notes.data = new_notes
        notes.tag = notestag                                  
    
def deleteNotesEntry(session, teamnum, comp, old_notes, notestag):
    notes = session.query(NotesEntry).filter(NotesEntry.team==teamnum).\
                                      filter(func.lower(NotesEntry.competition)==func.lower(comp)).\
                                      filter(NotesEntry.data==old_notes).all()
    try:
        note = notes[0]
        session.delete(note)
    except:
        pass
    
def getTeamNotes(session, teamId, comp):
    notes = session.query(NotesEntry).filter(NotesEntry.team==teamId).\
                                      filter(func.lower(NotesEntry.competition)==func.lower(comp)).all()
    return notes
        
def getTeamNotesAsString(session, teamId, comp):
    note_string = ''
    notes = getTeamNotes(session, teamId, comp)
    for note in notes:
        note_string += note.data.replace(',', ' ').replace('  ',' ').replace('"','\'') + '\r'
    note_string = note_string.rstrip()
    return str(note_string)
        
def getTeamAttributes(session, teamId, comp):
    attrList = []
    try:
        attrList = session.query(TeamAttribute).filter(TeamAttribute.team==teamId).\
                                                filter(func.lower(TeamAttribute.competition)==func.lower(comp)).all()
        print str(attrList)
    except:
        pass
    return attrList

def getTeamAttributesInOrder(session, teamId, comp):
    attrList = []
    try:
        attrList = session.query(TeamAttribute).\
                filter(TeamAttribute.team==teamId).\
                filter(func.lower(TeamAttribute.competition)==func.lower(comp)).\
                order_by(TeamAttribute.attr_name).all()
    except:
        pass
    return attrList

def getTeamAttributesWithValue(session, comp, name, value, descending_order=True, max_teams=100):
    teamList = []
    try:
        if descending_order == True:
            teamList = session.query(TeamAttribute).\
                    filter(func.lower(TeamAttribute.competition)==func.lower(comp)).\
                    filter(TeamAttribute.attr_name==name).\
                    filter(TeamAttribute.all_values.contains(value)).\
                    all()    
        else:
            teamList = session.query(TeamAttribute).\
                    filter(func.lower(TeamAttribute.competition)==func.lower(comp)).\
                    filter(TeamAttribute.attr_name==name).\
                    filter(TeamAttribute.all_values.contains(value)).\
                    all()    
    except:
        pass
    return teamList

def getTeamAttributesInRankOrder(session, comp, name, descending_order=True, max_teams=100):
    teamList = []
    try:
        if descending_order == True:
            teamList = session.query(TeamAttribute).\
                    filter(func.lower(TeamAttribute.competition)==func.lower(comp)).\
                    filter(TeamAttribute.attr_name==name).\
                    order_by(TeamAttribute.cumulative_value.desc()).\
                    all()    
        else:
            teamList = session.query(TeamAttribute).\
                    filter(func.lower(TeamAttribute.competition)==func.lower(comp)).\
                    filter(TeamAttribute.attr_name==name).\
                    order_by(TeamAttribute.cumulative_value).\
                    all()    
    except:
        pass
    return teamList

def getTeamAttributesInAverageRankOrder(session, comp, name, descending_order=True, max_teams=100):
    teamList = []
    try:
        if descending_order == True:
            teamList = session.query(TeamAttribute).\
                    filter(func.lower(TeamAttribute.competition)==func.lower(comp)).\
                    filter(TeamAttribute.attr_name==name).\
                    order_by(TeamAttribute.avg_value.desc()).\
                    all()    
        else:
            teamList = session.query(TeamAttribute).\
                    filter(func.lower(TeamAttribute.competition)==func.lower(comp)).\
                    filter(TeamAttribute.attr_name==name).\
                    order_by(TeamAttribute.avg_value).\
                    all()
    except:
        pass
    return teamList

def getTeamAttribute(session, team, comp, name):
    try:
        attrList = session.query(TeamAttribute).filter(TeamAttribute.team==team).\
                                                filter(func.lower(TeamAttribute.competition)==func.lower(comp)).\
                                                filter(TeamAttribute.attr_name==name)
        return attrList.first()
    except:
        return None

def getTeamsInRankOrder(session, comp, descending_order=True, max_teams=100):
    teamList = []
    try:
        if descending_order == True:
            teamList = session.query(TeamRank).\
                filter(func.lower(TeamRank.competition)==func.lower(comp)).\
                order_by(TeamRank.score.desc()).\
                all()
        else:
            teamList = session.query(TeamRank).\
                filter(func.lower(TeamRank.competition)==func.lower(comp)).\
                order_by(TeamRank.score).\
                all()
    except:
        pass  

    return teamList

def getTeamsInNumericOrder(session, comp, max_teams=100):
    teamList = []
    try:
        teamList = session.query(TeamRank).\
                filter(func.lower(TeamRank.competition)==func.lower(comp)).\
                order_by(TeamRank.team).\
                all()    
    except:
        pass  
    return teamList

def getTeamScore(session, teamId, comp=None):
    teamScores = []
    try:
        if comp == None:
            teamScores = session.query(TeamRank).filter(TeamRank.team==teamId).all()
        else:
            teamScores =  session.query(TeamRank).filter(TeamRank.team==teamId).\
                                                  filter(func.lower(TeamRank.competition)==func.lower(comp)).all()
    except:
        pass
    return teamScores

def calculateTeamScore(session, teamId, comp, attr_defs):
    attributes = session.query(TeamAttribute).filter(TeamAttribute.team==teamId).\
                                              filter(func.lower(TeamAttribute.competition)==func.lower(comp)).all()
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
                                       filter(func.lower(TeamRank.competition)==func.lower(comp)).all()    
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
            if name.lower() == value.lower():
                if mapped_value is None:
                    mapped_value = int(token_val)
                else:
                    mapped_value += int(token_val)
                break
    if mapped_value == None:
        raise Exception('ERROR: No Mapping For Value: %s' % value)
    return mapped_value

def mapAllValuesToShortenedString( attr_def, all_values, need_quote=False, delim_str=':' ):
    if attr_def['Type'] == 'Map_Integer':
        value_list = all_values.split(':')
        unique_values = dict()
        for item in value_list:
            single_value_list = item.split(',')
            for single_item in single_value_list:
                try:
                    unique_values[single_item] += 1
                except KeyError:
                    unique_values[single_item] = 1
                    
        value_string = ''
        if ( need_quote == True ):
            value_string = "'"
        
        index = 0    
        for value in sorted(unique_values):
            if index > 0:
                value_string += delim_str
            value_string += '%s(%d)' % (value,unique_values[value])
            index += 1

        if ( need_quote == True ):
            value_string += "'"
        return value_string
    else:
        return all_values
            

def mapAllValuesToDict( attr_def, all_values, delim_str=':' ):
    value_dict = {}
    if attr_def['Type'] == 'Map_Integer':
        value_list = all_values.split(':')
        unique_values = dict()
        for item in value_list:
            single_value_list = item.split(',')
            for single_item in single_value_list:
                try:
                    unique_values[single_item] += 1
                except KeyError:
                    unique_values[single_item] = 1
        
        for value in sorted(unique_values):
            value_dict[value] = unique_values[value]

    return value_dict

    
def mapValueToString(value, all_values, attr_def, need_quote=False, delim_str='-'):
    if attr_def.has_key('Display_Numeric') and attr_def['Display_Numeric'] == 'Yes':
        return str(value)
    elif attr_def['Type'] == 'Map_Integer':
        value_list = all_values.split(':')
        unique_values = dict()
        for item in value_list:
            single_value_list = item.split(',')
            for single_item in single_value_list:
                try:
                    unique_values[single_item] += 1
                except KeyError:
                    unique_values[single_item] = 1
                    
        value_string = ''
        if ( need_quote == True ):
            value_string = "'"
        
        index = 0    
        for value in sorted(unique_values):
            if index > 0:
                value_string += delim_str
            value_string += '%s(%d)' % (value,unique_values[value])
            index += 1
            
        if ( need_quote == True ):
            value_string += "'"
        return value_string
    else:
        return str(value)
    
        
def createOrUpdateAttribute(session, team, comp, category, name, value, attribute_def):
    attrList = session.query(TeamAttribute).filter(TeamAttribute.team==team).\
                                            filter(func.lower(TeamAttribute.competition)==func.lower(comp)).\
                                            filter(TeamAttribute.attr_name==name)
    attr = attrList.first()
    attr_type = attribute_def['Type']
    date = datetime.datetime.now(); #gets the current date and time down to the microsecond
    
    if attribute_def['Name'] == 'Notes':
        addNotesEntry(session, team, comp, value, date)
    elif attribute_def['Type'] == 'String':
        if attr:
            attr.all_values += ':' + value
        else:
            attr = TeamAttribute(team=team, competition=comp,
                                 category = category, attr_name=name, 
                                 attr_type=attr_type, num_occurs=1,
                                 attr_value=0.0, cumulative_value=0.0, 
                                 avg_value=0.0, all_values=value)
            session.add(attr)
            
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
            attr = TeamAttribute(team=team, competition=comp,
                                 category = category, attr_name=name, 
                                 attr_type=attr_type, num_occurs=1,
                                 attr_value=attr_value, cumulative_value=attr_value, 
                                 avg_value=attr_value, all_values=value)
            session.add(attr)
            print attr.json()

def modifyAttributeValue(session, team, comp, name, old_value, new_value, attribute_def):
    attrList = session.query(TeamAttribute).filter(TeamAttribute.team==team).\
                                            filter(func.lower(TeamAttribute.competition)==func.lower(comp)).\
                                            filter(TeamAttribute.attr_name==name)
    attr = attrList.first()
    attr_type = attribute_def['Type']
    date = datetime.datetime.now(); #gets the current date and time down to the microsecond
    
    if attribute_def['Name'] == 'Notes':
        modifyNotesEntry(session, team, comp, old_value, new_value, date)
    elif attribute_def['Type'] == 'String':
        if attr: 
            if attr.all_values.find(old_value) != -1:
                attr.all_values = attr.all_values.replace(old_value,new_value,1)
            else:
                raise ValueError('Value Not Found')
        else:
            raise ValueError('Attribute Not Found')
    else:
        # make sure that the value itself has been applied to this attribute
        if attr:
            if attr.all_values.find(old_value) != -1:
                old_attr_value = convertValues(attr_type, old_value, attribute_def)
                new_attr_value = convertValues(attr_type, new_value, attribute_def)
            
                attr.attr_value = new_attr_value
                attr.cumulative_value -= old_attr_value
                attr.cumulative_value += new_attr_value
                attr.avg_value = attr.cumulative_value / attr.num_occurs
                attr.all_values = attr.all_values.replace(old_value,new_value,1)            
                print attr.json()
            else:
                raise ValueError('Value Not Found')
        else:
            raise ValueError('Attribute Not Found')

def deleteAttributeValue(session, team, comp, name, old_value, attribute_def, no_throw=False):
    attrList = session.query(TeamAttribute).filter(TeamAttribute.team==team).\
                                            filter(func.lower(TeamAttribute.competition)==func.lower(comp)).\
                                            filter(TeamAttribute.attr_name==name)
    attr = attrList.first()
    attr_type = attribute_def['Type']
    date = datetime.datetime.now(); #gets the current date and time down to the microsecond
    
    if attribute_def['Name'] == 'Notes':
        deleteNotesEntry(session, team, comp, old_value, date)
    elif attribute_def['Type'] == 'String':
        if attr:
            if attr.all_values.find(old_value) != -1:
                if attr.num_occurs == 1:
                    # if there is no other occurrences, then delete the attribute altogether
                    session.delete(attr)
                else:
                    # otherwise, remove this occurrence from the data set
                    attr.num_occurs -= 1
                    attr.all_values = attr.all_values.replace(old_value,'',1)
                    attr.all_values = attr.all_values.replace('::', ':',1)
                    attr.all_values = attr.all_values.lstrip(':')
                    attr.all_values = attr.all_values.rstrip(':')
            else:
                if no_throw is False:
                    raise ValueError('Value Not Found')
        else:
            if no_throw is False:
                raise ValueError('Attribute Not Found')
    else:
        # make sure that the value itself has been applied to this attribute
        if attr:
            if attr.all_values.find(old_value) != -1:
                if attr.num_occurs == 1:
                    # if there is no other occurrences, then delete the attribute altogether
                    session.delete(attr)
                else:
                    # otherwise, remove this occurrence from the data set
                    old_attr_value = convertValues(attr_type, old_value, attribute_def)                
                    attr.cumulative_value -= old_attr_value
                    attr.num_occurs -= 1
                    attr.avg_value = attr.cumulative_value / attr.num_occurs
                    attr.all_values = attr.all_values.replace(old_value,'',1)            
                    attr.all_values = attr.all_values.replace('::', ':',1)
                    attr.all_values = attr.all_values.lstrip(':')
                    attr.all_values = attr.all_values.rstrip(':')
                    
                    # set the attribute value to the last entered value
                    attr_value_list = attr.all_values.split(':')
                    attr_value_str = attr_value_list[-1]
                    if attr_value_str != '':
                        attr.attr_value = convertValues(attr_type, attr_value_str, attribute_def)
                    else:
                        attr.attr_value = 0.0
       
                    print attr.json()
            else:
                if no_throw is False:
                    raise ValueError('Value Not Found')
        else:
            if no_throw is False:
                raise ValueError('Attribute Not Found')


def createOrUpdateMatchDataAttribute(session, team, comp, match, scouter, name, value):
    attrList = session.query(MatchData).filter(MatchData.team==team).\
                                        filter(func.lower(MatchData.competition)==func.lower(comp)).\
                                        filter(MatchData.match==match).\
                                        filter(MatchData.attr_name==name)
    attr = attrList.first()    
    if attr:
        attr.attr_value = value
        attr.scouter = scouter
        print attr.json()
    else:
        attr = MatchData(team=team, competition=comp,
                         match=match, scouter=scouter,
                         attr_name=name, attr_value=value)
        session.add(attr)
        print attr.json()


def addOrUpdateTeamInfo(session, team_num, nickname, fullname, rookie_season, 
                        motto, location, website):
    
    team_list = session.query(TeamInfo).filter(TeamInfo.team==team_num)
    
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
        team = TeamInfo(team=team_num, nickname=nickname, fullname=fullname,
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
        url_str = '/api/v2/team/frc%d' % team
        try:
            team_data = TbaIntf.get_from_tba_parsed(url_str)

            team_info = setTeamInfoFromTba(session, team_data)
            
        except:
            team_info = None
            
    return team_info

def setTeamInfoFromTba(session, team_data):
    team = team_data['team_number']
    
    if team_data.has_key('nickname'):
        nickname=team_data['nickname']
    else:
        nickname='None'
    if team_data.has_key('name'):
        fullname=team_data['name']
    else:
        fullname='None'
        
    try:
        rookie_season=int(team_data['rookie_year'])
    except:
        rookie_season=1980
        
    if team_data.has_key('location'):
        location=team_data['location']
    else:
        location='Unknown'
    if team_data.has_key('motto'):
        motto=team_data['motto']
    else:
        motto='None'
    if team_data.has_key('website'):
        website=team_data['website']
    else:
        website='None'
        
    team_info = addOrUpdateTeamInfo(session, team, 
                        nickname, fullname, rookie_season,
                        motto, location, website)


def setTeamGeoLocation(session, team_key=None):
    
    teams = session.query(TeamInfo).filter(TeamInfo.team>0).all()
    
    geo_locations_found = 0
    for team in teams:
        # some teams in the database don't have complete information, so skip
        # those that don't list an address location
        if team.location != '' and team.geo_location is None:
            print 'Getting Geo Location For Team: FRC%d' % team.team
            try:
                # check to see if we haven't already obtained the geo location and
                # skip those that have already been set. The Google APIs have usage
                # limits so we're going to have to do this a piece at a time
                geo_location = GoogleMapsIntf.get_geo_location( team.location )
                
                # if the location is not found, let's massage the location and try again
                if geo_location is None:
                    if 'USA'  in team.location:
                        print 'Skipping team FRC%d From %s' & (team.team,team.location)
                    else:
                        split_location = team.location.split(',')
                        if len(split_location) > 2:
                            new_location = split_location[0] + ',' + split_location[-1]
                            geo_location = GoogleMapsIntf.get_geo_location( new_location )
                        
                #if len(geo_location) != 2:
                #    raise
                if geo_location is not None:
                    geo_location_json = json.dumps(geo_location)
                    team.geo_location = geo_location_json
                
                    print 'Geo Location For FRC%d: %s' % (team.team, geo_location_json)
                
                    geo_locations_found += 1
            
                    # commit each location as it is found so that we don't lose any
                    # should an exception be raised
                    session.commit()        
                    
            except:
                print 'Error Getting Geo Location For Team: FRC%d' % team.team
                #break
                
            # pause between each request to ensure that we don't exceed the rate in which we
            # call the Google APIs
            time.sleep(1)
            
    print 'Successful Geo Location Lookups: %d ' % geo_locations_found
    
    return

def setEventInfo( event_info, event_data):
    event_info.event_key       = event_data['key']
    event_info.event_code      = event_data['event_code']
    event_info.name            = event_data['name']
    event_info.short_name      = event_data['short_name']
    event_info.event_year      = event_data['year']
    event_info.event_type      = event_data['event_type_string']
    event_info.district_name   = event_data['event_district']
    event_info.start_date      = event_data['start_date']
    event_info.end_date        = event_data['end_date']
    event_info.location        = event_data['location']

def addOrUpdateEventInfo(session, event_data):
    event_key = event_data['key']
    
    event_info = session.query(EventInfo).filter(EventInfo.event_key==event_key).first()
    
    if event_info:
        setEventInfo(event_info, event_data)
    else:
        event_info = EventInfo()
        setEventInfo(event_info, event_data)        
        session.add(event_info)

    return event_info

def setEventsGeoLocation(session, event_key=None):
    
    events = session.query(EventInfo).all()
    
    for event in events:
        try:
            if 'Mexico' in event.location:
                print 'Location: %s' % event.location
                
            if event.geo_location is None or event.geo_location == 'null':
                print 'Getting Geo Location For Event: %d %s' % (event.event_year,event.name)
                geo_location = GoogleMapsIntf.get_geo_location( event.location )
                geo_location_json = json.dumps(geo_location)
                event.geo_location = geo_location_json
            
                session.commit()
                
                time.sleep(1)

        except:
            print 'Error Getting Geo Location For Event: %s' % event.name
            

    return

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
    else:
        attr_value = value
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

def recalculate_scoring(global_config, competition=None, attr_definitions=None):
    
    if competition is None:
        competition = global_config['this_competition'] + global_config['this_season']
        if competition == None or competition == '':
            raise Exception( 'Competition Not Specified!')

    # Build the attribute definition dictionary from the definitions csv file
    if global_config['attr_definitions'] == None:
        return
    
    if attr_definitions is None:
        attrdef_filename = WebCommonUtils.get_attrdef_filename(competition)
        if attrdef_filename is not None:
            attr_definitions = AttributeDefinitions.AttrDefinitions(global_config)
            attr_definitions.parse(attrdef_filename)
        else:
            return

    session = DbSession.open_db_session(global_config['db_name'] + global_config['this_season'])
    team_rankings = getTeamsInRankOrder(session, competition)
    for team_entry in team_rankings:
        score = calculateTeamScore(session, team_entry.team, competition, attr_definitions)
        setTeamScore(session, team_entry.team, competition, score)
    session.commit()
    dump_database_as_csv_file(session, global_config, attr_definitions, competition)
    session.remove()

def format_string_attr_for_csv(attr):
    attr_string = ''
    delim_str = '\r'
    value_list = attr.all_values.split(':')
    
    # Count up identical string values and display them only once with an occurence 
    # count if the string appears more than once
    unique_values = dict()
    for item in value_list:
        single_value_list = item.split(',')
        for single_item in single_value_list:
            # replace any embedded commas and strip off trailing whitespace
            single_item = single_item.replace(',', ' ').replace('  ',' ').rstrip()
            try:
                unique_values[single_item] += 1
            except KeyError:
                unique_values[single_item] = 1
    
    index = 0
    for value in sorted(unique_values):
        if index > 0:
            attr_string += delim_str
        if unique_values[value] == 1:
            attr_string += '%s' % value
        else:
            attr_string += '%s(%d)' % (value,unique_values[value])
        index += 1

    attr_string = attr_string.rstrip()
    return attr_string

    
def dump_database_as_csv_file(session, global_config, attr_definitions, competition=None):
    
    if competition == None:
        competition = global_config['this_competition'] + global_config['this_season']

    # read in the attribute definitions and sort them in the colum order
    attr_dict = attr_definitions.get_definitions()
    attr_order = [{} for i in range(len(attr_dict))]
    
    try:
        for key, value in attr_dict.items():
            attr_order[(int(float(value['Column_Order']))-1)] = value
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
            if (attr_def.has_key('Include_In_Report') is False) or (attr_def['Include_In_Report'] != 'No'):
                mystring += ',' + attr_def['Name']

                # for the checkbox control type, write out each checkbox item as a separate column
                if attr_def['Control'] == 'Checkbox':
                    attr_def['Columns'] = []
                    map_values = attr_def['Map_Values'].split(':')
                    for map_value in map_values:
                        item_name = map_value.split('=')[0]
                        attr_def['Columns'].append(item_name)
                        mystring += ',%s_%s' % (attr_def['Name'],item_name)
    except Exception, e:
        print 'Exception: %s' % str(e)

    mystring += ',Match_Count'
    mystring += '\n'
    fo.write( mystring )
    
    # Get the list of teams in rank order, then loop through teams and dump their stored
    # attribute values
    error_logged = False
    team_rankings = getTeamsInRankOrder(session, competition)
    for team_entry in team_rankings:
        
        # extract the number of matches that have been recorded for this team
        match_attribute = getTeamAttribute(session, team_entry.team, competition, 'Match')
        if match_attribute != None:
            num_samples = match_attribute.num_occurs
        else:
            num_samples = 1

        mystring = '%d,%d' % (team_entry.team,team_entry.score)

        # retrieve each attribute from the database in the proper order
        for attr_def in attr_order:
            try:
                if (attr_def.has_key('Include_In_Report') is False) or (attr_def['Include_In_Report'] != 'No'):
                    if attr_def['Name'] == 'Notes':
                        # We'll treat the notes separately, formatting the collected notes as a string with 
                        # embedded newlines between each note entry
                        mystring += ',"%s"' % getTeamNotesAsString(session, team_entry.team, competition)
                    else:
                        attribute = getTeamAttribute(session, team_entry.team, competition, attr_def['Name'])
                        if attribute == None:
                            # if the attribute doesn't exist, just put in an empty field so that the columns
                            # stay aligned
                            mystring += ','
                            # also, if the control type is checkbox, then also write empty columns for each checkbox item
                            if attr_def['Control'] == 'Checkbox':
                                columns = attr_def['Columns']
                                for column in columns:
                                    mystring +=','
                        elif attr_def['Type'] == 'String':
                            mystring += ',"%s"' % format_string_attr_for_csv(attribute)
                        else:
                            if ( attr_def['Statistic_Type'] == 'Total'):
                                mystring += ',' + mapValueToString(int(attribute.cumulative_value), attribute.all_values, attr_def)
                            elif ( attr_def['Statistic_Type'] == 'Average'):
                                if num_samples != 0 and attribute.category == 'Match':
                                    average_value = '%0.2f' % (attribute.cumulative_value/num_samples)
                                else:
                                    average_value = '%0.2f' % (attribute.avg_value)
                                mystring += ',' + mapValueToString(average_value, attribute.all_values, attr_def)
                            else:
                                mystring += ',' + mapValueToString(attribute.attr_value, attribute.all_values, attr_def)
        
                            # if the control type is checkbox, then also write out each checkbox item as a separate column
                            if attr_def['Control'] == 'Checkbox':
                                value_dict = {}
                                if attribute is not None:
                                    value_dict = mapAllValuesToDict(attr_def, attribute.all_values)
                                columns = attr_def['Columns']
                                for column in columns:
                                    try:
                                        if attr_def['Statistic_Type'] == 'Average':
                                            # for the average, show a fraction to be more accurate
                                            if num_samples != 0 and attribute.category == 'Match':
                                                value = '%0.2f' % (float(value_dict[column])/num_samples)
                                            else:
                                                value = '%0.2f' % (float(value_dict[column])/attribute.num_occurs)
                                        else:
                                            value = str(value_dict[column])                                
                                    except:
                                        value = ' '
        
                                    mystring += ',' + value
            except KeyError:
                if error_logged is False:
                    print( 'Unexpected row - check for gaps in the Column_Order within the spreadsheet')
                    error_logged = True
            except:
               print( 'Unexpected error creating CSV row for team %d scouting data' % team_entry.team )

        mystring += ',%d' % num_samples
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


