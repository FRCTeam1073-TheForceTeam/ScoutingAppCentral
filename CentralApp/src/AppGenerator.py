'''
Created on Dec 29, 2012

@author: ksthilaire
'''

import os
import re
import shutil

base_packagename = 'org.team1073.'

'''
    Recursive function that will split a pathname into its a list of 
    parts, up to a maximum depth
'''
def splitpath(path, maxdepth=20):
    ( head, tail ) = os.path.split(path)
    return splitpath(head, maxdepth - 1) + [ tail ] \
         if maxdepth and head and head != path \
         else [ head or tail ]
         
def prepare_destination_project( base_project_path, base_projectname, dest_project_path, dest_projectname, \
                                 dest_activity_prefix, dest_app_name, dest_app_label ):
    
    base_activity = base_projectname + 'Activity'
    dest_activity = dest_activity_prefix + base_activity
    dest_packagename = base_packagename + dest_activity_prefix.lower() + 'scouting'
    
    if os.path.isdir(dest_project_path):
        print 'Project Hierarchy Exists: %s' % dest_project_path
    else:
        print 'Creating Project Hierarchy From Base Project: %s' % dest_project_path    
        shutil.copytree(base_project_path, dest_project_path)
    
        # delete any existing generated files from the copied project
        for gen_dir in ('gen', 'bin'):
            for root, dirs, files in os.walk(os.path.join(dest_project_path, gen_dir)):
                for f in files:
                    if f.endswith('.apk'):
                        os.unlink(os.path.join(root, f))
                for d in dirs:
                    if d == 'classes' or d == 'res':
                        for root2, dirs2, files2 in os.walk(os.path.join(root,d)):
                            for d2 in dirs2:
                                shutil.rmtree(os.path.join(root2,d2))
                    else:
                        shutil.rmtree(os.path.join(root,d))
        
        # rename the src directory hierarchy according to the package name
        package_elem = dest_packagename.split('.')
        src_path = os.path.join(dest_project_path, 'src', package_elem[0], package_elem[1])
        src_dir_list = os.listdir(src_path)
        if len(src_dir_list) != 1:
            raise Exception('Unexpected number of directories in %s' % src_path)   
        os.rename(os.path.join(src_path, src_dir_list[0]), os.path.join(src_path, package_elem[2]))    
        
        # update the java files to reflect the proper package name and to 
        # update the activity name references
        src_path = os.path.join(dest_project_path, 'src', package_elem[0], package_elem[1], package_elem[2])
        files = os.listdir(src_path)
        for f in files:
            java_infile = open(os.path.join(src_path, f),'r')
            java_outfile = open(os.path.join(src_path, (f+'.tmp')),'w')
            for line in java_infile:
                if line.startswith('package '):
                    line = 'package ' + dest_packagename + ';\n'
                elif line.find(dest_activity) == -1:
                    line = line.replace(base_activity, dest_activity)
                java_outfile.write(line)
            java_infile.close()
            java_outfile.close()
            shutil.move(os.path.join(src_path, (f + '.tmp')),os.path.join(src_path, f))   
        shutil.move(os.path.join(src_path, (base_activity + '.java')),os.path.join(src_path, (dest_activity + '.java')))   
    
        # update the .project file to reflect the project name
        project_infile = open(os.path.join(dest_project_path, '.project'), 'r')
        project_outfile = open(os.path.join(dest_project_path, '.project.tmp'), 'w')
        for line in project_infile:
            if line.find(dest_projectname) != -1:
                project_outfile.write(line)
            else:
                newline = line.replace(base_projectname, dest_projectname)
                project_outfile.write(newline)
            
        project_infile.close()
        project_outfile.close()
        shutil.move(os.path.join(dest_project_path, '.project.tmp'),os.path.join(dest_project_path, '.project'))
        
        # update the library references in the project.properties file to properly reference
        # any libraries that are referenced by the base application project
        #
        # first, scan the base and destination paths, looking for the common base directory,
        # and build a relative path from the destination path to the base
        base_path_parts = splitpath(base_project_path)
        dest_path_parts = splitpath(dest_project_path)
        for i in range(len(base_path_parts)):
            if i > len(dest_path_parts):
                break
            if base_path_parts[i] != dest_path_parts[i]:
                break
        library_relative_path = ''
        for j in range(i,len(dest_path_parts)):
            library_relative_path += '../'
        for j in range(i,len(base_path_parts)-1):
            library_relative_path += base_path_parts[j] + '/'
            
        # update the project.properties file to set the path to any referenced libraries based 
        # on the generated relative path
        project_properties_infile = open(os.path.join(dest_project_path, 'project.properties'), 'r')
        project_properties_outfile = open(os.path.join(dest_project_path, 'project.properties.tmp'), 'w')
        for line in project_properties_infile:
            if line.find('android.library.reference') != -1:
                newline = line.replace('../', library_relative_path)
                project_properties_outfile.write(newline)
            else:
                project_properties_outfile.write(line)
        project_properties_infile.close()
        project_properties_outfile.close()
        shutil.move(os.path.join(dest_project_path, 'project.properties.tmp'),os.path.join(dest_project_path, 'project.properties'))
        
        # update the manifest XML file to reflect the package name and activity reference
        manifest_infile = open(os.path.join(dest_project_path, 'AndroidManifest.xml'), 'r')
        manifest_outfile = open(os.path.join(dest_project_path, 'AndroidManifest.xml.tmp'), 'w')
        for line in manifest_infile:
            try:
                line.index('package=')
                parts = line.split('package=',1)
                if parts[1].startswith(dest_packagename):
                    raise 
                newline = parts[0] + 'package=\"' + dest_packagename + '\"\n'
                manifest_outfile.write(newline)
            except:
                if line.find(dest_projectname) == -1:
                    line = line.replace(base_projectname, dest_projectname)
                manifest_outfile.write(line)
        manifest_infile.close()
        manifest_outfile.close()
        shutil.move(os.path.join(dest_project_path, 'AndroidManifest.xml.tmp'),os.path.join(dest_project_path, 'AndroidManifest.xml'))
        
        # update the strings.xml file with the application name and label
        strings_infile = open(os.path.join(dest_project_path, 'res', 'values', 'strings.xml'), 'r')
        strings_outfile = open(os.path.join(dest_project_path, 'res', 'values', 'strings.xml.tmp'), 'w')
        for line in strings_infile:
            if line.find('app_name') != -1:
                line = '    <string name="app_name">' + dest_app_name + '</string>\n'
            if line.find('app_label') != -1:
                line = '    <string name="app_label">' + dest_app_label + '</string>\n'
            strings_outfile.write(line)        
        strings_infile.close()
        strings_outfile.close()
        shutil.move(os.path.join(dest_project_path, 'res', 'values', 'strings.xml.tmp'),os.path.join(dest_project_path, 'res', 'values', 'strings.xml'))

