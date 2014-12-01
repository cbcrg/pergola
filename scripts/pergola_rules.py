#!/usr/bin/env python

"""
30 oct 2014

Script to run pergola from the command line
"""

from pergola  import intervals
from pergola  import mapping
# from pergola  import tracks
from argparse import ArgumentParser, ArgumentTypeError
from sys      import stderr
# from re       import match
import os
from pergola import parsers


# _dt_act_options = ['all', 'one_per_channel']
# _tr_act_options = ['split_all', 'join_all', 'join_odd', 'join_even'] 

def main(path, ontol_file_path, tracks=None, list=None, range=None, track_actions=None, 
         dataTypes_actions=None, write_format=None, relative_coord=False, intervals_gen=False,
         multiply_factor=None, fields_read=None):
    
#     parser = ArgumentParser(parents=[parsers.parser])
#     
#     args = parser.parse_args()
    print >> stderr, "@@@Pergola_rules.py: Input file: %s" % path 
    print >> stderr, "@@@Pergola_rules.py: Configuration file: %s" % ontol_file_path
    print >> stderr, "@@@Pergola_rules.py: Selected tracks are: ", args.tracks
    
    #Configuration file
    ontol_file_dict = mapping.OntologyInfo(ontol_file_path)
    
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
    
    # Handling argument track actions
    if tracks2merge and args.track_actions:
        raise ValueError ("Options --list -l or --range -r are incompatible with " \
                          "--track_actions -a, please change your options")
    
    track_act = args.track_actions
    print >> stderr, "@@@Pergola_rules.py Track actions are: ", track_act
    
    # Handling argument dataTypes actions
    dataTypes_act = args.dataTypes_actions
    print >> stderr, "@@@Pergola_rules.py dataTypes actions are: ", dataTypes_act
    
    # Handling argument format
    write_format = args.format
    
    if write_format:
        print >> stderr, "@@@Pergola_rules.py format to write files: ", write_format
    else:
        write_format='bed' # TODO simplify code, give default to arparse is simpler
        print >>stderr, "@@@Pergola_rules.py format to write files has been set" \
                        " to default value:", write_format
     
    # Handling relative coordinates
    print >> stderr, "@@@Pergola_rules.py: Relative coordinates set to: %s" % args.relative_coord
    relative_coord = args.relative_coord
    
    # Handling intervals_gen
    print >> stderr, "@@@Pergola_rules.py: Intervals parameter set to: %s" % args.intervals_gen
    intervals_gen = args.intervals_gen
    
    # Handling multiply_factor
    multiply_f = args.multiply_factor
    if multiply_f:
        print >>stderr, "@@@Pergola_rules.py: Multiply factor parameter set to: %s" % args.multiply_factor                        
    else:
        multiply_f = 1
    
    # Handling multiply_factor
    fields2read = args.fields_read
    if fields2read:
        print >>stderr, "@@@Pergola_rules.py: Fields to read from the file are: %s" % args.fields_read                        
    else:
        fields2read = None    
                          
#         print >>stderr, 'Chromosome fasta like file will be dump into \"%s\" ' \
#                         'as it has not been set using path_w' % (pwd)
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
                                multiply_t=multiply_f, header=True)
#     print "..............",intData.range_values #del
#     intData = structures.IntData(path, ontology_dict=ontol_file_dict.correspondence, relative_coord=True) #This one does not make any difference relative_coord
    
    # intData.data although relative_coord is set does not work
    print "intData.data"
#     print intData.data
    print "intData.read()"
#     print intData.read(relative_coord=relative_coord)
    print "----min value",intData.min
    print "----max value",intData.max
    
    if track_act: tracks2merge = parsers.read_track_actions(tracks=intData.tracks, track_action=track_act)
     
#     print "____________",intData.tracks
#     print "::::::::", intData.data

    
    mapping.write_chr (intData)#mantain
    
#     intData = intData.read(relative_coord=True)
    data_read = intData.read(relative_coord=True)
    
#     intData.read(self, fields=None, relative_coord=False, intervals_gen=False, fields2rel=None, multiply_t=1,**kwargs):
    
    print "************type of data_read.data ",type (data_read.data) #list of tuples
    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>data_read.dataTypes",data_read.dataTypes
    data_read.save_track()
    
    for i in data_read.data:
#         print i
        pass
    
    
#     bed_str =  data_read.convert(mode=write_format, tracks=sel_tracks, tracks_merge=tracks2merge, 
#                                  dataTypes_actions=dataTypes_act)
    
    bed_str =  data_read.convert(mode=write_format, tracks=sel_tracks, tracks_merge=tracks2merge, 
                                 dataTypes_actions=dataTypes_act, window=1)
    
     
#     ## Tracks in sel_tracks is just to set tracks to be kept and which ones to be remove
#     ## Quiza en tracks tambien deberia permitir que se metieran list y ranges pero entonces lo que deberia hacer es poner una
#     ## funcion comun para procesar esto en las dos opciones
#     ## however tracks_merge are the trakcs to be join
#     bed_str =  intData.convert(relative_coord=relative_coord, mode=write_format, tracks=sel_tracks, tracks_merge=tracks2merge, dataTypes_actions=dataTypes_act)
#     bed_str =  intData.convert(mode=write_format, tracks=sel_tracks, tracks_merge=tracks2merge, dataTypes_actions=dataTypes_act) 
       
#     print bed_str#del
    for key in bed_str:
        print "key.......: ",key
        bedSingle = bed_str[key]
#         print "::::::::::::::",bedSingle.dataTypes
        bedSingle.save_track()
#         bedSingle.convert(mode=write_format, tracks=sel_tracks) 
        
#         for i in bedSingle:
#             print i 
#     print intData.fieldsG                                   
#     iter=intData.read(intervals_gen=True)
#buscar al manera de que si esta timepoint en el configuration file entonces crea de uno
    
#     for  i in iter:
#         print i                                  
                                      
                                    
                                    
                               

if __name__ == '__main__':
        
    parser = ArgumentParser(parents=[parsers.parser])
    args = parser.parse_args()
    
    exit(main(path=args.input, ontol_file_path=args.ontology_file, tracks=args.tracks))