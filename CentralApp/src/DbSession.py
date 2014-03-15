'''
Created on Feb 09, 2013

@author: ksthilaire
'''

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

def open_db_session( db_name, db_model=None ):
    if db_name.endswith('.db') == False:
        db_name = db_name + '.db'
    db_connect='sqlite:///%s'%(db_name)
    my_db = create_engine(db_connect)
    Session = sessionmaker(bind=my_db)
    session = Session()

    # Create the database if it doesn't already exist and the model is provided
    if not os.path.exists('./' + db_name):    
        db_model.create_db_tables(my_db)

    return session

