#!/usr/bin/env python

"""
30 oct 2014

Script to run pergola from the command line
"""

from pergola  import intervals
from pergola  import mapping
# from pergola  import tracks
from argparse import ArgumentParser
from sys      import stderr
# from re       import match
import os
from pergola import parsers


# _dt_act_options = ['all', 'one_per_channel']
# _tr_act_options = ['split_all', 'join_all', 'join_odd', 'join_even'] 

def main(path, ontol_file_path, sel_tracks=None, list=None, range=None, track_actions=None, 
         dataTypes_actions=None, dataTypes_list=None, write_format=None, relative_coord=False, intervals_gen=False,
         multiply_f=None, no_header=False, fields2read=None, window_size=None, no_track_line=False):
    
    print >> stderr, "@@@Pergola_rules.py: Input file: %s" % path 
    print >> stderr, "@@@Pergola_rules.py: Configuration file: %s" % ontol_file_path
    
    #Tracks selected by user
    print >> stderr, "@@@Pergola_rules.py: Selected tracks are: ", sel_tracks
    
    #Configuration file
    ontol_file_dict = mapping.OntologyInfo(ontol_file_path)
    
    # Handling list or range of tracks to join if set
    if list and range:
        raise ValueError("Argument -l/--list and -r/--range are not compatible. " \
                         "As both arguments set tracks to be joined.")    
    elif (list):
        tracks2merge = list
    elif (range):
        tracks2merge = range
    else:
        tracks2merge = ""
    
    if tracks2merge: print >> stderr, "Tracks to join are: ", tracks2merge
    
    # Handling argument track actions
    if tracks2merge and track_actions:
        raise ValueError ("Options --list -l or --range -r are incompatible with " \
                          "--track_actions -a, please change your options")
    
    track_act = track_actions
    print >> stderr, "@@@Pergola_rules.py: Track actions are: ", track_act
    
    data_types_list = dataTypes_list
    print >> stderr, "@@@Pergola_rules.py: dataTypes list is: ", data_types_list
      
    # Handling argument dataTypes actions
    dataTypes_act = dataTypes_actions
    print >> stderr, "@@@Pergola_rules.py: dataTypes actions are: ", dataTypes_act
    
    # Handling argument format    
    if write_format:
        print >> stderr, "@@@Pergola_rules.py format to write files: ", write_format
    else:
        write_format='bed' # TODO simplify code, give default to arparse is simpler
        print >>stderr, "@@@Pergola_rules.py format to write files has been set" \
                        " to default value:", write_format
     
    # Handling relative coordinates
    print >> stderr, "@@@Pergola_rules.py: Relative coordinates set to: %s" % relative_coord
    
    # Handling intervals_gen
    print >> stderr, "@@@Pergola_rules.py: Intervals parameter set to: %s" % intervals_gen
    
    # Handling multiply_intervals
    if multiply_f:
        print >>stderr, "@@@Pergola_rules.py: Multiply intervals parameter set to: %s" % multiply_f                        
    else:
        multiply_f = 1
    
    print >> stderr, "@@@Pergola_rules.py: Selected tracks are: ", sel_tracks
    
    header_sw = True
    
    if no_header:
        header_sw = False
        print >> stderr, "@@@Pergola_rules.py: Data file has header set to: ", header_sw

    # Handling multiply_factor
    if fields2read:
        print >>stderr, "@@@Pergola_rules.py: Fields to read from the file are: %s" % fields2read                        
    else:
        fields2read = None    
    
    if window_size:
        print >>stderr, "@@@Pergola_rules.py: Window size set to: %d" % window_size
    else:
        window_size = 300
        print >>stderr, "@@@Pergola_rules.py: Window size set to default: %d" % window_size
#         print >>stderr, 'Chromosome fasta like file will be dump into \"%s\" ' \
#                         'as it has not been set using path_w' % (pwd)
    #Track line--> some genome browsers such as savant do not display correctly the file when the track line is in the file
    print "no_track_line set to........................................................: %s" % no_track_line
    if no_track_line:
        track_line=False
    else:
        track_line=True
        
    print >>stderr, "@@@Pergola_rules.py: track_line set to........................................................: %s" % track_line
        
    ################
    # Reading data
