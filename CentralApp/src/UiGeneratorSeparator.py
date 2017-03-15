'''
Created on Feb 19, 2012

@author: Ken
'''

from UiGeneratorControl import UiGenControl

class LineSeparatorUiGenControl( UiGenControl ):
    attr_def = None

    def __init__(self, attr_def=None):
        self.attr_def = attr_def

    def gen_xml_string(self, above_name):
    
        xml_str =  "    <!-- Begin NAME line separator -->\n"

        xml_str += "    <View\n"
        xml_str += "        android:id=\"@+id/NAMELabel\"\n"
        xml_str += "        android:layout_width=\"fill_parent\"\n"
        xml_str += "        android:layout_height=\"1dp\"\n"
        xml_str += "        android:layout_marginTop=\"8dp\"\n"
        xml_str += "        android:layout_marginBottom=\"8dp\"\n"
        xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        xml_str += "        android:gravity=\"center_vertical|right\"\n"
        xml_str += "        android:background=\"@android:color/darker_gray\" />\n"
        xml_str += "\n"
        
        xml_str += "    <!-- End NAME line separator -->\n\n"
        return xml_str

    def gen_hidden_xml_string(self, item_label, above_item):
        xml_str =  "    <!-- Begin %s line separator -->\n" % item_label

        xml_str += "    <View\n"
        xml_str += "        android:id=\"@+id/%s_Separator\"\n" % item_label
        xml_str += "        android:layout_width=\"fill_parent\"\n"
        xml_str += "        android:layout_height=\"0dp\"\n"
        xml_str += "        android:layout_marginTop=\"0dp\"\n"
        xml_str += "        android:layout_marginBottom=\"0dp\"\n"
        xml_str += "        android:layout_below=\"@+id/%s\"\n" % above_item
        xml_str += "        android:gravity=\"center_vertical|right\"\n"
        xml_str += "        android:background=\"@android:color/black\" />\n"
        xml_str += "\n"
        
        xml_str += "    <!-- End %s line separator -->\n\n" % item_label
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
    
