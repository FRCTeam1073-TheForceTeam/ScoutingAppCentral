'''
Created on Sep 5, 2014

@author: ken_sthilaire
'''
import PIL.Image
import os


#sizes = [(120,120), (720,720), (1600,1600)]
sizes = [(100,100),(240,240)]

def create_thumbnails_by_directory(dir_name):
    
    # if the directory name starts with a slash, prepend a '.' to make it a relative
    # path from this point.
    if dir_name.startswith('/'):
        dir_name = '.' + dir_name
                
    for root, dirs, files in os.walk(dir_name):
        # strip off any leading '.' in the root path so that the resulting entry
        # will have an absolute path
        #root = root.lstrip('.')
        
        for name in files:
            file_path = os.path.join(root,name).replace('\\','/')
            create_thumbnails_from_image(file_path)
            
    return

def create_thumbnails(imagefiles):
    for imagefile in imagefiles:
        create_thumbnails_from_image(imagefile)
        

def create_thumbnails_from_image(imagefile, overwrite=False):
    
    # split the image file path into individual segments
    path_segments = imagefile.split('/')
    
    # the filename itself is the last segment, and the directory path is everything else
    filebase = path_segments[-1]
    path_segments = path_segments[:-1]
    
    # add the directory name where we will store the thumbnails
    path_segments.append('Thumbnails')
    
    # finally create the path to the directory and make sure that it exists
    path = os.path.join(*path_segments).replace('\\','/')
    try: 
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

    for size in sizes:
        thumbnail = '%s/%dx%d_%s' % (path,size[0],size[1],filebase)
        if (os.path.isfile(thumbnail)==False) or (overwrite==True):
            try:
                image_obj = PIL.Image.open(imagefile)
                image_obj = image_obj.resize((1000,1000))
                image_obj.thumbnail(size)
                image_obj.save(thumbnail)
            except:
                print 'Error creating thumbnail for %s' % filebase


def rotate_image(imagefile, degrees):
    image_obj = PIL.Image.open(imagefile)
    image_obj = image_obj.rotate(degrees)
    image_obj.save(imagefile,True)

def resize_image(imagefile, width,height):
    image_obj = PIL.Image.open(imagefile)
    image_obj = image_obj.resize((width,height))
    image_obj.save(imagefile,True)

