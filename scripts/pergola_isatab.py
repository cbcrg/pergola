#!/usr/bin/env python

"""
26 Nov 2014

Script to run pergola from the command line using isatab format
"""

sp = " "

from pergola import parsers
from pergola  import intervals
from pergola  import mapping
# from scripts import pergola_rules
from argparse import ArgumentParser, ArgumentTypeError
from sys      import stderr, exit
import os
# from bcbio import isatab
import pergola_rules


from urllib import urlretrieve, URLopener
from urllib2 import urlopen, URLError, HTTPError

def check_assay_pointer (pointer):
    pass

url = "https://raw.githubusercontent.com/cbcrg/pergola/master/data/feeding_beh_files/20120502_FDF_CRG_hab_DevW1_W2_filt_c1.csv"
# url = "users/cn/jespinosa/Desktop/SB_PhD_list.txt"  
file_name = url.split('/')[-1]

from os.path import expanduser
home_dir = expanduser('~')

path_pergola = os.path.join(home_dir,".pergola/projects")

if not os.path.exists(path_pergola):
    os.makedirs(path_pergola)

path_file = os.path.join(path_pergola, file_name)
print "...............",home_dir
print "...............",path_file

try:
    url_file = urlopen(url)
    
    if not os.path.exists(path_pergola):
        os.makedirs(path_pergola)
    
    file_name = url.split('/')[-1]
    path_file = os.path.join(path_pergola, file_name)
    
    #Check whether file is already created
    if not os.path.exists(path_file):
        local_file = open(path_file, "w")
        local_file.write(url_file.read())
    else:
        print "file has already been downloaded before\n"
except URLError, HTTPError:
    try:
        f = open(url)
    except IOError:
        raise IOError("Pointer inside isatab assays table is either a file in your system or a valid URL")
     
exit("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

print "file name is::::::::::::::::::::::::::", path_file

# "/users/cn/jespinosa/Desktop/test.csv"


# url_file = URLopener()

# url_file.retrieve(url, path_file)

# urlretrieve("https://raw.githubusercontent.com/cbcrg/pergola/master/dat/feeding_beh_files/20120502_FDF_CRG_hab_DevW1_W2_filt_c1.csv", "/users/cn/jespinosa/Desktop/test.csv")
        
# exit("culo...................") #del         

def main():
    parser = ArgumentParser(parents=[parsers.parser])
    
    args = parser.parse_args()
    
    print >> stderr, "@@@Pergola_isatab.py: Input file: %s" % args.input 
    print >> stderr, "@@@Pergola_isatab.py: Configuration file: %s" % args.ontology_file
    print >> stderr, "@@@Pergola_isatab.py: Selected tracks are: ", args.tracks
    
    # I have to check whether when a isatab folder is given if it is actually a folder or a file
    # difference with -i
    if not os.path.isdir(args.input):
        raise ValueError ("Argument input must be a folder containning data in isatab format")
    
    # It might be interesting to check inside the function whether files are url or in path
    dict_files = parsers.parse_isatab_assays (args.input)
    print dict_files
    
    # First try with files in local then with url
    for key in dict_files:
        file_path = dict_files[key]
        print "key %s -----value %s"% (key, dict_files[key]) 
        print "\n file name is::::::::::::::::::::::::::%s   \n" % dict_files[key]
        
        # Here I would implement the download or checking if the file is in local
        # This way you might be able to just download files that you want to process
        
        pergola_rules.main(path=dict_files[key], ontol_file_path=args.ontology_file,
                           sel_tracks=args.tracks, list=args.list, range=args.range,
                           track_actions=args.track_actions, dataTypes_actions=args.dataTypes_actions,
                           write_format=args.format, relative_coord=args.relative_coord,
                           intervals_gen=args.intervals_gen, multiply_f=args.multiply_factor,
                           fields2read=args.fields_read)

    exit ("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")    
#It might be interesting to implement a append option

if __name__ == '__main__':
    exit(main())