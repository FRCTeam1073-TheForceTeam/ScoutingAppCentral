'''
Created on Sep 29, 2014

@author: ken_sthilaire
'''
import os
import zipfile

'''
Function will create a compressed zip file with the contents of the source directory
'''
def make_zipfile(output_filename, source_dir):
    relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zipfd:
        for root, dirs, files in os.walk(source_dir):
            for filename in files:
                zipfd.write(os.path.relpath(os.path.join(root, filename), os.path.join(source_dir, '..')))
                