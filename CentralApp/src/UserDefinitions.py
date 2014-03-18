'''
Created on Feb 02, 2013

@author: ksthilaire
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import UsersDataModel
import os
import csv
import xlrd

tmpfile = 'user-tmp.csv'

class UserDefinitions:
    
    def __init__(self):
        self._userdefinitions = {}
        
    def get_definition(self, username):
        return self._userdefinitions[username]

    def get_definitions(self):
        return self._userdefinitions
         
    def parse(self, filename):
        first_row = True
        header_row = []
        
        # if the specified file is an Excel spreadsheet, convert the
        # spreadsheet into a csv file that we will then process.
        # alternatively, we could also process the Excel format directly,
        # though this way keeps the actual parsing in one place
        if filename.endswith('.xls') or filename.endswith('.xlsx'):
            filename = self.xls_to_csv(filename)
            
        self._csv_reader = csv.reader(open(filename, 'r'))
        for row in self._csv_reader:
            if first_row == True:
                first_row = False 
                header_row = row
                #print header_row
            else:
                definition = {}
                for index, item in enumerate(row):
                    definition[header_row[index]] = item
                        
                #print 'user definition: ', definition
                self._userdefinitions[definition['Username']] = definition

    # function will convert Excel spreadsheet files (xls or xlsx) to a csv file that can
    # then be parsed by this class
    def xls_to_csv(self, input_file ):
        wb = xlrd.open_workbook(input_file)
        sheet_names = wb.sheet_names()
        # for user definition file parsing, we only read the first sheet in the workbook
        sheet_name = sheet_names[0]
        outfile_name = './tmp/%s.csv' % sheet_name
        outfile = file(outfile_name, 'wb')
        writer = csv.writer(outfile)
        sheet = wb.sheet_by_name(sheet_name)
        for row in xrange(sheet.nrows):
            writer.writerow([sheet.cell_value(row,col) for col in xrange(sheet.ncols)])
        outfile.close()
        return outfile_name

    # the __repr__ method allows this class to be printed 
    def __repr__(self):
        return self._userdefinitions.__repr__()            

    
    
if __name__ == '__main__':
     
        
    myfile = './config/Users-2013.xlsx'
    user_definitions = UserDefinitions()
    # create the user definition dictionary from the csv file
    user_definitions.parse(myfile)
    print user_definitions
        
    db_name = 'Issues2013'
    db_connect='sqlite:///%s'%(db_name)
    my_db = create_engine(db_connect)
    Session = sessionmaker(bind=my_db)
    session = Session()

    # Create the database if it doesn't already exist
    if not os.path.exists('./' + db_name):    
        UsersDataModel.create_db_tables(my_db)

    users = user_definitions.get_definitions()
    for user, definition in users.iteritems():
        UsersDataModel.addUserFromAttributes(session, definition)
    
    session.commit()
    
    taskgroups = UsersDataModel.getTaskgroupList(session)
    print taskgroups
    for group in taskgroups:
        print group
        members = UsersDataModel.getTaskgroupMembers(session,group)
        print members
    
    subgroups = UsersDataModel.getSubgroupList(session)
    print subgroups
    
    users = UsersDataModel.getUserList(session)
    print users
    
    users = UsersDataModel.getDisplayNameList(session)
    print users
    
    
