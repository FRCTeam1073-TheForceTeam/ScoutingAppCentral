'''
Created on Jan 13, 2013

@author: Ken
'''

class UiGenControl( object ):
    attr_def = None
    custom_buttons = False

    def __init__(self, attr_def):
        self.attr_def = attr_def

    def enable_custom_buttons(self):
        self.custom_buttons = True

    def gen_xml_string(self, above_name):
        xml_str = ''
        return xml_str

    def gen_java_declarations_string(self):
        java_str  = ''
        return java_str

    def gen_java_init_string(self):
        java_str  = ''
        return java_str

    def gen_java_button_handler(self):
        java_str  = ''
        return java_str

    def gen_java_discard_handler(self):
        java_str  = ''
        return java_str

    def gen_java_save_handler(self):
        java_str  = ''
        return java_str

    def gen_java_reload_handler(self):
        java_str  = ''
        return java_str
    
    def gen_java_helper_functions(self):
        java_str  = ''
        return java_str
    

