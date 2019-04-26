#!/usr/bin/env python
#
#  Copyright (c) 2014-2019, Centre for Genomic Regulation (CRG).
#  Copyright (c) 2014-2019, Jose Espinosa-Carrasco and the respective authors.
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
# import os
from os.path import basename, splitext
from pergola import parsers

def main(args=None):
    parser_pergola_rules = ArgumentParser(parents=[parsers.parent_parser]) 
    
    args = parser_pergola_rules.parse_args()

    multiple_files = False

    if len(args.input) > 1:
        print "@@@Pergola_rules.py: Multiple input files processed"
        multiple_files = True

    for idx, input_file in enumerate(args.input):

        if multiple_files:
            if args.output_file_name is None:
                output_file_n = splitext(basename(input_file))[0]
            else:
                output_file_n = args.output_file_name + "_" + str(idx + 1)
        else:
            output_file_n = args.output_file_name

        pergola_rules(path=input_file, map_file_path=args.mapping_file, sel_tracks=args.tracks,
                      list=args.list, range=args.range, track_actions=args.track_actions,
                      data_types_actions=args.data_types_actions, data_types_list=args.data_types_list,
                      write_format=args.format, relative_coord=args.relative_coord,
                      intervals_gen=args.intervals_gen, interval_step=args.interval_step,
                      multiply_f=args.multiply_intervals, no_header=args.no_header, fields2read=args.fields_read,
                      window_size=args.window_size, no_track_line=args.no_track_line, separator=args.field_separator,
                      bed_lab_sw=args.bed_label, color_dict=args.color_file, window_mean=args.window_mean,
                      value_mean=args.value_mean, min_t=args.min_time, max_t=args.max_time, phases=args.phases,
                      genome=args.genome, output_file_name=output_file_n, starting_phase=args.starting_phase,
                      shift=args.shift)

def pergola_rules(path, map_file_path, sel_tracks=None, list=None, range=None, track_actions=None, 
                  data_types_actions=None, data_types_list=None, write_format=None, relative_coord=False,
                  intervals_gen=False, multiply_f=None, no_header=False, fields2read=None, window_size=None,
                  no_track_line=False, separator=None, bed_lab_sw=False, color_dict=None, window_mean=False,
                  value_mean=False, min_t=None, max_t=None, interval_step=None, phases=False, genome=False,
                  output_file_name=None, starting_phase=False, shift=None):
    
    print >> stderr, "@@@Pergola_rules.py: Input file: %s" % path 
    print >> stderr, "@@@Pergola_rules.py: Configuration file: %s" % map_file_path
    
    # Tracks selected by user
    print >> stderr, "@@@Pergola_rules.py: Selected tracks are: ", sel_tracks
    
    # Configuration file
    map_file_dict = mapping.MappingInfo(map_file_path)
    
    # Reading color dictionary to set data_types
    if color_dict:
        print >> stderr, "@@@Pergola_rules.py: Color for data_types in file............ %s" % color_dict
        d_colors_data_types = parsers.read_colors (color_dict)
    else:
        d_colors_data_types = None    
        
    # Handling list or range of tracks to join if set
    if list and range:
        raise ValueError("@@@Pergola_rules.py: Argument -l/--list and -r/--range are not compatible. " \
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
        write_format = 'bed'
        print >>stderr, "@@@Pergola_rules.py format to write files has been set" \
                        " to default value:", write_format

    # Handling relative coordinates
    print >> stderr, "@@@Pergola_rules.py: Relative coordinates set to................. %s" % relative_coord
    
    # Handling intervals_gen
    print >> stderr, "@@@Pergola_rules.py: Intervals parameter set to.................. %s" % intervals_gen

    # Handling interval_step
    if interval_step:
        if intervals_gen:
            print >> stderr, "@@@Pergola_rules.py: Interval step set to........................ %s" % interval_step
        else:
            raise ValueError("Interval step needs intervals paramater to be set -n/--intervals_gen")

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

    if value_mean:
        print >> stderr, "@@@Pergola_rules.py: Value mean set to....................... %d" % value_mean
    else:
        value_mean = False

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

    start = intData.min
    end = intData.max

    if relative_coord:
        start = 0
        end = intData.max - intData.min

    print >> stderr, "@@@Pergola_rules.py: min time in trajectory......................... %d" % start
    print >> stderr, "@@@Pergola_rules.py: max time in trajectory......................... %d" % end

    if min_t or min_t == 0:
        min_time = min_t
        print >> stderr, "@@@Pergola_rules.py: min_time set by user to.............. %d" % min_t
    else:
        min_time = start

    if max_t:
        max_time = max_t
        print >> stderr, "@@@Pergola_rules.py: max_time set by user to............... %d" % max_t
    else:
        if interval_step:
            max_time = end + interval_step
        else:
            max_time = end + 1

    # Phases option
    print >> stderr, "@@@Pergola_rules.py: Phases file set to............................%s" % phases

    # Genome option
    print >> stderr, "@@@Pergola_rules.py: Genome option set to..........................%s" % genome

    # Output file name
    print >> stderr, "@@@Pergola_rules.py: Output file/s name set t......................%s" % output_file_name

    # Starting phase option
    if starting_phase:
        if phases:
            print >> stderr, "@@@Pergola_rules.py: Starting phase set to.............. %s" % starting_phase
        else:
            raise ValueError("Starting phase needs phases option to be set to true")
    else:
        starting_phase = "light"
    if shift:
        time_shift = shift
        print >> stderr, "@@@Pergola_rules.py: Time shift set to....................... %d" % shift
    else:
        #         window_size = 300
        time_shift = 0
        print >> stderr, "@@@Pergola_rules.py: Window size set by default to............ %d" % window_size

    if multiply_f:
        min_time = min_time * multiply_f
        max_time = max_time * multiply_f

    if track_act: tracks2merge = parsers.read_track_actions(tracks=intData.tracks, track_action=track_act)

    data_read = intData.read(relative_coord=relative_coord,
                             intervals=intervals_gen,
                             multiply_t=multiply_f,
                             min_time=min_time, max_time=max_time,
                             int_step=interval_step)

    if genome:
        # whole trajectory
        # mapping.write_chr(data_read, min_c=start, max_c=end)
        # mapping.write_chr_sizes(data_read, min_c=start, max_c=end)

        # using min and max set by user
        mapping.write_chr(data_read)
        mapping.write_chr_sizes(data_read)

    if phases:
        # writes cytoband and light, dark and light_dark bed files
        mapping.write_cytoband(end=end, start=time_shift, start_phase=starting_phase, track_line=track_line,
                               lab_bed=bed_lab)
        # mapping.write_period_seq(start=0, end=intData.max, delta=43200, name_file="phases_dark", track_line=False)

    ## all intervals not save, in should be an option if necessary to save it
    # data_read.save_track(name_file="all_intervals")

    bed_str = data_read.convert(mode=write_format, tracks=sel_tracks,
                                tracks_merge=tracks2merge, data_types=data_types_list,
                                data_types_actions=data_types_act, window=window_size,
                                mean_win=window_mean, mean_value=value_mean, color_restrictions=d_colors_data_types)
                                #min_t_trim=min_t, max_t_trim=max_t)
    
    for key in bed_str:
        bedSingle = bed_str[key]

        output_file_n = None

        if output_file_name is not None:
            output_file_n = output_file_name + '.' + '_'.join(key)

        bedSingle.save_track(name_file=output_file_n, track_line=track_line, bed_label=bed_lab)

if __name__ == '__main__':
    exit(main())