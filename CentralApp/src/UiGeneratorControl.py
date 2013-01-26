'''
Created on Jan 13, 2013

@author: Ken
'''

class UiGenControl( object ):
    attr_def = None

    def __init__(self, attr_def):
        self.attr_def = attr_def

    def gen_xml_string(self, above_name):
        xml_str = 'XML definition string generator'
        return xml_str

    def gen_java_declarations_string(self):
        java_str  = 'Java variable declaration string generator'
        return java_str

    def gen_java_init_string(self):
        java_str  = 'Java variable initialization string generator'
        return java_str

    def gen_java_button_handler(self):
        java_str  = 'Java button handler string generator'
        return java_str

    def gen_java_discard_handler(self):
        java_str  = 'Java discard handler string generator'
        return java_str

    def gen_java_save_handler(self):
        java_str  = 'Java save handler string generator'
        return java_str

    def gen_java_reload_handler(self):
        java_str  = 'Java reload handler string generator'
        return java_str
    