#     intData = structures.IntData(path, ontology_dict=ontol_file_dict.correspondence, intervals=intervals_gen, multiply_t=1000)
#     intData = structures.IntData(path, ontology_dict=ontol_file_dict.correspondence, intervals=intervals_gen, multiply_t=multiply_f)
#     intData = intervals.IntData(path, ontology_dict=ontol_file_dict.correspondence, intervals=intervals_gen, multiply_t=multiply_f)
#     intData = intervals.IntData(path, ontology_dict=ontol_file_dict.correspondence, 
#                                 fields_names=fields2read, intervals=intervals_gen, 
#                                 multiply_t=multiply_f)
    intData = intervals.IntData(path, ontology_dict=ontol_file_dict.correspondence, 
                                fields_names=fields2read, intervals=intervals_gen, 
                                multiply_t=multiply_f, header=header_sw)
    
    
    print "tracks before call are------------------------",intData.tracks
    
    if track_act: tracks2merge = parsers.read_track_actions(tracks=intData.tracks, track_action=track_act)
    
    print "tracks 2 merge .....................",tracks2merge
    
    mapping.write_chr (intData)#mantain
        
#    write_cytoband(self, end, mode="w", start=0, delta=43200, path_w=None):
    data_read = intData.read(relative_coord=True)    
    
    start = intData.min
    end = intData.max
    
    print "min>>>>>>>>>>>>>>>>>>>", start
    print "max>>>>>>>>>>>>>>>>>>>", end
    
    if relative_coord:
       start = 0
       end = intData.max - intData.min
     
    print "min>>>>>>>>>>>>>>>>>>>", start
    print "max>>>>>>>>>>>>>>>>>>>", end
    
#     mapping.write_cytoband(intData, end=end, start=26953, delta=43200)
    # I don't need anymore the start to be shift because files are trimmed
    mapping.write_cytoband(intData, end=end)
    
#     print ">>>>>>>>>>>>>>>>>>>>>>>>>>>data_read.dataTypes",data_read.dataTypes

    # Save the data in a text file similar to the original read file
    data_read.save_track()
    
#     for i in data_read.data:
# #         print i
#         pass
    
        
    bed_str =  data_read.convert(mode=write_format, tracks=sel_tracks, tracks_merge=tracks2merge, 
                                 data_types=data_types_list, dataTypes_actions=dataTypes_act, 
                                 window=window_size)
    
     
#     ## Tracks in sel_tracks is just to set tracks to be kept and which ones to be remove
#     ## Quiza en tracks tambien deberia permitir que se metieran list y ranges pero entonces lo que deberia hacer es poner una
#     ## funcion comun para procesar esto en las dos opciones
#     ## however tracks_merge are the trakcs to be join

    for key in bed_str:
#         print "key.......: ",key#del
        bedSingle = bed_str[key]
        print "::::::::::::::",bedSingle.dataTypes
        # TODO add an if checking whether it is a bedgraph or not to get the mean 
#         bedGraph_mean = bedSingle.win_mean()
#         print bedGraph_mean
        bedSingle.save_track(track_line=track_line)
#         print "Tracks in the file", bedSingle.track
        
#         bedSingle.convert(mode=write_format, tracks=sel_tracks) 
        
#         for i in bedSingle:
#             print i 
#     print intData.fieldsG                                   
#     iter=intData.read(intervals_gen=True)
#buscar al manera de que si esta timepoint en el configuration file entonces crea de uno
    
#     for  i in iter:
#         print i                                  
                                      
                                    
                                    
                               

if __name__ == '__main__':
        
    parser_pergola_rules = ArgumentParser(parents=[parsers.parent_parser])        
    
    # Eventually adding arguments only for pergola_rules
#     parser_pergola_rules.add_argument('-fo', '--foo', required=False, metavar="FOO", help='Foo is foo')

    args = parser_pergola_rules.parse_args()
    
    exit(main(path=args.input, ontol_file_path=args.ontology_file, sel_tracks=args.tracks, 
              list=args.list, range=args.range, track_actions=args.track_actions, 
              dataTypes_actions=args.dataTypes_actions, dataTypes_list=args.dataTypes_list,
              write_format=args.format, relative_coord=args.relative_coord, intervals_gen=args.intervals_gen, 
              multiply_f=args.multiply_intervals, no_header=args.no_header, 
              fields2read=args.fields_read, window_size=args.window_size, 
              no_track_line=args.no_track_line))