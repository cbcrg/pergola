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
=========================
Module: pergola.parsers
=========================

.. module:: parsers

This module provides the way to read scripts options provided by pergola library.


"""

from _version  import __version__
from sys       import stderr
from argparse  import ArgumentParser, ArgumentTypeError
from re        import match
from os.path   import abspath, split, realpath
from mapping   import check_path

_csv_file_ext = ".csv"

_dt_act_options = ['all', 'one_per_channel']
_tr_act_options = ['split_all', 'join_all', 'join_odd', 'join_even']
_starting_phase_options = ['light', 'dark']

PATH = abspath(split(realpath(__file__))[0])


def parse_num_range(string):
    """ 
    This function generate a numeric range from a string containing the boundaries
    From 1-4 generates a string  
    
    :param tracks: :py:func:`set` of tracks to which track_action should be applied set([1,2])
    :param delimiter: :py:func:`str` option to join tracks (join_all, split_all, join_odd, join_evens)
            
    :return: :py:func:`set` with all the numbers in range as strings
    
    """
    
    m = match(r'(\d+)(?:-(\d+))?$', string)

    if not m:
        raise ArgumentTypeError("'" + string + "' is not a range of number. Expected '0-5' or '2'.")
    start = m.group(1)
    end = m.group(2) or start
    list_range=list(range(int(start,10), int(end,10)+1))
    set_range=set(['{0}'.format(t) for t in list_range]) #str because track can be set in the form of track_1 for instance
    
    return set_range


def read_track_actions (tracks, track_action = "split_all"):
    """ 
    Read track actions and returns a set with the tracks to be joined
    
    :param tracks: :py:func:`set` of tracks to which track_action should be applied set([1,2])
    :param track_action: :py:func:`str` option to join tracks (join_all, split_all, join_odd, join_evens)
    
    :return: :py:func:`set` of tracks to be joined
     
    """
    
    if track_action not in _tr_act_options:
        raise ValueError("Track_action \'%s\' not allowed. Possible values are %s"%(track_action,', '.join(['{}'.format(m) for m in _tr_act_options])))
    
    tracks2merge = ""
    
    if track_action == "join_all":
        tracks2merge = tracks
    elif track_action == 'join_odd':
        tracks2merge = set([t for t in tracks if int(t) % 2])
    elif track_action == 'join_even':
        tracks2merge = set([t for t in tracks if not int(t) % 2])
    else:
        tracks2merge = ""
        
    print >> stderr,"Tracks to merge are: ", ",".join("'{0}'".format(t) for t in tracks2merge)
       
    if not tracks2merge:
        print >> stderr,("No track action applied as track actions \'%s\' can not be applied to list of tracks provided \'%s\'"%(track_action, " ".join(tracks)))
        
    return (tracks2merge)


def read_colors (path_color_file):
    """     
    Reads user colors for each data_type  
    
    :param None path_color_file: :py:func:`str` path to read user color for data_types     
       
    :returns: d_user_color dictionary {'data_type_1': 'orange', 'data_type_2':'blue'}
    
    """

    check_path(path_color_file)
    comment_tag_t = "#"    
    d_user_color = {}                            
    
    with open(path_color_file) as f:    
       
       for row in f:
           
           if(row.startswith(comment_tag_t) or row.startswith('\n')):               
                continue
                       
           row_split = row.rstrip('\n').split('\t') 
           (data_type, color) = row_split
           
           # colors are checked inside tracks.assign_color
           d_user_color[data_type] = color
    
    return d_user_color

""""   
Parsers arguments of pergola_rules.py script (aka pergola)