# Modify the main.xml file to include the generated UI code
def update_generated_xml_code(dest_project_path, gen_fragments, use_custom_buttons=False):
    xml_infile = open(os.path.join(dest_project_path, 'res', 'layout', 'main.xml'), 'r')
    xml_outfile = open(os.path.join(dest_project_path, 'res', 'layout', 'main.xml.tmp'), 'w')
    discard_line = False
    for line in xml_infile:
        # if we're using the custom buttons, strip off the UIGEN tag to uncomment
        # the custom button layout
        if 'UIGEN_CUSTOM_BUTTONS' in line:
            if use_custom_buttons and 'xmlns' not in line:    
                line = line.replace('UIGEN_CUSTOM_BUTTONS','android')
                xml_outfile.write(line)
            continue

        # check for the end marker that indicates that need to disable 
        # the line discard mode
        marker_token = get_uigen_token(line)
        if marker_token != None and marker_token[1] == 'END':
            discard_line = False
            
        # write the line to the output file if not in discard mode
        if discard_line == False:
            xml_outfile.write(line)
            
        # check for the begin marker that indicates where to start inserting
        # the generated code and set the discard mode to replace any existing 
        # generated code between the markers
        if marker_token != None and marker_token[1] == 'BEGIN':
            if marker_token[0].find( 'ISSUE' ) != -1:
                tokens = marker_token[0].split('ISSUE')
                index = int(tokens[1][0])
                tokens[1] = tokens[1][2:]
                indexed_marker = tokens[0] + tokens[1]
                discard_line = True
                if gen_fragments.has_key(indexed_marker):
                    xml_outfile.write(gen_fragments[indexed_marker][index])                
            else:
                discard_line = True
                if gen_fragments.has_key(marker_token[0]):
                    xml_outfile.write(gen_fragments[marker_token[0]])

        '''
        if marker_token != None and marker_token[1] == 'BEGIN':
            discard_line = True
            if gen_fragments.has_key(marker_token[0]):
                xml_outfile.write(gen_fragments[marker_token[0]])
        '''
        
    xml_infile.close()
    xml_outfile.close()
    shutil.move(os.path.join(dest_project_path, 'res', 'layout', 'main.xml.tmp'),os.path.join(dest_project_path, 'res', 'layout', 'main.xml'))
    
    # reopen the xml file and scan for last label name so that we can update the
    # Notes xml entry definition to be below that last label
    xml_infile = open(os.path.join(dest_project_path, 'res', 'layout', 'main.xml'), 'r')
    xml_outfile = open(os.path.join(dest_project_path, 'res', 'layout', 'main.xml.tmp'), 'w')
    editing_notes_label = False
    editing_notes_entry = False
    label_above_notes_field = ''
    for line in xml_infile:
        # check for a line that contains an ID string
        if line.find('android:id=') != -1:
            # if we have reached the notes entry, then mark that we are in the xml definition
            # for the notes entry
            if line.find('NotesLabel') != -1:
                editing_notes_label = True
            elif line.find('NotesEntry') != -1:
                editing_notes_entry = True
            elif line.find('Label') != -1:
                label_above_notes_field = line.replace('android:id=', 'android:layout_below=')       
        elif line.find('Last label on control') != -1:
            # some controls will have an explicit comment line that indicates the label of the last
            # field within the control field (e.g. scoring matrix), and if so, then extract the
            # label from the comment line
            tokens = line.split(':')
            label = tokens[1].split('-->')[0].replace(' ', '')
            label_above_notes_field = "        android:layout_below=\"@+id/" + label + "\"\n"

        if editing_notes_label == True:
            if line.find('android:layout_below=') != -1:
                editing_notes_label = False
                line = label_above_notes_field
        if editing_notes_entry == True:
            if line.find('android:layout_below=') != -1:
                editing_notes_entry = False
                line = label_above_notes_field
                
        xml_outfile.write(line)
            
    xml_infile.close()
    xml_outfile.close()
    shutil.move(os.path.join(dest_project_path, 'res', 'layout', 'main.xml.tmp'),os.path.join(dest_project_path, 'res', 'layout', 'main.xml'))
    
    
    

