'''
Created on Feb 09, 2013

@author: ksthilaire
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def open_db_session( db_name ):
    db_connect='sqlite:///%s'%(db_name)
    my_db = create_engine(db_connect)
    Session = sessionmaker(bind=my_db)
    session = Session()

    return session

