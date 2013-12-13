#!/usr/bin/python
'''
Created on Jan 04, 2013

@author: ksthilaire
'''

import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy import schema
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from optparse import OptionParser

import time

import DbSession

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


class IssueType(Base):
    __tablename__ = "issue_types"
    
    issue_type  = Column(String(32))
    max_id      = Column(Integer)    
    
class Issue(Base):
    __tablename__ = 'issues'

    # Constructor parameters.
    issue_id         = Column(String(32))
    summary          = Column(String(80))
    status           = Column(String(32))
    priority         = Column(String(32))
    subgroup         = Column(String(32))
    component        = Column(String(32))
    owner            = Column(String(32))
    description      = Column(String(512))
    submitter        = Column(String(32))
    debrief_key      = Column(String(32))
    timestamp        = Column(String(64))

    def create_file(self, basepath):
        basename = 'Issue_%s' % self.issue_id
        filename = '%s/%s.txt' % (basepath, basename)
        i = 1
        while os.path.isfile(filename):
            basename = 'Issue_%s_%03d' % (self.issue_id,i)
            filename = '%s/%s.txt' % (basepath, basename)
            i+=1
            
        fd = open(filename, 'w')
        
        issue_str  = 'Id:%s\n' % self.issue_id
        issue_str += 'Platform:%s\n' % self.issue_id.split('-')[0]
        issue_str += 'Summary:%s\n' % self.summary
        issue_str += 'Status:%s\n' % self.status
        issue_str += 'Priority:%s\n' % self.priority
        issue_str += 'Subgroup:%s\n' % self.subgroup
        issue_str += 'Component:%s\n' % self.component
        issue_str += 'Owner:%s\n' % self.owner
        issue_str += 'Submitter:%s\n' % self.submitter
        issue_str += 'Description:%s\n' % self.description
        issue_str += 'Timestamp:%s\n' % self.timestamp
        if self.debrief_key != None:
            issue_str += 'Debrief_Key:%s\n' % self.debrief_key
        
        issue_str = issue_str.rstrip('\n')    
        fd.write(issue_str)
        fd.close()

        
class IssueComment(Base):
    __tablename__ = "issue_comments"

    issue_id    = Column(String(32))
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
    
def getIssueComments(session, issue_id):
    comments = session.query(IssueComment).filter(IssueComment.issue_id==issue_id).\
                             order_by(IssueComment.tag).all()
    print str(comments)
    return comments
        
def getIssue(session, issue_id):
    issue_list = session.query(Issue).filter(Issue.issue_id==issue_id).all()
    print str(issue_list)
    if len(issue_list) > 0:
        issue = issue_list[0]
    else:
        issue = None
        
    return issue

def getIssuesByOwner(session, owner):
    issue_list = session.query(Issue).filter(Issue.owner==owner).all()
    print str(issue_list)
    return issue_list

def getIssuesByStatus(session, status):
    issue_list = session.query(Issue).filter(Issue.status==status).all()
    print str(issue_list)
    return issue_list

def getIssuesByPlatform(session, platform):
    issue_list = session.query(Issue).filter(Issue.issue_id.like(platform+'%')).all()
    print str(issue_list)
    return issue_list
    
def getIssuesByPlatformAndMultipleStatus(session, platform, status1, status2, order_by_priority=False):
    if order_by_priority:
        issue_list = session.query(Issue).filter(Issue.issue_id.like(platform+'%')).\
                filter(or_(Issue.status==status1, Issue.status==status2)).\
                order_by(Issue.priority).all()
    else:
        issue_list = session.query(Issue).filter(Issue.issue_id.like(platform+'%')).\
                filter(or_(Issue.status==status1, Issue.status==status2)).\
                order_by(Issue.issue_id).all()
    print str(issue_list)
    return issue_list
    
def getIssuesByMultipleStatus(session, status1, status2, order_by_priority=False):
    if order_by_priority:
        issue_list = session.query(Issue).filter(or_(Issue.status==status1, Issue.status==status2)).\
                order_by(Issue.priority).all()
    else:
        issue_list = session.query(Issue).filter(or_(Issue.status==status1, Issue.status==status2)).\
                order_by(Issue.issue_id).all()
                    
    print str(issue_list)
    return issue_list

def getIssuesInNumericOrder(session, max_issues=100):
    issueList = session.query(Issue).\
            order_by(Issue.issue_id).\
            all()    
    return issueList

def addOrUpdateIssue(session, issue_id, summary, status, priority, 
                     subgroup, component, submitter, owner, description, 
                     timestamp, debrief_key=None):

    issueList = session.query(Issue).filter(Issue.issue_id==issue_id)
    
    # should only be one issue in the list
    issue = issueList.first()
    if issue:
        # issue exists, so update it
        issue.issue_id = issue_id
        issue.description = description
        issue.owner = owner
        issue.priority = priority
        issue.subgroup = subgroup
        issue.component = component
        issue.status = status
        issue.submitter = submitter
        issue.summary = summary
        issue.timestamp = timestamp
        if debrief_key != None:
            issue.debrief_key = debrief_key
    else:
        issue = Issue(issue_id=issue_id, summary=summary, status=status, 
                      priority=priority, subgroup=subgroup, component=component,
                      submitter=submitter, owner=owner, description=description,
                      timestamp=timestamp, debrief_key=debrief_key)
        session.add(issue)
    print issue.json()
    return issue

