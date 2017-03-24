#!/usr/bin/env python
#
#  Copyright (c) 2014-2016, Centre for Genomic Regulation (CRG).
#  Copyright (c) 2014-2016, Jose Espinosa-Carrasco and the respective authors.
#
#  This file is part of Pergola.
#
#  Pergola is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pergola is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Pergola.  If not, see <http://www.gnu.org/licenses/>.

"""
30 oct 2014

Script to run pergola from the command line
"""

from pergola  import intervals
from pergola  import mapping
# from pergola  import tracks
from argparse import ArgumentParser
from sys      import stderr, exit
import os
from pergola import parsers

def main(args=None):       
    parser_pergola_rules = ArgumentParser(parents=[parsers.parent_parser]) 
    
    args = parser_pergola_rules.parse_args()
    
    pergola_rules(path=args.input, map_file_path=args.mapping_file, sel_tracks=args.tracks, 
              list=args.list, range=args.range, track_actions=args.track_actions, 
              data_types_actions=args.data_types_actions, data_types_list=args.data_types_list,
              write_format=args.format, relative_coord=args.relative_coord, 
              intervals_gen=args.intervals_gen, multiply_f=args.multiply_intervals, 
              no_header=args.no_header, fields2read=args.fields_read, window_size=args.window_size, 
              no_track_line=args.no_track_line, separator=args.field_separator, 
              bed_lab_sw=args.bed_label, color_dict=args.color_file, window_mean=args.window_mean,
              min_t=args.min_time, max_t=args.max_time)
  
def pergola_rules(path, map_file_path, sel_tracks=None, list=None, range=None, track_actions=None, 
         data_types_actions=None, data_types_list=None, write_format=None, relative_coord=False, intervals_gen=False,
         multiply_f=None, no_header=False, fields2read=None, window_size=None, no_track_line=False, separator=None,
         bed_lab_sw=False, color_dict=None, window_mean=False, min_t=None, max_t=None):
    
    print >> stderr, "@@@Pergola_rules.py: Input file: %s" % path 
    print >> stderr, "@@@Pergola_rules.py: Configuration file: %s" % map_file_path
    
    #Tracks selected by user
    print >> stderr, "@@@Pergola_rules.py: Selected tracks are: ", sel_tracks
    
    #Configuration file
    map_file_dict = mapping.MappingInfo(map_file_path)
    
    # Reading color dictionary to set data_types
    if color_dict:
        print >> stderr, "@@@Pergola_rules.py: Color for data_types in file............ %s" % color_dict
        d_colors_data_types = parsers.read_colors (color_dict)
    else:
        d_colors_data_types = None    
        
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
    
    if tracks2merge: print >> stderr, "@@@Pergola_rules.py: Tracks to join are............ ", tracks2merge
    
    # Handling argument track actions
    if tracks2merge and track_actions:
        raise ValueError ("Options --list -l or --range -r are incompatible with " \
                          "--track_actions -a, please change your options")
    
    track_act = track_actions
    print >> stderr, "@@@Pergola_rules.py: Track actions are.............................. ", track_act
    
    data_types_list = data_types_list
    print >> stderr, "@@@Pergola_rules.py: data_types list is: ", data_types_list
      
    # Handling argument data_types actions
    data_types_act = data_types_actions
    print >> stderr, "@@@Pergola_rules.py: data_types actions are......................... ", data_types_act
    
    # Handling argument format    
    if write_format:
        print >> stderr, "@@@Pergola_rules.py format to write files....................... ", write_format
    else:
        write_format='bed' # TODO simplify code, give default to arparse is simpler
        print >>stderr, "@@@Pergola_rules.py format to write files has been set" \
                        " to default value:", write_format
     
    # Handling relative coordinates
    print >> stderr, "@@@Pergola_rules.py: Relative coordinates set to................. %s" % relative_coord
    
    # Handling intervals_gen
    print >> stderr, "@@@Pergola_rules.py: Intervals parameter set to.................. %s" % intervals_gen
    
    # Handling multiply_intervals
    if multiply_f:
        print >>stderr, "@@@Pergola_rules.py: Multiply intervals parameter set to...... %s" % multiply_f                        
    else:
        multiply_f = 1
    
    print >> stderr, "@@@Pergola_rules.py: Selected tracks are......................... ", sel_tracks
    
    # Setting whether input file has header or not
    header_sw = True
    
    if no_header:
        header_sw = False
        print >> stderr, "@@@Pergola_rules.py: Data file has header set to............. ", header_sw

    # Handling fields to read
    if fields2read:
        print >>stderr, "@@@Pergola_rules.py: Fields to read from the file are......... %s" % fields2read                        
    else:
        fields2read = None    
    
    # When binning data setting the window of time used in seconds
    # if not size provided set to False
    if window_size:
        print >>stderr, "@@@Pergola_rules.py: Window size set to....................... %d" % window_size
    else:
