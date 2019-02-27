'''
Created on Jan 24, 2012

@author: ksthilaire
'''

import csv
import xlrd
import os

import UiGeneratorMatchGroup

tmpfile = 'attr-tmp.csv'
attrdef_overrides_filename = './config/attrdef_overrides.txt'

class AttrDefinitions:
    
    def __init__(self, global_config=None):
        self._attrdefinitions = {}
        self._attr_names = {}

        # if this instance was created with config, then store it in the object, otherwise
        # just create an empty dictionary so that we can reference it within the methods
        if global_config is not None:
            self.global_config = global_config
        else:
            self.global_config = {}
        
    def get_definition(self, attr_name):
        if self._attrdefinitions.has_key(attr_name):
            return self._attrdefinitions[attr_name]
        else:
            return None

    def add_definition(self, attr_def):
        self._attrdefinitions[attr_def['Name']] = attr_def
        self._attr_names[attr_def['Name']] = attr_def['Name']

    def get_definitions(self):
        return self._attrdefinitions
         
    def parse(self, filename, sheet_type=None):
        first_row = True
        header_row = []
        extra_attrdefinitions = {}
        extra_column_order = 1000
        
        # if the specified file is an Excel spreadsheet, convert the
        # spreadsheet into a csv file that we will then process.
        # alternatively, we could also process the Excel format directly,
        # though this way keeps the actual parsing in one place
        if filename.endswith('.xls') or filename.endswith('.xlsx'):
            filename = self.xls_to_csv(filename)
            
        self._csv_reader = csv.reader(open(filename, 'r'))
        row_number = 0
        for row in self._csv_reader:
            if first_row == True:
                first_row = False
                header_row = row
                # make sure that all column headings are capitalized
                for index, heading in enumerate(row):
                    header_row[index] = heading.title()
                #print header_row
            else:
                definition = {}
                for index, item in enumerate(row):
                    #print 'attr: ', header_row[index], ' value: ', item
                    
                    # check if the global_config indicates that we're working with the 2014-era tablet UI that does not
                    # normalize the case of the attributes. If we are in 'legacy' mode, then just use the attribute
                    # label as is. If not, then capitalize the first character only
                    if self.global_config.has_key('legacy_tablet_ui') and self.global_config['legacy_tablet_ui'].lower() == 'yes':
                        definition[header_row[index]] = item
                    else:
                        # strip out any leading or trailing whitespace characters. We have had cases where the spreadsheet
                        # has <CR> or spaces in the fields, causing weird behavior when we try to generate the UI applications.
                        # so, we will strip whitespace left and right, and within the field itself
                        # then capitalize the first character of the field
                        item = item.lstrip().strip()
                        item = item.replace(' ','')
                        item = item.title()
                        definition[header_row[index]] = item

                # if the name field of the attribute is empty, then assume an empty line and skip it
                if definition['Name'] == '':
                    #print 'Empty attribute row, skipping...'
                    continue

                # set the Column_Order attribute to the row number, doing away with the troublesome
                # column that has proven to be error prone. With this change, the column display
                # order will be the same as the order of the rows of the spreadsheet
                definition['Column_Order'] = row_number

                # if there is no Order column in the attribute definition, then insert an Order term
                # into the definition and set it to the row_number. The above Column_Order and 
                # this Order attribute should be combined to eliminate any lingering confusion over
                # their use. In the early days, there were two separate purposes for these columns, but
                # there really is no reason to keep them separate. The order of the attributes when 
                # creating the tablet UI is based on the row ordering in the spreadsheet itself.
                if not definition.has_key('Order'):
                    definition['Order'] = row_number

                #print 'attribute definition: ', definition
                sheet_qualifier = definition['Sheet']
                
                # the following code will detect duplicate rows in the attribute definitions file. We
                # continue to see issues where the file has rows with the same attribute name and this
                # code will raise an exception during the parsing of the attribute definitions file
                if self._attr_names.has_key(definition['Name']):
                    raise Exception('ERROR: Duplicate Name In Attribute Definitions, Attribute Name: %s, Row Number: %d' % (definition['Name'],row_number+1))
                else:
                    self._attr_names[definition['Name']] = definition['Name']
                    
                if sheet_type == None or sheet_qualifier.lower() == 'all' or sheet_qualifier.lower() == 'both' or sheet_qualifier.lower() == sheet_type.lower():
                    self._attrdefinitions[definition['Name']] = definition
                    
                    # for the scoring matrix, add default attribute definitions for the individual scoring fields
                    # if explicit attributes have not been defined in the spreadsheet
                    if definition['Control'] == 'Scoring_Matrix' or definition['Control'] == 'Scoring_Timer':
                        definition['Type'] = 'Integer'

                        disp_type = None
                        options_str = definition['Options']    
                        if options_str != '':
                            options = options_str.split(':')
                            for option in options:
                                if option.find('=') != -1:
                                    option_name, option_value = option.split('=')
                                    if option_name == 'Type':
                                        disp_type = option_value
                                        break

                        map_values_str = definition['Map_Values']
                        map_values = map_values_str.split(':')
                        for map_value in map_values:
                            label = map_value.split('=')[0]
                            attr_name = definition['Name'] + '_' + label
                            
                            new_definition = definition.copy()
                            new_definition['Name'] = attr_name
                            if disp_type != None:
                                new_definition['Display_Name'] = attr_name.replace('Points', disp_type)
                            new_definition['Order'] = ''
                            new_definition['Control'] = 'None'
                            new_definition['Options'] = ''
                            new_definition['Weight'] = '0.0'
                            new_definition['Map_Values'] = ''
                            new_definition['Type'] = 'Integer'
                            new_definition['Include_In_Report'] = 'No'
                            new_definition['Column_Order'] = str(extra_column_order)
                            extra_column_order += 1

                            extra_attrdefinitions[attr_name] = new_definition
                    elif definition['Control'] == 'Checkbox':
                        definition['Type'] = 'Map_Integer'
                        # set the control to use numeric values in the generated CSV file
                        definition['Display_Numeric'] = 'Yes'
                    elif definition['Control'] == 'Radio':
                        definition['Type'] = 'Map_Integer'
                        # set the control to use numeric values in the generated CSV file
                        definition['Display_Numeric'] = 'Yes'
                    elif definition['Control'] == 'Match_Group':
                        expanded_definitions = UiGeneratorMatchGroup.GetMatchGroupControlDefs(definition)

                        # check for name conflicts in the expanded definitions that were added as part
                        # of the match group expansion
                        for expanded_def_name in expanded_definitions.keys():
                            if self._attr_names.has_key(expanded_def_name):
                                raise Exception('ERROR: Duplicate Name In Match Group Attribute Expansion, Attribute Name: %s, Row Number: %d' % (definition['Name'],row_number+1))
                            else:
                                self._attr_names[expanded_def_name] = expanded_def_name

                        self._attrdefinitions.update(expanded_definitions)
                                                
                        # reset the row_number based on the currrent order of this definition. It has
                        # been incremented by the number of expanded definitions
                        row_number = definition['Order']
                        
            row_number += 1

        extra_column_order = float(len(self._attrdefinitions) + 1)            
        for key, extra_attr in extra_attrdefinitions.iteritems():
            if not self._attrdefinitions.has_key(key):
                extra_attr['Column_Order'] = str(extra_column_order)
                extra_column_order += 1
                self._attrdefinitions[key] = extra_attr
        
        self.read_attr_overrides()

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

    def read_attr_overrides(self):
    
        if os.path.exists(attrdef_overrides_filename):
            override_file = open(attrdef_overrides_filename, 'r')
            for override_line in override_file:
                if override_line.startswith('#'):
                    continue
                override_line = override_line.rstrip()
                if override_line.count('=') > 0:
                    (attr,value) = override_line.split('=',1)
                    
                    if self._attrdefinitions.has_key(attr):
                        self._attrdefinitions[attr]['Weight'] = value
                else:
                    # ignore lines that don't have an equal sign in them
                    pass   
            override_file.close()
    
    def write_attr_overrides(self):
        attrdef_overrides = {}
        override_file = open(attrdef_overrides_filename, 'w+')
        #for key, value in attrdef_overrides.iteritems():
        for key, attr_def in sorted(self._attrdefinitions.items()):
            attrdef_overrides[key] = attr_def['Weight']
            
        for attr, weight in sorted(attrdef_overrides.items()):
            line = '%s=%s\n' % (attr,weight)
            override_file.write(line)
        override_file.close()

            

    # the __repr__ method allows this class to be printed 
    def __repr__(self):
        return self._attrdefinitions.__repr__()            

    def get_attr_dict_by_category(self):
        category_dict = dict()
        category_dict['Uncategorized'] = list()
        for key, attrdef in self._attrdefinitions.iteritems():
            # skip over the line separators, as they don't have any meaning beyond the
            # tablet UI generation
            if attrdef['Control'] == 'Line_Separator':
                continue
            
            if attrdef.has_key('Sub_Category') and attrdef['Sub_Category'] != '':
                try:
                    category_dict[attrdef['Sub_Category']].append(key)
                except KeyError:
                    category_dict[attrdef['Sub_Category']] = list()
                    category_dict[attrdef['Sub_Category']].append(key)
            else:
                category_dict['Uncategorized'].append(key)
                
        
        return category_dict

    
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
    
    
    
    