# Modify the main java file to include the generated UI code
def update_generated_java_code(base_projectname, dest_project_path, dest_activity_prefix, gen_fragments):
    base_activity = base_projectname + 'Activity'
    dest_activity = dest_activity_prefix + base_activity
    dest_packagename = base_packagename + dest_activity_prefix.lower() + 'scouting'

    if gen_fragments.has_key('UIGEN:HANDLERS'):
        handler_str = gen_fragments['UIGEN:HANDLERS']
        handler_str = handler_str.replace(base_activity, dest_activity)
        gen_fragments['UIGEN:HANDLERS'] = handler_str
            
    package_elem = dest_packagename.split('.')
    src_path = os.path.join(dest_project_path, 'src', package_elem[0], package_elem[1], package_elem[2])
    java_infile = open(os.path.join(src_path, (dest_activity + '.java')),'r')
    java_outfile = open(os.path.join(src_path, (dest_activity + '.java.tmp')),'w')
    discard_line = False
    for line in java_infile:
        # check for the end marker that indicates that need to disable 
        # the line discard mode
        marker_token = get_uigen_token(line)
        if marker_token != None and marker_token[1] == 'END':
            discard_line = False

        # write the line to the output file if not in discard mode
        if discard_line == False:
            java_outfile.write(line)
            
        # check for the begin marker that indicates where to start inserting
        # the generated code and set the discard mode to replace any existing 
        # generated code between the markers
        if marker_token != None and marker_token[1] == 'BEGIN':
            # if the marker token has the word ISSUE in it, then it is part of a series
            if marker_token[0].find( 'ISSUE' ) != -1:
                tokens = marker_token[0].split('ISSUE')
                index = int(tokens[1][0])
                tokens[1] = tokens[1][2:]
                indexed_marker = tokens[0] + tokens[1]
                if gen_fragments.has_key(indexed_marker):
                    discard_line = True
                    java_outfile.write(gen_fragments[indexed_marker][index])                
            else:
                if gen_fragments.has_key(marker_token[0]):
                    discard_line = True
                    fragment = gen_fragments[marker_token[0]]
                    java_outfile.write(fragment)
                else:
                    print 'Missing fragment for %s' % marker_token[0]
            
    java_infile.close()
    java_outfile.close()
    shutil.move(os.path.join(src_path, (dest_activity + '.java.tmp')),os.path.join(src_path, (dest_activity + '.java')))

