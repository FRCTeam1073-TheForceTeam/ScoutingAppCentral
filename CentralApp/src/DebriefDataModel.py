#!/usr/bin/python
'''
Created on Feb 03, 2013

@author: ksthilaire
'''

from sqlalchemy import create_engine
from sqlalchemy import schema
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import sessionmaker
from optparse import OptionParser



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


class Debrief(Base):
    __tablename__ = 'debriefs'

    match_id         = Column(Integer)
    competition      = Column(String(32))
    summary          = Column(String(80))
    description      = Column(String(512))

class DebriefIssue(Base):
    __tablename__ = 'debrief_issues'
    
    match_id         = Column(Integer)
    competition      = Column(String(32))
    issue_id         = Column(String(32))
    priority         = Column(String(32))
       
class DebriefComment(Base):
    __tablename__ = "debrief_comments"

    match_id    = Column(Integer)
    competition = Column(String(32))
    data        = Column(String(1024))
    tag         = Column(String(64))
    submitter   = Column(String(32))
    
class ProcessedFiles(Base):
    __tablename__ = "processed_files"

    filename = Column(String(256), nullable=False)

def isFileProcessed(session, filename):
    
    file_list = session.query(ProcessedFiles).filter(ProcessedFiles.filename==filename).all()
    if len(file_list)>0:
        return True
    else:
        return False

def addProcessedFile(session, name):
    file_name = ProcessedFiles(filename=name)
    session.add(file_name)
    

def getDebriefComments(session, match_id):
    comments = session.query(DebriefComment).filter(DebriefComment.match_id==match_id).all()
    print str(comments)
    return comments
        
def getDebriefIssues(session, match_id):
    issues = session.query(DebriefIssue).filter(DebriefIssue.match_id==match_id).\
                           order_by(DebriefIssue.priority).all()
    print str(issues)
    return issues
        
def getDebriefIssue(session, match_id, priority):
    issues = session.query(DebriefIssue).filter(DebriefIssue.match_id==match_id).\
                                         filter(DebriefIssue.priority==priority).all()
    if len(issues) > 0:
        issue = issues[0]
    else:
        issue = None
    return issue
        
def getDebrief(session, match_id):
    debrief_list = session.query(Debrief).filter(Debrief.match_id==match_id).all()
    print str(debrief_list)
    if len(debrief_list) > 0:
        debrief = debrief_list[0]
    else:
        debrief = None
        
    return debrief

def getDebriefsInNumericOrder(session, max_debriefs=100):
    debriefList = session.query(Debrief).\
            order_by(Debrief.match_id).\
            all()    
    return debriefList

def addOrUpdateDebrief(session, match_id, competition, summary, description):

    debriefList = session.query(Debrief).filter(Debrief.match_id==match_id).\
                                         filter(Debrief.competition==competition)
    debrief = debriefList.first()
    if debrief:
        # debrief exists, so update it
        debrief.match_id = match_id
        debrief.competition = competition
        debrief.description = description
        debrief.summary = summary
    else:
        debrief = Debrief(match_id=match_id, competition=competition, 
                          summary=summary, description=description)
        session.add(debrief)
    print debrief.json()

def addOrUpdateDebriefIssue(session, match_id, competition, issue_id, priority): 

    issueList = session.query(DebriefIssue).filter(DebriefIssue.match_id==match_id).\
                                            filter(DebriefIssue.competition==competition).\
                                            filter(DebriefIssue.priority==priority)
    issue = issueList.first()
    if issue:
        # debrief exists, so update it
        issue.match_id = match_id
        issue.competition = competition
        issue.issue_id = issue_id
        issue.priority = priority
    else:
        issue = DebriefIssue(match_id=match_id, competition=competition, priority=priority,
                             issue_id=issue_id)
        session.add(issue)
        
    print issue.json()


def addOrUpdateDebriefComment(session, match_id, competition, submitter, tag, data): 

    commentList = session.query(DebriefComment).filter(DebriefComment.match_id==match_id).\
                                                filter(Debrief.competition==competition).\
                                                filter(DebriefComment.tag==tag)
    comment = commentList.first()
    if comment:
        # debrief exists, so update it
        comment.match_id = match_id
        comment.competition = competition
        comment.tag = tag
        comment.submitter = submitter
        comment.data = data
    else:
        comment = DebriefComment(match_id=match_id, competition=competition, tag=tag, 
                                 submitter=submitter, data=data)
        session.add(comment)
        
    print comment.json()

def addDebriefFromAttributes(session, debrief_attributes):
    try:
        match_id = debrief_attributes['Match']
        competition = debrief_attributes['Competition']
            
        if debrief_attributes.has_key('Match_Summary'):
            summary = debrief_attributes['Match_Summary']
        else:
            summary = ''
            
        if debrief_attributes.has_key('Description'):
            description = debrief_attributes['Description']
        elif debrief_attributes.has_key('Notes'):
            description = debrief_attributes['Notes']
        else:
            description = ''
        
        addOrUpdateDebrief(session, match_id, competition, summary, description)
        
        session.commit()
    except KeyError:
        raise Exception( 'Incomplete Debrief Record' )
    
        
def deleteAllProcessedFiles(session):
    p_list = session.query(ProcessedFiles).all()
    for item in p_list:
        session.delete(item)
    session.flush()
    
def deleteAllDebriefs(session):
    a_list = session.query(Debrief).all()
    for item in a_list:
        session.delete(item)
    session.flush()

def deleteAllDebriefComments(session):
    n_list = session.query(DebriefComment).all()
    for item in n_list:
        session.delete(item)
    session.flush()
    
def deleteDebriefCommentsByTag(session, match_id, tag):
    comments = session.query(DebriefComment).filter(DebriefComment.match_id==match_id).\
                                           filter(DebriefComment.tag==tag).\
                                           all()
    for item in comments:
        session.delete(item)
    session.flush()

def deleteDebriefCommentsByData(session, match_id, data):
    comments = session.query(DebriefComment).filter(DebriefComment.match_id==match_id).\
                                           filter(DebriefComment.data==data).\
                                           all()
    for item in comments:
        session.delete(item)
    session.flush()
        
def create_db_tables(my_db):
    Base.metadata.create_all(my_db)

if __name__ == '__main__':

    parser = OptionParser()

    # db options.
    parser.add_option(
        "-u","--user",dest="user", default='root', help='Database user name')
    parser.add_option(
        "-d","--db",dest="db", default='issues2013', help='Database name')
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



