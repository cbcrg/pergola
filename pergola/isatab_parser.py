"""
=========================
Module: pergola.parsers
=========================

.. module:: parsers

This module provides the way to read ISA-tab format.


"""

from sys       import stderr
from bcbio     import isatab 
from os.path   import join, isfile, exists, isdir
from urllib2   import urlopen, HTTPError, URLError

def parse_isatab_assays(isatab_dir):
    """ 
    Read all files contained in isatab format to be processed by pergola
    
    :param isatab_dir: :py:func:`str` containing the path to isatab data folder
    
    :return: :py:func:`dict` of files to be processed by pergola
     
    TODO: This functions needs that the assays to be process are tag some way
    """
    dict_files = dict()
    
#     if not path.isdir(isatab_dir):
    if not isdir(isatab_dir):
        raise ValueError ("Argument input must be a folder containning data in isatab format")
    
    rec = isatab.parse(isatab_dir) 
    
    #Sample name are the key shared by both study and assay
    for i in rec.studies:
#         print "studies are", i
#         print "..................",i.assays
#         print i.assays.node['metadata']
        for j in i.assays:
#             print "assays are:", j
#             print "-----------", j.nodes
            for file in j.nodes.keys():
#                 print j.nodes[file].metadata['Sample Name'][0]
                key = j.nodes[file].metadata['Sample Name'][0]
#                 print "key.................", key
#                 print "---------------type", type (dict_files)
#                 print "-------------------------",type (key)
                dict_files[key] = file
#                 print "file to process is ------------------",file
    return dict_files

def check_assay_pointer(pointer, download_path):
    """
    Checks whether the argument pointer is the path to a local file or it is a URL
    If it is a URL it downloads the file to $HOME/.pergola if it has not been previously downloaded 
        
    :param pointer: :py:func:`str` path to a file or URL
    :param download_path: :py:func:`str` path to download files if they are specified as an URL  
    
    :returns: path of file to be processed        
    """
    # We check that the files has not been previously downloaded 
    file_name = pointer.split('/')[-1]
    path_file = join(download_path, file_name)
    
    #Checking if pointer is a file
    if isfile(pointer):
       print >>stderr, "\nPointer in isatab assays \"%s\" is a file in the system" % pointer
       return (pointer)   
    elif exists(path_file):
        print >>stderr, "File has already been downloaded before: %s" % path_file
        return (path_file)
    else:
        if not internet_on():  raise URLError("Check your network connection")
        
        try:
            url_file = urlopen(pointer)
            local_file = open(path_file, "w")
            local_file.write(url_file.read())
            print "\nFile %s has been correctly downloaded to %s"%(file_name, download_path)
            return (path_file)
        except (HTTPError, ValueError):
            raise ValueError("Pointer inside isatab assays table is either a file in your system nor a valid URL %s: " %
                             pointer)
        
def internet_on():
    """
    Checks whether there is an available internet connection
    
    :returns: :py:func:`boolean` True when internet connection is available otherwise False
    """
    try:
        response=urlopen('http://www.google.com', timeout=1)
        return True
    except URLError as err: pass
    return False