def merge_java_activity_file(dest_path, new_file, current_file):
    java_newfile = open(os.path.join(dest_path, new_file),'r')
    java_currentfile = open(os.path.join(dest_path, current_file),'r')
    java_outfile = open(os.path.join(dest_path, current_file + '.tmp'),'w')
    
    '''
    discard_line = False
    for line in java_currentfile:
        # check for the end marker that indicates that need to disable 
        # the line discard mode
        if line.find('UIGEN:VAR_DECLARE_END') != -1:
            discard_line = False
        if line.find('UIGEN:VAR_INIT_END') != -1:
            discard_line = False
        if line.find('UIGEN:SAVE_END') != -1:
            discard_line = False
        if line.find('UIGEN:RELOAD_END') != -1:
            discard_line = False
        if line.find('UIGEN:DISCARD_END') != -1:
            discard_line = False
        if line.find('UIGEN:HANDLERS_END') != -1:
            discard_line = False
            
        # write the line to the output file is not in discard mode
        if discard_line == False:
            java_outfile.write(line)
            
        # check for the markers that indicate where to insert the generated code
        # and set the discard mode to replace any existing generated code between
        # the markers
        if line.find('UIGEN:VAR_DECLARE_BEGIN') != -1:
            discard_line = True
            java_outfile.write(gen_java_var_declarations)
            
        if line.find('UIGEN:VAR_INIT_BEGIN') != -1:
            discard_line = True
            java_outfile.write(gen_java_var_init)
            
        if line.find('UIGEN:SAVE_BEGIN') != -1:
            discard_line = True
            java_outfile.write(gen_java_save_handlers)
            
        if line.find('UIGEN:RELOAD_BEGIN') != -1:
            discard_line = True
            java_outfile.write(gen_java_reload_handlers)
    
        if line.find('UIGEN:DISCARD_BEGIN') != -1:
            discard_line = True
            java_outfile.write(gen_java_discard_handlers)
            
        if line.find('UIGEN:HANDLERS_BEGIN') != -1:
            discard_line = True
            java_outfile.write(gen_java_button_handlers)
    '''
    java_newfile.close()
    java_currentfile.close()
    java_outfile.close()
    
    shutil.move(os.path.join(dest_path, (current_file + '.tmp')),os.path.join(dest_path, current_file))    

