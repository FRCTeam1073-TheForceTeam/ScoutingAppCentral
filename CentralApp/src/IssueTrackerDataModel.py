#!/usr/bin/python
'''
Created on Jan 04, 2013

@author: ksthilaire
'''

import datetime
from sqlalchemy import create_engine
from sqlalchemy import schema
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import sessionmaker
from optparse import OptionParser

import time

import UserDefinitions

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
    
class IssueComment(Base):
    __tablename__ = "issue_comments"

    issue_id    = Column(String(32))
    data        = Column(String(1024))
    tag         = Column(String(64))
    submitter   = Column(String(32))
    
class User(Base):
    __tablename__ = "users"
    
    username        = Column(String(32))
    email_address   = Column(String(64))
    cellphone       = Column(String(32))
    carrier         = Column(String(32))
    subgroup        = Column(String(128))
    password        = Column(String(32))
    display_name    = Column(String(64))
    role            = Column(String(32))
    contact_mode    = Column(String(32))
    altname         = Column(String(32))
    access_level    = Column(Integer)
    
class TaskgroupMember(Base):
    __tablename__ = "taskgroups"
    
    taskgroup = Column(String(32))
    username  = Column(String(32))

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
    comments = session.query(IssueComment).filter(IssueComment.issue_id==issue_id).all()
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

def getIssuesInNumericOrder(session, max_issues=100):
    issueList = session.query(Issue).\
            order_by(Issue.issue_id).\
            all()    
    return issueList

def addIssueComment(session, issue_id, notes, notestag):
    notes = IssueComment(issue_id=issue_id, data=notes, tag=notestag)
    session.add(notes)
    
def addOrUpdateIssue(session, issue_id, summary, status, priority, 
                     subgroup, component, submitter, owner, description):

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
    else:
        issue = Issue(issue_id=issue_id, summary=summary, status=status, 
                      priority=priority, subgroup=subgroup, component=component,
                      submitter=submitter, owner=owner, description=description)
        session.add(issue)
    print issue.json()

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
            subgroup = ''
            
        if issue_attributes.has_key('Component'):
            component = issue_attributes['Component']
        else:
            component = ''
        
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
        
        if issue_attributes.has_key('Comment'):
            comment = issue_attributes['Comment']
        else:
            comment = ''
        
    except KeyError:
        raise Exception( 'Incomplete Issue Record' )
    
    addOrUpdateIssue(session, issue_id, summary, status, priority, 
                     subgroup, component, submitter, owner, description)
    
    if comment != '':
        addOrUpdateIssueComment(session, issue_id, submitter, timestamp, comment)
    
    session.commit()

'''    
        if carrier == 'Verizon':
            user.textmsg_address = cellphone + '@vtext.com'
        elif carrier == 'ATT':
            user.textmsg_address = cellphone + '@txt.att.net'
        elif carrier == 'USCell':
            user.textmsg_address = cellphone + '@email.uscc.net'
'''
    
def addOrUpdateUser(session, username, email_address, cellphone, carrier, 
                    subgroup, password, display_name, role, contact_mode, 
                    altname, access_level):

    userList = session.query(User).filter(User.username==username)
    
    # should only be one issue in the list
    user = userList.first()
    if user:
        # user exists, so update it
        user.username = username
        user.email_address = email_address
        user.cellphone = cellphone
        user.password = password
        user.display_name = display_name
        user.contact_mode = contact_mode
        user.subgroup = subgroup
        user.role = role
        user.carrier = carrier
        user.altname = altname
        user.access_level = access_level
    else:
        user = User(username=username, email_address=email_address, cellphone=cellphone,
                    password=password, display_name=display_name, contact_mode=contact_mode,
                    subgroup=subgroup,role=role,carrier=carrier, altname=altname,
                    access_level=access_level)
        session.add(user)
    print user.json()