def addOrUpdateIssueComment(session, issue_id, submitter, tag, data): 

    commentList = session.query(IssueComment).filter(IssueComment.issue_id==issue_id). \
                                              filter(IssueComment.tag==tag)
    
    # should only be one issue in the list
    comment = commentList.first()
    if comment:
        # issue exists, so update it
        comment.issue_id = issue_id
        comment.tag = tag
        comment.submitter = submitter
        comment.data = data
    else:
        comment = IssueComment(issue_id=issue_id, tag=tag, 
                      submitter=submitter, data=data)
        session.add(comment)
        
    print comment.json()

def addIssueFromAttributes(session, issue_attributes):
    try:
        issue_type  = issue_attributes['Platform']
        # extract the issue id from the attributes or generate one for this type
        if issue_attributes.has_key('Id'):
            issue_id = issue_attributes['Id']
        else:
            issue_id = getIssueId(session, issue_type)
            
        if issue_attributes.has_key('Summary'):
            summary = issue_attributes['Summary']
        else:
            summary = ''
            
        if issue_attributes.has_key('Status'):
            status = issue_attributes['Status']
        else:
            status = ''
            
        if issue_attributes.has_key('Priority'):
            priority = issue_attributes['Priority']
        else:
            priority = ''
        
        if issue_attributes.has_key('Subgroup'):
            subgroup = issue_attributes['Subgroup']
        else:
            subgroup = 'Unassigned'
            
        if issue_attributes.has_key('Component'):
            component = issue_attributes['Component']
        else:
            component = 'Unknown'
        
        if issue_attributes.has_key('Submitter'):
            submitter = issue_attributes['Submitter']
        else:
            submitter = ''
            
        if issue_attributes.has_key('Owner'):
            owner = issue_attributes['Owner']
        else:
            owner = 'Unassigned'
        
        if issue_attributes.has_key('Description'):
            description = issue_attributes['Description']
        else:
            description = ''
        
        if issue_attributes.has_key('Timestamp'):
            timestamp = issue_attributes['Timestamp']
        else:
            timestamp = str(int(time.time()))
        
        if issue_attributes.has_key('Debrief_Key'):
            debrief_key = issue_attributes['Debrief_Key']
        else:
            debrief_key = None
            
        if issue_attributes.has_key('Comment'):
            comment = issue_attributes['Comment']
        else:
            comment = ''
        
    except KeyError:
        raise Exception( 'Incomplete Issue Record' )
    
    issue = addOrUpdateIssue(session, issue_id, summary, status, priority, 
                             subgroup, component, submitter, owner, description, 
                             timestamp, debrief_key)
    
    if comment != '':
        addOrUpdateIssueComment(session, issue_id, submitter, timestamp, comment)
    
    session.commit()

    return issue
    
def getIssueId(session, issue_type):

    issueTypes = session.query(IssueType).filter(IssueType.issue_type==issue_type)
    
    # should only be one issue in the list
    issue = issueTypes.first()
    if issue:
        # issue type exists, so update it
        issue.max_id += 1
    else:
        issue = IssueType(issue_type=issue_type, max_id=1)
        session.add(issue)
        
    session.commit()
    return '%s-%d' % (issue_type,issue.max_id)
        

def getIssueTypes(session):
    issueTypes = session.query(IssueType).all()
    return issueTypes

        
def deleteAllProcessedFiles(session):
    p_list = session.query(ProcessedFiles).all()
    for item in p_list:
        session.delete(item)
    session.flush()
    
def deleteAllIssues(session):
    a_list = session.query(Issue).all()
    for item in a_list:
        session.delete(item)
    session.flush()

def deleteAllIssueComments(session):
    n_list = session.query(IssueComment).all()
    for item in n_list:
        session.delete(item)
    session.flush()

def deleteIssueComments(session, issue_id):
    comments = session.query(IssueComment).filter(IssueComment.issue_id==issue_id).\
                             all()
    for item in comments:
        session.delete(item)
    session.flush()

def deleteIssueCommentsByUser(session, issue_id, username):
    comments = session.query(IssueComment).filter(IssueComment.issue_id==issue_id).\
                                           filter(IssueComment.submitter==username).\
                                           all()
    for item in comments:
        session.delete(item)
    session.flush()

def deleteIssueCommentsByTag(session, issue_id, tag):
    comments = session.query(IssueComment).filter(IssueComment.issue_id==issue_id).\
                                           filter(IssueComment.tag==tag).\
                                           all()
    for item in comments:
        session.delete(item)
    session.flush()

def deleteIssueCommentsByData(session, issue_id, data):
    comments = session.query(IssueComment).filter(IssueComment.issue_id==issue_id).\
                                           filter(IssueComment.data==data).\
                                           all()
    for item in comments:
        session.delete(item)
    session.flush()
        
def create_db_tables(my_db):
    Base.metadata.create_all(my_db)

def dump_db_tables(my_db):
    meta = schema.MetaData(my_db)
    meta.reflect()
    meta.drop_all()

    
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

    # Dump the contents of the database if requested through the command option
    if options.drop:
        dump_db_tables(my_db)



