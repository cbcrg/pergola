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
from os import path

# from bcbio import isatab
import pergola_rules


# from urllib import urlretrieve, URLopener
from urllib2 import urlopen, URLError, HTTPError

home_dir = path.expanduser('~')
path_pergola = path.join(home_dir,".pergola/projects")

url = "https://raw.githubusercontent.com/cbcrg/pergola/master/data/feeding_beh_files/20120502_FDF_CRG_hab_DevW1_W2_filt_c1.csv"
# url = "/users/cn/jespinosa/Desktop/SB_PhD_list.txt"

# check_assay_pointer(url)
      

def main():

    parser_isatab = ArgumentParser(parents=[parsers.parent_parser])        
    parser_isatab.add_argument('-ft', '--file_tab', required=False, metavar="FILE_TAG", help='Tag for file field in isatab')

    args = parser_isatab.parse_args()
    
    print >> stderr, "@@@Pergola_isatab.py: Input file: %s" % args.input 
    print >> stderr, "@@@Pergola_isatab.py: Configuration file: %s" % args.ontology_file
    print >> stderr, "@@@Pergola_isatab.py: Selected tracks are: ", args.tracks
    
    # I have to check whether when a isatab folder is given if it is actually a folder or a file
    # difference with -i
    if not path.isdir(args.input):
        raise ValueError ("Argument input must be a folder containning data in isatab format")
    
    # It might be interesting to check inside the function whether files are url or in path
    dict_files = parsers.parse_isatab_assays (args.input)
    print dict_files
    
    # First try with files in local then with url
    for key in dict_files:
        pointer_file = dict_files[key]
        print "key %s -----value %s"% (key, dict_files[key])
        print ">>>>>>>>>>>>>>>>>>>>>pointer to file is:", pointer_file
        
        # Tengo que relacionar de alguna manera cual es el assay de donde tiene que sacar los archivos
        #Probar varios isatab files 
        
        file_path = parsers.check_assay_pointer(pointer_file, download_path=path_pergola) 
        print "File name is::::::::::::::::::::::::::%s   \n" % file_path
        
#         dataTypes_list=args.dataTypes_list #del
        pergola_rules.main(path=file_path, ontol_file_path=args.ontology_file,
                           sel_tracks=args.tracks, list=args.list, range=args.range,
                           track_actions=args.track_actions, dataTypes_list=args.dataTypes_list,
                           dataTypes_actions=args.dataTypes_actions, write_format=args.format,
                           relative_coord=args.relative_coord, intervals_gen=args.intervals_gen,                        
                           multiply_f=args.multiply_intervals, fields2read=args.fields_read, 
                           window_size=args.window_size)
        
        exit ("Going out to see what do I have here")
#It might be interesting to implement a append option

if __name__ == '__main__':
    exit(main())