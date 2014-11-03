#!/usr/bin/env python

"""
30 oct 2014

Script to run pergola from the command line
"""

from pergola  import structures
from pergola  import input
from argparse import ArgumentParser, ArgumentTypeError
from sys      import stderr
from re import match
import os

_dt_act_options = ['all', 'one_per_channel']

def main():
    parser = ArgumentParser(description = 'Script to transform behavioral data into GB readable data')
    parser.add_argument('-i', '--input', required=True, metavar="PATH", help='Input file path')
    parser.add_argument('-c','--config_file', required=False, metavar="ONTOLOGY_FILE",
                        help='''Configuration file with the ontology between fields in behavioral file
                        'and genome browser grammar''')
    parser.add_argument('-t','--tracks', required=False, metavar="TRACKS", type=int, nargs='+', 
                        help='List of selected tracks')
    parser.add_argument('-l','--list', required=False, metavar="LIST_OF_TRACKS", type=str, nargs='+',
                        help='Numeric list of tracks to be joined in a single genomic like file')### string allowed as some tracks could be named as: track_1, track2....
    parser.add_argument('-r','--range', required=False, type=parse_num_range,
                        help='Numeric range of tracks to be joined in a single genomic like file',)
    parser.add_argument('-d','--dataTypes_actions', required=False, choices=_dt_act_options,
                        help='Unique values of dataTypes field should be dumped on' + \
                             ' different data structures or not')
    
    args = parser.parse_args()
    
     
    print >> stderr, "Input file: %s" % args.input
    print >> stderr, "Configuration file: %s" % args.config_file
    print >> stderr, "@@@Pergola_rules.py Selected tracks are: ", args.tracks
    
    path = args.input
    
    #Configuration file
    config_file_path = args.config_file
    config_file_dict = input.ConfigInfo(config_file_path)
    
    #Tracks selected by user
    sel_tracks = args.tracks 
    
    # Handling list or range of tracks to join if set
    if args.list and args.range:
        raise ValueError("Argument -l/--list and -r/--range are not compatible. " \
                         "As both arguments set a tracks to join.")    
    elif (args.list):
        tracks2merge = args.list
    elif (args.range):
        tracks2merge = args.range
    else:
        tracks2merge = ""
    
    if tracks2merge: print >> stderr, "Tracks to join are: ", tracks2merge
    
    # Handling argument dataTypes actions
    dataTypes_act = args.dataTypes_actions
    print >> stderr, "@@@Pergola_rules.py dataTypes actions are: ", dataTypes_act
    
    
    
    
    
    ################
    # Reading data
    intData = structures.IntData(path, ontology_dict=config_file_dict.correspondence)
#     print "____________",intData.tracks
#     print "::::::::", intData.data
    structures.write_chr (intData)
#     intData = intData.read(relative_coord=True)
#     print intData.read(relative_coord=True)
  
      
    ## Tracks in sel_tracks is just to set tracks to be kept and which ones to be remove
    ## Quiza en tracks tambien deberia permitir que se metieran list y ranges pero entonces lo que deberia hacer es poner una
    ## funcion comun para procesar esto en las dos opciones
    ## however tracks_merge are the trakcs to be join
    bed_str =  intData.convert(relative_coord=True, mode = 'bedGraph', tracks=sel_tracks, tracks_merge=tracks2merge, dataTypes_actions=dataTypes_act)
       
#     print bed_str
    for key in bed_str:
        print "key.......: ",key
        bedSingle = bed_str[key]
        bedSingle.write()
#         for i in bedSingle:
#             print i 
                                      
                                      
                                    
                                    
                                    
                                    
                                    
def parse_num_range(string):
    m = match(r'(\d+)(?:-(\d+))?$', string)

    if not m:
        raise ArgumentTypeError("'" + string + "' is not a range of number. Expected '0-5' or '2'.")
    start = m.group(1)
    end = m.group(2) or start
    list_range=list(range(int(start,10), int(end,10)+1))
    set_range=set(['{0}'.format(t) for t in list_range]) #str because track can be set in the form of track_1 for instance
    
    return set_range

if __name__ == '__main__':
    exit(main())