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
from UiGeneratorMatchGroup import MatchGroupUiGenControl

import UiGeneratorDebriefApp

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

def gen_ui( global_config, attrdef_filename, sheet_type, create_fragment_file=False, use_custom_buttons=False ):
    if sheet_type in ('Pit','Match'):
        return gen_scouting_sheet_ui(global_config, attrdef_filename, sheet_type, create_fragment_file, use_custom_buttons)
    elif sheet_type in ('Debrief'):
        return gen_debrief_sheet_ui(global_config, attrdef_filename, sheet_type, create_fragment_file, use_custom_buttons)
    else:
        err_str = 'Unsupported sheet type: %s' % (sheet_type)
        raise Exception(err_str)
        
def gen_scouting_sheet_ui( global_config, attrdef_filename, sheet_type, create_fragment_file=False, use_custom_buttons=False ):
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
    java_helper_functions = ''

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
                control = item['Control']
                if control == 'None':
                    # skip any attribute that has no control defined
                    continue
                elif control == 'Text':
                    ctrl_gen = TextFieldUiGenControl(item)
                elif control == 'Radio':
                    ctrl_gen = RadioButtonUiGenControl(item)
                elif control == 'Checkbox':
                    ctrl_gen = CheckboxUiGenControl(item)
                elif control == 'Scoring_Matrix':
                    ctrl_gen = ScoringMatrixUiGenControl(item)
                elif control == 'Line_Separator':
                    ctrl_gen = LineSeparatorUiGenControl(item)
                elif control == 'Heading':
                    ctrl_gen = HeadingFieldUiGenControl(item)
                elif control == 'Button':
                    ctrl_gen = ButtonUiGenControl(item)
                elif control == 'Match_Group':
                    ctrl_gen = MatchGroupUiGenControl(item)
                else:
                    'Unexpected Control Type Field: %s' % control
                    raise
    
                if use_custom_buttons:
                    ctrl_gen.enable_custom_buttons()

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
                
                java_helper_functions += ctrl_gen.gen_java_helper_functions()
                java_helper_functions = java_helper_functions.replace('NAME', item['Name'])
                
                if (control == 'Scoring_Matrix'):
                    above_name = ctrl_gen.get_last_label()
                elif control == 'Text': 
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
        fo.write( '\n======================= java helper function code fragments ======================\n\n')
        fo.write( java_helper_functions )
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
    gen_fragments['UIGEN:HELPER_FUNCTIONS'] = java_helper_functions
    
    return gen_fragments

