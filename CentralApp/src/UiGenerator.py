'''
Created on Feb 4, 2012

@author: Ken
'''

from optparse import OptionParser
import AttributeDefinitions
from UiGeneratorCheckbox import CheckboxUiGenControl
from UiGeneratorRadioButton import RadioButtonUiGenControl
from UiGeneratorTextfield import TextFieldUiGenControl
from UiGeneratorScoringMatrix import ScoringMatrixUiGenControl 
from UiGeneratorSeparator import LineSeparatorUiGenControl 
from UiGeneratorButton import ButtonUiGenControl 
from UiGeneratorHeading import HeadingFieldUiGenControl

def gen_java_reload_handlers_termstr():
    java_str = "                }\n"
    return java_str
        
def attr_order_compare( left, right ):
    if not left['Order']:
        left_order = 0
    else:
        left_order = int(float(left['Order']))
    if not right['Order']:
        right_order = 0
    else:
        right_order = int(float(right['Order']))
    return cmp( left_order, right_order )

def gen_ui( global_config, attrdef_filename, sheet_type, create_fragment_file=False ):
    # Build the attribute definition dictionary from the definitions spreadsheet file
    attr_definitions = AttributeDefinitions.AttrDefinitions(global_config)
    attr_definitions.parse(attrdef_filename, sheet_type)

    attr_dict = attr_definitions.get_definitions()
    num_attr = len(attr_dict)
    attr_order = [{} for i in range(len(attr_dict))]
    
    i=0
    for key, value in attr_dict.items():
        attr_order[i] = value
        i += 1
        
    attr_order.sort(attr_order_compare)
    
    xml_string = ''
    java_declarations = ''
    java_var_init_strings = ''
    java_button_handlers = ''
    java_discard_handlers = ''
    java_save_handlers = ''
    java_reload_handlers = ''

    # initialize the build_filename string to include the team number and the scouting sheet type into
    # the filename that contains the collected scouting data
    java_build_filename_string_rewritten = False
    java_build_filename_string = '                    final String filename = buildFilename( TeamEntry, "' + \
                                 sheet_type + '", "" );\n'
    
    above_name = 'TeamLabel'
    
    try:
        for item in attr_order:
            ctrl_gen = None
            if item['Order'] != '' and int(float(item['Order'])) != 0:
                if item['Control'] == 'Text':
                    ctrl_gen = TextFieldUiGenControl(item)
                elif item['Control'] == 'Radio':
                    ctrl_gen = RadioButtonUiGenControl(item)
                elif item['Control'] == 'Checkbox':
                    ctrl_gen = CheckboxUiGenControl(item)
                elif item['Control'] == 'Scoring_Matrix':
                    ctrl_gen = ScoringMatrixUiGenControl(item)
                elif item['Control'] == 'Line_Separator':
                    ctrl_gen = LineSeparatorUiGenControl(item)
                elif item['Control'] == 'Heading':
                    ctrl_gen = HeadingFieldUiGenControl(item)
                elif item['Control'] == 'Button':
                    ctrl_gen = ButtonUiGenControl(item)
    
                xml_string += ctrl_gen.gen_xml_string(above_name)
                xml_string = xml_string.replace('ABOVELabel', above_name)
                xml_string = xml_string.replace('NAME', item['Name'])
    
                java_declarations += ctrl_gen.gen_java_declarations_string()
                java_declarations = java_declarations.replace('NAME', item['Name'])
    
                java_var_init_strings += ctrl_gen.gen_java_init_string()
                java_var_init_strings = java_var_init_strings.replace('NAME', item['Name'])
    
                java_button_handlers += ctrl_gen.gen_java_button_handler()
                java_button_handlers = java_button_handlers.replace('NAME', item['Name'])
    
                java_discard_handlers += ctrl_gen.gen_java_discard_handler()
                java_discard_handlers = java_discard_handlers.replace('NAME', item['Name'])
    
                java_save_handlers += ctrl_gen.gen_java_save_handler()
                java_save_handlers = java_save_handlers.replace('NAME', item['Name'])
    
                java_reload_handlers += ctrl_gen.gen_java_reload_handler()
                java_reload_handlers = java_reload_handlers.replace('NAME', item['Name'])
                
                if (item['Control'] == 'Scoring_Matrix'):
                    above_name = ctrl_gen.get_last_label()
                elif item['Control'] == 'Text': 
                    above_name = item['Name'] + 'Entry'
                else:
                    above_name = item['Name'] + 'Label'
                    
                if sheet_type == 'Match' and java_build_filename_string_rewritten == False:
                    java_build_filename_string_rewritten = True
                    java_build_filename_string = '                    final String filename = buildFilename( TeamEntry, "' + \
                                                 sheet_type + '", MatchEntry.getText().toString() );\n'
                elif sheet_type == 'Debrief' and java_build_filename_string_rewritten == False:
                    java_build_filename_string_rewritten = True
                    java_build_filename_string = '                    final String filename = buildDebriefFilename( "' + \
                                                 sheet_type + '", "Match", MatchEntry.getText().toString() );\n'
                elif sheet_type == 'Issue' and java_build_filename_string_rewritten == False:
                    java_build_filename_string_rewritten = True
                    java_build_filename_string = '                    final String filename = buildIssueFilename( IdEntry, "' + \
                                                 sheet_type + '");\n'
    except:
        err_str = 'Error generating %s control: %s, check Map_Values string "%s" or Options string "%s" for proper formatting' % \
                  (item['Control'],item['Name'],item['Map_Values'],item['Options'])
        raise Exception(err_str)
        
         
    if create_fragment_file == True:
        # write out the xml file fragment
        outputFilename = './tmp/gen-ui-' + sheet_type + '.txt'
        fo = open(outputFilename, "w+")
        fo.write( '\n======================= main.xml code fragments ======================\n\n')
        fo.write( xml_string )
        fo.write( '\n======================= java declarations code fragments ======================\n\n')
        fo.write( java_declarations )
        fo.write( '\n======================= java var init code fragments ======================\n\n')
        fo.write( java_var_init_strings )
        fo.write( '\n======================= java button handlers code fragments ======================\n\n')
        fo.write( java_button_handlers )
        fo.write( '\n======================= java save handlers code fragments ======================\n\n')
        fo.write( java_save_handlers )
        fo.write( '\n======================= java reload handlers code fragments ======================\n\n')
        fo.write( java_reload_handlers )
        fo.write( '\n======================= java discard handlers code fragments ======================\n\n')
        fo.write( java_discard_handlers )
        fo.write( '\n======================= java build_filename() code fragment ======================\n\n')
        fo.write( java_build_filename_string )
        fo.close()
    
    # create a dictionary of all the generated code fragments to return to the 
    # caller
    gen_fragments = {}
    gen_fragments['UIGEN:VAR_DECLARE'] = java_declarations
    gen_fragments['UIGEN:VAR_INIT'] = java_var_init_strings
    gen_fragments['UIGEN:SAVE'] = java_save_handlers
    gen_fragments['UIGEN:RELOAD'] = java_reload_handlers
    gen_fragments['UIGEN:DISCARD'] = java_discard_handlers
    gen_fragments['UIGEN:HANDLERS'] = java_button_handlers
    gen_fragments['UIGEN:XML_FIELDS'] = xml_string
    gen_fragments['UIGEN:BUILD_FILENAME'] = java_build_filename_string
    
    return gen_fragments

if __name__ == '__main__':
    
    # command line options handling
    parser = OptionParser()
    
    parser.add_option(
        "-t","--type",dest="type", default="pit", 
        help='Which UI to generate [pit|match]')
    parser.add_option(
        "-d","--definitions",dest="definitionFileBase", default="AttributeDefinitions-reboundrumble", 
        help='Attribute Definitions File')

    # Parse the command line arguments
    (options,args) = parser.parse_args()
    
    attrdef_filename = options.definitionFileBase + '.xlsx'  

    gen_ui( attrdef_filename, options.type, create_fragment_file=True )
                
