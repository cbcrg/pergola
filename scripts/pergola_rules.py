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
         dataTypes_actions=None, write_format=None, relative_coord=False, intervals_gen=False,
         multiply_f=None, fields2read=None):
    
#     parser = ArgumentParser(parents=[parsers.parser]) #del
#     
#     args = parser.parse_args()
    print >> stderr, "@@@Pergola_rules.py: Input file: %s" % path 
    print >> stderr, "@@@Pergola_rules.py: Configuration file: %s" % ontol_file_path
    
    #Tracks selected by user
    print >> stderr, "@@@Pergola_rules.py: Selected tracks are: ", sel_tracks
    
    #Configuration file
    ontol_file_dict = mapping.OntologyInfo(ontol_file_path)
    
    # Handling list or range of tracks to join if set
    if list and range:
        raise ValueError("Argument -l/--list and -r/--range are not compatible. " \
                         "As both arguments set a tracks to join.")    
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
    
    # Handling multiply_factor
    if multiply_f:
        print >>stderr, "@@@Pergola_rules.py: Multiply factor parameter set to: %s" % multiply_f                        
    else:
        multiply_f = 1
    
    # Handling multiply_factor
    if fields2read:
        print >>stderr, "@@@Pergola_rules.py: Fields to read from the file are: %s" % fields2read                        
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
    
    
    print "tracks before call are------------------------",intData.tracks
    
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
    
    print "tracks 2 merge .....................",tracks2merge
#     print "____________",intData.tracks
#     print "::::::::", intData.data

    
    mapping.write_chr (intData)#mantain
    
#     intData = intData.read(relative_coord=True)
    data_read = intData.read(relative_coord=True)
    
#     intData.read(self, fields=None, relative_coord=False, intervals_gen=False, fields2rel=None, multiply_t=1,**kwargs):
    print "haber que hay aqui", data_read.list_tracks
    print "************type of data_read.data ",type (data_read.data) #list of tuples
    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>data_read.dataTypes",data_read.dataTypes
    print ":::::::::::::::::::::", type (data_read)
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
    
    exit(main(path=args.input, ontol_file_path=args.ontology_file, sel_tracks=args.tracks, 
              list=args.list, range=args.range, track_actions=args.track_actions, 
              dataTypes_actions=args.dataTypes_actions, write_format=args.format, 
              relative_coord=args.relative_coord, intervals_gen=args.intervals_gen, 
              multiply_f=args.multiply_factor, fields2read=args.fields_read))