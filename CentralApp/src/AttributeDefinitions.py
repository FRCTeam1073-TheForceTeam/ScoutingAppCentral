'''
Created on Jan 24, 2012

@author: ksthilaire
'''

import csv
import xlrd

tmpfile = 'attr-tmp.csv'

class AttrDefinitions:
    
    def __init__(self):
        self._attrdefinitions = {}
        
    def get_definition(self, attr_name):
        return self._attrdefinitions[attr_name]

    def get_definitions(self):
        return self._attrdefinitions
         
    def parse(self, filename, sheet_type=None):
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
                    #print 'attr: ', header_row[index], ' value: ', item
                    definition[header_row[index]] = item
                        
                #print 'attribute definition: ', definition
                sheet_qualifier = definition['Sheet']
                if sheet_type == None or sheet_qualifier.lower() == 'both' or sheet_qualifier.lower() == sheet_type.lower():
                    self._attrdefinitions[definition['Name']] = definition

    # function will convert Excel spreadsheet files (xls or xlsx) to a csv file that can
    # then be parsed by this class
    def xls_to_csv(self, input_file ):
        wb = xlrd.open_workbook(input_file)
        sheet_names = wb.sheet_names()
        # for attribute definition file parsing, we only read the first sheet in the workbook
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
        return self._attrdefinitions.__repr__()            

    
    
if __name__ == '__main__':
        
    myfile = 'AttributeDefinitions-reboundrumble.csv'
    attr_definitions = AttrDefinitions()
    # create the attribute definition dictionary from the csv file
    attr_definitions.parse(myfile)
    print attr_definitions
    
    # go retrieve the definition for a specific attribute     
    speedDefinition = attr_definitions.get_definition('Speed')
    print 'Speed definition: ', speedDefinition
    
    print 'The attribute type for Speed is:', speedDefinition['Type']
    
    
    
    