# update the base java code from the specified source file, preserving all
# generated and custom java code
def update_base_java_code(base_project_path, base_projectname, dest_project_path ):
    base_activity = base_projectname + 'Activity'
    dest_activity = dest_activity_prefix + base_activity
    dest_packagename = base_packagename + dest_activity_prefix.lower() + 'scouting'

    package_elem = dest_packagename.split('.')
    src_path = os.path.join(dest_project_path, 'src', package_elem[0], package_elem[1])
    src_dir_list = os.listdir(src_path)
    if len(src_dir_list) != 1:
        raise Exception('Unexpected number of directories in %s' % src_path)   
    src_path = os.path.join(src_path, src_dir_list[0])

    dest_src_path = os.path.join(dest_project_path, 'src', package_elem[0], package_elem[1], package_elem[2])

    # copy all the java files from the source directory to the destination directory
    # and update the packagename reference and activity name to reflect this 
    # project.
    files = os.listdir(src_path)
    for f in files:
        java_infile = open(os.path.join(src_path, f),'r')
        
        # modify the activity name if contained in the filename. This
        # will be the case for the main java activity file
        f = f.replace(base_activity, dest_activity)
        
        java_outfile = open(os.path.join(dest_src_path, (f+'.new')),'w')
        for line in java_infile:
            if line.startswith('package '):
                line = 'package ' + dest_packagename + ';\n'
            elif line.find(dest_activity) == -1:
                line = line.replace(base_activity, dest_activity)
            java_outfile.write(line)
        java_infile.close()
        java_outfile.close()
        
    # at this point, we have the new java base files with a .new extension and
    # the current files.
    files = os.listdir(dest_src_path)
    for f in files:
        # for every file that has a .new extension, we will need to either copy
        # that file over any existing .java file, or merge the contents of the new
        # file with the existing file
        if f.endswith('.new'):
            if os.path.exists(os.path.join(dest_src_path, os.path.splitext(f)[0])):
                # we only need to merge the main activity java file; others can 
                # directly copied over
                if f.find(dest_activity) != -1:
                    merge_java_activity_file(dest_src_path, f, os.path.splitext(f)[0])
                else:
                    shutil.move(os.path.join(dest_src_path,f), os.path.join(dest_src_path, os.path.splitext(f)[0]))

def get_marker_token(marker, string):
    token_type = None
    token_start = string.find(marker)
    if token_start != -1:
        token_end = string.find('_BEGIN')
        if token_end != -1:
            token_type = 'BEGIN'
        else:
            token_end = string.find('_END')
            if token_end != -1:
                token_type = 'END'
    if token_type != None:
        return(string[token_start:token_end], token_type)
    else:
        return None
    
def get_uigen_token(string):
    return get_marker_token('UIGEN:', string)
def get_uicustom_token(string):
    return get_marker_token('UICUSTOM:', string)


if __name__ == '__main__':
    
    workspace_dir = os.getcwd()

    base_projectdir = 'ScoutingAppBase'
    base_project_path = os.path.join(workspace_dir, base_projectdir)
    
    dest_projectdir = 'TestProjectDir'
    dest_project_path = os.path.join(workspace_dir, dest_projectdir)
    
    base_projectname = 'ScoutingApp'
    base_packagename = 'org.team1073.'
    
    base_activity = base_projectname + 'Activity'
    
    dest_activity_prefix = 'Test'
    dest_projectname = dest_activity_prefix + base_projectname
    dest_app_name = 'Scouting Application: 2013 Test Application'
    dest_app_label = 'Test Scouter App'
        
    prepare_destination_project( base_project_path, base_projectname, dest_project_path, dest_projectname, \
                                 dest_activity_prefix, dest_app_name, dest_app_label )
    gen_fragments = {}
    
    update_generated_xml_code(dest_project_path, gen_fragments)
    
    update_generated_java_code(base_projectname, dest_project_path, dest_activity_prefix, gen_fragments)

    test_string = '    //// UIGEN:VAR_DECLARE_BEGIN - insert generated code for field variables declarations'
    mytoken = get_uigen_token( test_string )
    print 'mytoken: Token - %s, Type - %s' % (mytoken[0], mytoken[1])
    test_string = '    //// UIGEN:VAR_DECLARE_END - insert generated code for field variables declarations'
    mytoken = get_uigen_token( test_string )
    print mytoken
    test_string = '    //// UICUSTOM:VAR_DECLARE_BEGIN - insert generated code for field variables declarations'
    mytoken = get_uigen_token( test_string )
    print mytoken
    mytoken = get_uicustom_token( test_string )
    print mytoken
    test_string = '    //// UICUSTOM:VAR_DECLARE_END - insert generated code for field variables declarations'
    mytoken = get_uicustom_token( test_string )
    print mytoken
    test_string = '    //// UIGEN:VAR_DECLARE_XXX - insert generated code for field variables declarations'
    mytoken = get_uigen_token( test_string )
    print mytoken
    
    
