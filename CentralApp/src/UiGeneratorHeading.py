'''
Created on January 17, 2016

@author: Ken
'''

from UiGeneratorControl import UiGenControl

class HeadingFieldUiGenControl( UiGenControl ):
    attr_def = None

    def __init__(self, attr_def):
        self.attr_def = attr_def
        self.config = { 'Lines':'1', 'Width':'Wide' }
        option_str = attr_def['Options']
        if option_str != '':
            options = option_str.split(':')
            for option in options:
                if option.find('=') != -1:
                    option_name, option_value = option.split('=')
                    self.config[option_name] = option_value

    def gen_xml_string(self, above_name):
        xml_str =  "    <!-- Begin NAME field text label and entry field -->\n"
        xml_str += "    <TextView\n"
        xml_str += "        android:id=\"@+id/NAMELabel\"\n"
        
        if self.config['Width'] == 'Narrow':
            xml_str += "        android:layout_width=\"200dp\"\n"
        elif self.config['Width'] == 'Wide':
            xml_str += "        android:layout_width=\"600dp\"\n"
        else:
            xml_str += "        android:layout_width=\"400dp\"\n"
        lines = int(self.config['Lines'])
        height = 40*lines
        xml_str += "        android:layout_height=\"%ddp\"\n" % height
            
        xml_str += "        android:layout_alignParentLeft=\"true\"\n"
        if above_name == 'NONE':
            xml_str += "        android:layout_alignParentTop=\"true\"\n"
        else:
            xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        xml_str += "        android:gravity=\"center_vertical\"\n"
        xml_str += "        android:text=\"%s\"/>\n" % self.attr_def['Map_Values']
        xml_str += "\n"
        xml_str += "    <!-- End NAME field heading label field -->\n\n"
        return xml_str

    def gen_java_declarations_string(self):
        return ''

    def gen_java_init_string(self):
        return ''

    def gen_java_button_handler(self):
        return ''

    def gen_java_discard_handler(self):
        return ''

    def gen_java_save_handler(self):
        return ''

    def gen_java_reload_handler(self):
        return ''