def addUserToTaskgroup(session, taskgroup, username):
    userList = session.query(TaskgroupMember).filter(TaskgroupMember.taskgroup==taskgroup).\
                                              filter(TaskgroupMember.username==username)
    user = userList.first()
    if not user:
        user = TaskgroupMember(taskgroup=taskgroup, username=username)
        session.add(user)
    print user.json()
    
def addUserFromAttributes(session, user_attributes):
    try:
        username = user_attributes['Username']
        email_address = user_attributes['Email_Address']
        cellphone = user_attributes['Cellphone']
        password = user_attributes['Password']
        display_name = user_attributes['Display_Name']
        contact_mode = user_attributes['Contact_Mode']
        subgroup = user_attributes['Subgroup']
        role = user_attributes['Role']
        carrier = user_attributes['Carrier']
        altname = user_attributes['Alt_Name']
        access_level = 5
        
    except KeyError:
        raise Exception( 'Incomplete User Record' )
    
    addOrUpdateUser(session, username, email_address, cellphone, carrier, 
                    subgroup, password, display_name, role, contact_mode, altname,
                    access_level)
    
    taskgroups = user_attributes['Taskgroups'].split(',')
    for group in taskgroups:
        addUserToTaskgroup(session, group, username)
    
    session.commit()

def getTaskgroupList(session):
    taskgroups = []
    results = session.query(TaskgroupMember.taskgroup).distinct().all()
    for result in results:
        taskgroups.append(str(result[0]))
    return taskgroups.sort()

def getSubgroupList(session):
    subgroups = []
    results = session.query(User.subgroup).distinct().all()
    for result in results:
        subgroups.append(str(result[0]))
    return subgroups.sort()

def getTaskgroupMembers(session, taskgroup):
    members = []
    results = session.query(TaskgroupMember).filter(TaskgroupMember.taskgroup==taskgroup).all()
    for result in results:
        members.append(str(result.username))
    return members
            
def getUserList(session):
    users = session.query(User).all()
    users.sort()
    return users

def getUsernameList(session):
    users = []
    results = session.query(User.username).all()
    
    for result in results:
        users.append(str(result[0]))
        
    users.sort()
    return users
    
def getDisplayNameList(session):
    users = []
    results = session.query(User.display_name).all()
    
    for result in results:
        users.append(str(result[0]))
        
    users.sort()
    return users
    
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

def deleteAllUsers(session):
    a_list = session.query(User).all()
    for item in a_list:
        session.delete(item)
    session.flush()

def deleteAllTaskgroupMembers(session):
    a_list = session.query(TaskgroupMember).all()
    for item in a_list:
        session.delete(item)
    session.flush()

def deleteAllIssueComments(session):
    n_list = session.query(IssueComment).all()
    for item in n_list:
        session.delete(item)
    session.flush()
    
def create_db_tables(my_db):
    Base.metadata.create_all(my_db)

def dump_db_tables(my_db):
    meta = schema.MetaData(my_db)
    meta.reflect()
    meta.drop_all()

def add_users_from_file( db_name, input_path):
    user_definitions = UserDefinitions.UserDefinitions()
    user_definitions.parse(input_path)
        
    db_connect='sqlite:///%s'%(db_name)
    my_db = create_engine(db_connect)
    Session = sessionmaker(bind=my_db)
    session = Session()

    users = user_definitions.get_definitions()
    for user, definition in users.iteritems():
        print 'Adding/Updating User %s' % user
        addUserFromAttributes(session, definition)
    
    session.commit()
    
def create_admin_user( db_name, pw):
    db_connect='sqlite:///%s'%(db_name)
    my_db = create_engine(db_connect)
    Session = sessionmaker(bind=my_db)
    session = Session()

    addOrUpdateUser(session, 'admin', 'none', 'none', 'none', 
                    'none', pw, 'Administrator', 'Admin', 'none', 
                    'none', 0)
    session.commit()
    
    
    
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