def gen_debrief_sheet_ui( global_config, attrdef_filename, sheet_type, create_fragment_file=False, use_custom_buttons=False ):
    '''
    # For 2017, we have moved away from the spreadsheet driven layout for the debrief app, using a simple text
    # file for the definition of the taskgroups instead. The layout itself will only alter the taskgroup section 
    # of the debrief app so there is no need to have the full spreadsheet layout, like we do for the scouting
    # apps themselves.
    
    # Build the attribute definition dictionary from the definitions spreadsheet file
    attr_definitions = AttributeDefinitions.AttrDefinitions()
    
    attr_definitions.parse(attrdef_filename, sheet_type)
    attr_dict = attr_definitions.get_definitions()
    '''
    
    # TODO: load the list of taskgroups from some file
    taskgroups = UiGeneratorDebriefApp.load_taskgroups(attrdef_filename)
    categories = UiGeneratorDebriefApp.load_categories(attrdef_filename)
    
    # generate the variable parts of the debrief app based on the taskgroups that have been 
    # defined
    attr_dict = UiGeneratorDebriefApp.get_debrief_app_control_defs(taskgroups)
    
    # now, sort the attributes definitions according to the 'Order' within each attribute. This is
    # an artifact of when we loaded the layout from a spreadsheet file. We'll keep this behavior
    # in case we go back to the spreadsheet over time
    num_attr = len(attr_dict)

    attr_order = [{} for i in range(len(attr_dict))]
    
    i=0
    for key, value in attr_dict.items():
        attr_order[i] = value
        i += 1
        
    attr_order.sort(attr_order_compare)

    xml_string = {}
    java_list_declaration_snippet = ''
    java_list_alloc_snippet = ''
    java_load_snippet = ''
    
    java_checkbox_declaration_snippets = {}
    java_discard_handler_snippets = {}
    java_save_handler_snippets = {}
    java_reload_handler_snippets = {}
    java_checkbox_init_snippets = {}
    java_is_checked_snippets = {}
    for category in categories:
        java_checkbox_declaration_snippets[category] = ''
        java_discard_handler_snippets[category] = ''
        java_save_handler_snippets[category] = ''
        java_reload_handler_snippets[category] = ''
        java_checkbox_init_snippets[category] = ''
        java_is_checked_snippets[category] = ''

    # initialize the build_filename string to include the team number and the scouting sheet type into
    # the filename that contains the collected scouting data
    java_build_filename_string_rewritten = False
    java_build_filename_string = '                    final String filename = buildFilename( TeamEntry, "' + \
                                 sheet_type + '", "" );\n'
    
    above_name = 'Issue1_SummaryEntry'

    try:
        
        category = 1        
        for item in attr_order:
            # generate the XML snippets...
            above_name = 'Issue%d_SummaryEntry' % category
            ctrl_gen = CheckboxUiGenControl(item, left_margin=140)
            xml_string[category] = ctrl_gen.gen_xml_string(above_name)
            xml_string[category] = xml_string[category].replace('ABOVELabel', above_name)
            xml_string[category] = xml_string[category].replace('NAME', item['Name'])
            
            # add in the separator field, too.
            item_label = 'Issue%d_Taskgroup' % category
            above_item = 'Issue%d_Taskgroup%sCheckBox' % (category, taskgroups[-1])
            separator_ctrl = LineSeparatorUiGenControl()
            xml_string[category] += separator_ctrl.gen_hidden_xml_string(item_label,above_item)
            
            category += 1
            
        for item in taskgroups:
    
            java_list_declaration_snippet += UiGeneratorDebriefApp.gen_list_declaration_snippet(item)
            java_list_alloc_snippet += UiGeneratorDebriefApp.gen_list_alloc_snippet(item)
            java_load_snippet += UiGeneratorDebriefApp.gen_load_taskgroups_snippet(item)
            
            for category in categories:
                java_checkbox_declaration_snippets[category] += UiGeneratorDebriefApp.gen_checkbox_declaration_snippet(category,item)
                java_discard_handler_snippets[category] += UiGeneratorDebriefApp.gen_discard_handler_snippet(category,item)
                java_save_handler_snippets[category] += UiGeneratorDebriefApp.gen_save_handler_snippet(category,item)
                java_reload_handler_snippets[category] += UiGeneratorDebriefApp.gen_reload_handler_snippet(category,item)
                java_checkbox_init_snippets[category] += UiGeneratorDebriefApp.gen_checkbox_init_snippet(category,item)
                java_is_checked_snippets[category] += UiGeneratorDebriefApp.gen_is_checked_snippet(category,item)
                
    except:
        err_str = 'Error generating %s control: %s, check Map_Values string "%s" or Options string "%s" for proper formatting' % \
                  (item['Control'],item['Name'],item['Map_Values'],item['Options'])
        raise Exception(err_str)
        
    if create_fragment_file == True:
        # write out the xml file fragment
        outputFilename = './tmp/gen-ui-' + sheet_type + '.txt'
        fo = open(outputFilename, "w+")
        fo.write( '\n======================= main.xml code fragments ======================\n\n')
        for category in categories:
            fo.write( xml_string[category] )
            
        fo.write( '\n======================= java list declarations code fragments ======================\n\n')
        fo.write( java_list_declaration_snippet )
        fo.write( '\n======================= java list allocation code fragments ======================\n\n')
        fo.write( java_list_alloc_snippet )
        fo.write( '\n======================= java load code fragments ======================\n\n')
        fo.write( java_load_snippet )
        fo.write( '\n======================= java checkbox declarations code fragments ======================\n\n')    
        for category in categories:
             fo.write( java_checkbox_declaration_snippets[category] )
        fo.write( '\n======================= java save handlers code fragments ======================\n\n')
        for category in categories:
            fo.write( java_save_handler_snippets[category] )
        fo.write( '\n======================= java reload handlers code fragments ======================\n\n')
        for category in categories:
            fo.write( java_reload_handler_snippets[category] )
        fo.write( '\n======================= java discard handlers code fragments ======================\n\n')
        for category in categories:
            fo.write( java_discard_handler_snippets[category] )
        fo.write( '\n======================= java checkbos init code fragments ======================\n\n')
        for category in categories:
            fo.write( java_checkbox_init_snippets[category] )
        fo.write( '\n======================= java is checked code fragments ======================\n\n')
        for category in categories:
            fo.write( java_is_checked_snippets[category] )
        fo.close()
    
    # create a dictionary of all the generated code fragments to return to the 
    # caller
    gen_fragments = {}
    gen_fragments['UIGEN:LIST_DECLARE'] = java_list_declaration_snippet
    gen_fragments['UIGEN:LIST_ALLOC'] = java_list_alloc_snippet
    gen_fragments['UIGEN:LIST_LOAD'] = java_load_snippet
    gen_fragments['UIGEN:CHECKBOX_DECLARE'] = java_checkbox_declaration_snippets
    gen_fragments['UIGEN:SAVE'] = java_save_handler_snippets
    gen_fragments['UIGEN:RELOAD'] = java_reload_handler_snippets
    gen_fragments['UIGEN:DISCARD'] = java_discard_handler_snippets
    gen_fragments['UIGEN:CHECKBOX_INIT'] = java_checkbox_init_snippets
    gen_fragments['UIGEN:IS_CHECKED'] = java_is_checked_snippets
    gen_fragments['UIGEN:XML_FIELDS'] = xml_string
    
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
                