#         window_size = 300        
        window_size = False
        print >>stderr, "@@@Pergola_rules.py: Window size set by default to............ %d" % window_size
    
    if window_mean:
        print >>stderr, "@@@Pergola_rules.py: Window mean set to....................... %d" % window_mean
    else:      
        window_mean = False
        
    if no_track_line:
        track_line=False
    else:
        track_line=True
        
    print >>stderr, "@@@Pergola_rules.py: track_line set to............................ %s" % track_line
    
    # Handling input file field delimiter    
    if not separator:
        separator = "\t"
        print >> stderr, "@@@Pergola_rules.py input file field separator set by default to...... \"\\t\"."
    else:        
        print >>stderr, "@@@Pergola_rules.py input file field separator set to..... \"%s\"" % separator
    
    if bed_lab_sw:
        bed_lab = True
        print >>stderr, "@@@Pergola_rules.py: bed_label set to......................... %s" % bed_lab
    else:
        bed_lab = False

    intData = intervals.IntData(path, map_dict=map_file_dict.correspondence, 
                                fields_names=fields2read,  
                                header=header_sw, delimiter=separator)
    
    if track_act: tracks2merge = parsers.read_track_actions(tracks=intData.tracks, track_action=track_act)
    
    data_read = intData.read(relative_coord=relative_coord, intervals=intervals_gen, multiply_t=multiply_f)
    
    mapping.write_chr (data_read)#mantain 
    mapping.write_chr_sizes (data_read)
       
    start = intData.min
    end = intData.max
    
    print >>stderr, "@@@Pergola_rules.py: min time: %d" % start
    print >>stderr, "@@@Pergola_rules.py: max time: %d" % end
     
    if relative_coord:
       start = 0
       end = intData.max - intData.min
    
    # Handling time range of data to extract
    if min_t:
        print >>stderr, "@@@Pergola_rules.py: Min time to trim...... %d" % min_t                        
    
    if max_t:
        print >>stderr, "@@@Pergola_rules.py: Max time to trim...... %d" % max_t                        
            
    # writes cytoband and light, dark and light_dark bed files
    mapping.write_cytoband(end=end, track_line=track_line, lab_bed=False)
#     mapping.write_period_seq(start=0, end=intData.max, delta=43200, name_file="phases_dark", track_line=False) 
    
    data_read.save_track(name_file="all_intervals")
    
    bed_str =  data_read.convert(mode=write_format, tracks=sel_tracks, tracks_merge=tracks2merge, 
                                 data_types=data_types_list, data_types_actions=data_types_act, 
                                 window=window_size, mean_win=window_mean, color_restrictions=d_colors_data_types,
                                 min_t_trim=min_t, max_t_trim=max_t)
    
    for key in bed_str:
        bedSingle = bed_str[key]
        bedSingle.save_track(track_line=track_line, bed_label=bed_lab)

# if __name__ == '__main__':
#         
#     parser_pergola_rules = ArgumentParser(parents=[parsers.parent_parser])        
#     
#     args = parser_pergola_rules.parse_args()
#     
#     exit(main(path=args.input, map_file_path=args.mapping_file, sel_tracks=args.tracks, 
#               list=args.list, range=args.range, track_actions=args.track_actions, 
#               data_types_actions=args.data_types_actions, data_types_list=args.data_types_list,
#               write_format=args.format, relative_coord=args.relative_coord, 
#               intervals_gen=args.intervals_gen, multiply_f=args.multiply_intervals, 
#               no_header=args.no_header, fields2read=args.fields_read, window_size=args.window_size, 
#               no_track_line=args.no_track_line, separator=args.field_separator, 
#               bed_lab_sw=args.bed_label, color_dict=args.color_file, window_mean=args.window_mean))
if __name__ == '__main__':
    exit(main())