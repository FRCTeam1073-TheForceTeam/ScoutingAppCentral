'''
Created on Dec 12, 2013

@author: ken_sthilaire
'''
#!/usr/bin/python
'''
Created on Jan 04, 2013

@author: ksthilaire
'''

from sqlalchemy import create_engine
from sqlalchemy import schema
from sqlalchemy import Column, Integer, String

from optparse import OptionParser

import UserDefinitions
import DbSession
import json

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
    state           = Column(String(32))

    def check_password(self, password):
        if self.password == password:
            return True
        else:
            return False
        
    def check_access_level(self, access_level):
        if self.access_level <= access_level:
            return True
        else:
            return False
        
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
    



    
def addOrUpdateUser(session, username, email_address, cellphone, carrier, 
                    subgroup, password, display_name, role, contact_mode, 
                    altname, access_level, state='Enabled'):

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
        user.state = state
    else:
        user = User(username=username, email_address=email_address, cellphone=cellphone,
                    password=password, display_name=display_name, contact_mode=contact_mode,
                    subgroup=subgroup,role=role,carrier=carrier, altname=altname,
                    access_level=access_level, state=state)
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
        access_level = int(float(user_attributes['Access_Level']))
        if user_attributes.has_key('State'):
            state = user_attributes['State']
        else:
            state = 'Enabled'
        
    except KeyError:
        raise Exception( 'Incomplete User Record' )
    
    addOrUpdateUser(session, username, email_address, cellphone, carrier, 
                    subgroup, password, display_name, role, contact_mode, altname,
                    access_level, state)
    
    taskgroups = user_attributes['Taskgroups'].replace(' ','').split(',')
    for group in taskgroups:
        group = group.title()
        addUserToTaskgroup(session, group, username)
    
    session.commit()

def getTaskgroupList(session):
    taskgroups = []
    results = session.query(TaskgroupMember.taskgroup).distinct().all()
    for result in results:
        if result[0] != '':
            taskgroups.append(str(result[0]))
    taskgroups.sort()
    return taskgroups

def getSubgroupList(session):
    subgroups = []
    results = session.query(User.subgroup).distinct().all()
    for result in results:
        subgroups.append(str(result[0]))
    subgroups.sort()
    return subgroups

def getTaskgroupMembers(session, taskgroup):
    members = []
    results = session.query(TaskgroupMember).filter(TaskgroupMember.taskgroup==taskgroup).all()
    for result in results:
        members.append(str(result.username))
    return members

def getEmailAddrFromCarrier(cellphone, carrier):
    email_addr = cellphone.replace('-','')
    
    if carrier == 'Verizon':
        email_addr += '@vtext.com'
    elif carrier == 'ATT':
        email_addr += '@mms.att.net'
    elif carrier == 'USCellular':
        email_addr += '@email.uscc.net'
    elif carrier == 'TMobile':    
        email_addr += '@tmomail.net'
    elif carrier == 'Sprint':    
        email_addr += '@messaging.sprintpcs.com'
    else:
        email_addr = None
    
    return email_addr

def getTaskgroupEmailList(session, taskgroup):
    email_list_str = '%s_email_list=' % taskgroup
    results = session.query(TaskgroupMember).filter(TaskgroupMember.taskgroup==taskgroup).all()
    for result in results:
        user = getUser(session, result.username)
        contact = None
        if user:
            if user.state == 'Enabled':
                if user.contact_mode == 'Email':
                    contact = user.email_address
                elif user.contact_mode == 'Text':
                    contact = getEmailAddrFromCarrier(user.cellphone, user.carrier)
        if contact != None:
            email_list_str += '%s;' % contact
            
    email_list_str = email_list_str.rstrip(';')    
    return email_list_str
            
def getTaskgroupEmailLists(global_config, name):
    session = DbSession.open_db_session(global_config['users_db_name'])
    email_list_str = ''
    
    if name == 'all':
        taskgroups = getTaskgroupList(session)
        for taskgroup in taskgroups:
            email_list_str += getTaskgroupEmailList(session, taskgroup) + '\n'
    else:
        email_list_str += getTaskgroupEmailList(session, name) + '\n'
        
    return email_list_str

