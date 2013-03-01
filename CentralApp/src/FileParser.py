'''
Created on Dec 27, 2011

@author: ksthilaire
'''

import csv

class FileParser(object):
    '''
    File parser class
    '''

    def __init__(self, filename):
        '''
        Constructor

        Args:
            filename: The name of the file to parse.
        '''
        # use the csv reader to parse out the comma separated elements within each row
        self._csv_reader = csv.reader(open(filename, 'r'), delimiter='|')

    def parse(self, file_attributes):
        '''Parse entire file.'''
        for row in self._csv_reader:
            try:
                self.parse_row(row, file_attributes)
            except Exception, e:
                print 'error parsing line: %s'%e

    def parse_row(self, row, file_attributes):
        '''Parse a single row of a file.
       
        Args:
            row: The row to be parsed.
        '''

        print 'Row data:', row
        # For each name:value pair in the row, separated by a comma
        for token in row:
            # print 'Token data:', token
            # Split out the attribute name and value
            attribute, value = token.split(':', 1)
            file_attributes[attribute] = value
  

