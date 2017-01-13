'''
Created on Feb 09, 2013

@author: ksthilaire
'''

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

def open_db_session( db_name, db_model=None ):
    if db_name.endswith('.db') is False:
        db_name = db_name + '.db'
    db_path = 'db/' + db_name
    db_connect='sqlite:///%s'%(db_path)
    my_db = create_engine(db_connect)

    session_factory = sessionmaker(bind=my_db)
    session = scoped_session(session_factory)

    # Create the database if it doesn't already exist and the model is provided
    if not os.path.exists('./' + db_path) and db_model is not None:
        db_model.create_db_tables(my_db)

    return session