def getUserTaskgroups(session, username):
    taskgroup_str=''
    results = session.query(TaskgroupMember).filter(TaskgroupMember.username==username).all()
    for result in results:
        taskgroup_str += '%s,' % result.taskgroup            
    taskgroup_str = taskgroup_str.rstrip(',')    
    return taskgroup_str


def getUserList(session):
    users = session.query(User).order_by(User.username).all()
    return users

def getUser(session, username):
    if username == '':
        return None
    
    userList = session.query(User).filter(User.username==username)
    user = userList.first()
    if user is None:
        userList = session.query(User).filter(User.altname==username)
        user = userList.first()
        
    return user

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
    

        
def deleteAllProcessedFiles(session):
    p_list = session.query(ProcessedFiles).all()
    for item in p_list:
        session.delete(item)
    session.flush()
    
def deleteAllUsers(session):
    a_list = session.query(User).all()
    for item in a_list:
        session.delete(item)
    session.flush()

def deleteUser(session, username):
    a_list = session.query(User).filter(User.username==username).all()
    for item in a_list:
        session.delete(item)
        
    deleteUserFromAllTaskgroups(session, username)
    session.flush()

def deleteAllTaskgroupMembers(session):
    a_list = session.query(TaskgroupMember).all()
    for item in a_list:
        session.delete(item)
    session.flush()

def deleteUsersFromTaskgroup(session, taskgroup):
    a_list = session.query(TaskgroupMember).filter(TaskgroupMember.taskgroup==taskgroup).\
                                            all()
    for item in a_list:
        session.delete(item)
    session.flush()

def deleteUserFromAllTaskgroups(session, username):
    a_list = session.query(TaskgroupMember).filter(TaskgroupMember.username==username).\
                                            all()
    for item in a_list:
        session.delete(item)
    session.flush()

def deleteUserFromTaskgroup(session, taskgroup, username):
    userList = session.query(TaskgroupMember).filter(TaskgroupMember.taskgroup==taskgroup).\
                                              filter(TaskgroupMember.username==username)
    user = userList.first()
    if user:
        session.delete(user)
    

def updateUserTaskgroups(session, username, taskgroups_str):
    deleteUserFromAllTaskgroups(session, username)
    taskgroups = taskgroups_str.split(',')
    for group in taskgroups:
        addUserToTaskgroup(session, group, username)
       
        
def create_db_tables(my_db):
    Base.metadata.create_all(my_db)

def dump_db_tables(my_db):
    meta = schema.MetaData(my_db)
    meta.reflect()
    meta.drop_all()

def add_users_from_file( session, input_path):
    user_definitions = UserDefinitions.UserDefinitions()
    user_definitions.parse(input_path)
        
    users = user_definitions.get_definitions()
    for user, definition in users.iteritems():
        print 'Adding/Updating User %s' % user
        if user != '':
            addUserFromAttributes(session, definition)
    
    session.commit()
    
def create_admin_user( session, pw):

    addOrUpdateUser(session, 'admin', 'none', 'none', 'none', 
                    'none', pw, 'Administrator', 'Admin', 'none', 
                    'none', 0, 'Enabled')
    session.commit()
    
    
    
if __name__ == '__main__':

    parser = OptionParser()

    # db options.
    parser.add_option(
        "-u","--user",dest="user", default='root', help='Database user name')
    parser.add_option(
        "-d","--db",dest="db", default='users2013', help='Database name')
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
        db_connect='mysql://%s:%s@localhost/%s'%(options.user, options.password, (options.db+'.db'))
    else:
        raise Exception("No Database Type Defined!")

    my_db = create_engine(db_connect)

    if options.create:
        Base.metadata.create_all(my_db)

    # Dump the contents of the database if requested through the command option
    if options.drop:
        dump_db_tables(my_db)