"""

parent_parser = ArgumentParser(description = 'Script to transform behavioral data into GB readable data', add_help=False)

parent_parser.add_argument('-i', '--input', required=True, metavar="PATH", nargs='+', help='Input file path')
parent_parser.add_argument('-m', '--mapping_file', required=True, metavar="MAPPING_FILE",
                    help='File to set the reciprocity between fields in behavioral file and terms used by Pergola' + \
                    ' and genome browser grammar')
parent_parser.add_argument('-t', '--tracks', required=False, metavar="TRACKS", type=int, nargs='+', 
                    help='List of selected tracks')
parent_parser.add_argument('-l','--list', required=False, metavar="LIST_OF_TRACKS", type=str, nargs='+',
                           help='Numeric list of tracks to be joined in a single genomic like file')### string allowed as some tracks could be named as: track_1, track2....
parent_parser.add_argument('-r', '--range', required=False, type=parse_num_range,
                           help='Numeric range of tracks to be joined in a single genomic like file')
parent_parser.add_argument('-a', '-ta', '--track_actions', required=False, choices=_tr_act_options,
                           help='Option of action with tracks selected, split_all, join_all,' + \
                           ' join_odd, join_even, join_range or join_list')
parent_parser.add_argument('-dl', '--data_types_list', required=False, metavar="LIST_OF_DATA_TYPES", type=str, nargs='+',
                           help='List of data_types to be joined')
parent_parser.add_argument('-d', '--data_types_actions', required=False, choices=_dt_act_options,
                           help='Unique values of data_types field should be dumped on' + \
                           ' different data structures or not')
parent_parser.add_argument('-f', '--format', required=False, type=str, default='bed',
                           help='Write file output format (bed or bedGraph)')
parent_parser.add_argument('-e', '-rel', '--relative_coord', required=False, action='store_true',
                           default=False, help='Sets first timepoint' \
                           ' to 0 and make all the others relative to this timepoint')
parent_parser.add_argument('-n', '-int', '--intervals_gen', required=False, action='store_true',
                           default=None, help='Set startChrom and endChrom from just a timepoint in the file ' \
                           'using field set as startChrom')
parent_parser.add_argument('-ns', '-int_s', '--interval_step', required=False, metavar="INTERVAL_STEP", type=int,
                           default=False, help='Set step to generate intervals from a single time point')
parent_parser.add_argument('-mi', '--multiply_intervals', metavar='N', type=int, required=False,
                           help='Multiplies value in data_value by the given factor')
parent_parser.add_argument('-nh', '--no_header', required=False, action='store_true', 
                           default=False, help='Data file contains no header')
parent_parser.add_argument('-s', '-fr', '--fields_read', metavar='FIELDS2READ', type=str, nargs='+',
                           help='List of fields to read from input file')
parent_parser.add_argument('-w', '--window_size', required=False, metavar="WINDOW_SIZE", type=int, 
                           help='Window size for bedGraph intervals, default value 300')
parent_parser.add_argument('-nt', '--no_track_line', required=False, action='store_true',
                           default=False, help='Track line no included in the bed file')
parent_parser.add_argument('-fs', '--field_separator', required=False, type=str,
                           default=False, help='Input file field separator')
parent_parser.add_argument('-bl', '--bed_label', required=False, action='store_true',
                           default=False, help='Show data_types as name field in bed file')
parent_parser.add_argument('-c', '--color_file', required=False, metavar="PATH_COLOR_FILE", 
                           help='Dictionary assigning colors of data_types path')
parent_parser.add_argument('-wm', '--window_mean', required=False, action='store_true',
                           default=False, help='Window values averaged by the window size')
parent_parser.add_argument('-vm', '--value_mean', required=False, action='store_true',
                           help='Window values averaged by number of items within window')
parent_parser.add_argument('-min', '--min_time', type=int, required=False,
                           help='Initial time point to extract')
parent_parser.add_argument('-max', '--max_time', type=int, required=False,
                           help='Last time point to extract')
parent_parser.add_argument('-ng', '--no_genome', required=False, dest='genome', action='store_false',
                           help='Avoinds the creation of a FASTA file which allows to render a longitudinal trajectory' \
                           ' in a genome browser')
parent_parser.add_argument('-np', '--no_phases', required=False, dest='phases', action='store_false',
                           help='Avoids the creation of a phases bed file')
parent_parser.set_defaults(genome=True)
parent_parser.set_defaults(phases=True)
parent_parser.add_argument('-o', '--output_file_name', help='File name for output files')
parent_parser.add_argument('-sp', '--starting_phase', type=str, required=False, choices=_starting_phase_options,
                           help='Sets the first phase to appear in the phases and cytoband file: light or dark\n')
parent_parser.add_argument('-sh', '--shift', required=False, metavar="TIME_SHIFT", type=int,
                           help='Time shift to be set for the first phase')
parent_parser.add_argument('-v', '--version', action='version', version='%(prog)s {version}'.format(version=__version__))

""""   
Parsers argument of jaaba_to_pergola.py script

"""

jaaba_parser = ArgumentParser(description = 'Script to transform Jaaba annotations into Pergola readable formats', 
                              add_help=False)
jaaba_parser.add_argument('-v', '--version', action='version', version='%(prog)s {version}'.format(version=__version__))

subparsers = jaaba_parser.add_subparsers(help='Calls pergola_rules.py', dest='command')
jaaba_parser_sp = subparsers.add_parser('sp', help="Converts Jaaba data and process it using pergola", parents=[parent_parser])
jaaba_parser_sc = subparsers.add_parser('sc', add_help='Converts scores Jaaba files into csv files')
jaaba_parser_fp = subparsers.add_parser('fp', add_help='Converts Jaaba features using pergola', parents=[parent_parser])
jaaba_parser_fc = subparsers.add_parser('fc', add_help='Converts Jaaba features into csv files')

jaaba_parser_sc.add_argument('-i', '--input', required=True, metavar="PATH", help='Input file path')

jaaba_parser_fc.add_argument('-i', '--input', required=True, metavar="PATH", help='Path to jaaba features')
jaaba_parser_fc.add_argument('-jf', '--feature', required=True, metavar="LIST_OF_FEATURES", type=str, nargs='+',
                            help='List of features to be extracted, e.g. velmag')
jaaba_parser_fc.add_argument('-dd', '--dumping_dir', required=False, metavar="DUMPING_DIR", help='Input file path')
# jaaba_parser_fp.add_argument('-i', '--input_jaaba_dir', required=True, metavar="PATH", help='Input file path')
# jaaba_parser_fp.add_argument('-jd', '--jaaba_dir', required=True, metavar="PATH", help='Path to jaaba features')
jaaba_parser_fp.add_argument('-jf', '--feature', required=True, metavar="LIST_OF_FEATURES", type=str, nargs='+',
                            help='List of features to be extracted, e.g. velmag')
jaaba_parser_fp.add_argument('-dd', '--dumping_dir', required=False, metavar="DUMPING_DIR", help='Input file path')
