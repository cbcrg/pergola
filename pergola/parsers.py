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
=========================
Module: pergola.parsers
=========================

.. module:: parsers

This module provides the way to read scripts options provided by pergola library.


"""

from sys       import stderr
from argparse  import ArgumentParser, ArgumentTypeError
from re        import match
from os        import makedirs
from os.path   import join, exists, abspath, split, realpath
from scipy.io  import loadmat
from numpy     import hstack, mean, divide, ndenumerate
from tempfile  import NamedTemporaryFile
from mapping   import MappingInfo, check_path
from intervals import IntData
from shutil    import copyfileobj

_csv_file_ext = ".csv"

_dt_act_options = ['all', 'one_per_channel']
_tr_act_options = ['split_all', 'join_all', 'join_odd', 'join_even']

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


###############
### JAABA stuff

def jaaba_scores_to_csv(input_file, name_file="JAABA_scores", mode="w", delimiter="\t", path_w=None, norm=False, data_type="a"):
    """   
    Creates a csv file from a scores file produced using JAABA and in matlab format
        
    :param mode: :py:func:`str` mode to use by default write
    :param "\t" delimiter: :py:func:`str` Character use to separate values of 
        the same record in file (default "\t").
    :param None path_w: :py:func:`str` path to dump the files, by default None
    :param False norm: set whether data should be normalize (-1,1) using normalization
        factor contained in the file
    :param data_type: :py:func:`str` data type in the file "behavior" e.g. chase
    
    """
    
    path = ""
    header = ["animal", "startTime", "endTime", "value", "dataType"]
    if not path_w: 
        path = getcwd()
        print >>stderr, 'CSV file will be dump into \"%s\" ' \
                       'as not path has been set in path_w' % (path)
    else:
        if exists(path_w):
            path = path_w
        else:
            raise IOError('Provided path does not exists: %s' % path_w)
    
    input_file = check_path(input_file)
#     jaaba_data = io.loadmat(input_file)
    jaaba_data = loadmat(input_file)
    
    # Checking JAABA version
    version_jaaba = hstack(hstack(hstack(jaaba_data['version'])))[0][0]
    
    if version_jaaba != '0.5.1':
        print >>stderr, 'WARNING: JAABA version is not 0.5.1 but %s, this might cause ' \
                        'problems if the structure of JAABA files has changed.' \
                        % (version_jaaba)
    
    # Structure of the file can be find here:
    # http://jaaba.sourceforge.net/ApplyingAClassifier.html#ScoresFile
    
    start_times = jaaba_data['allScores']['t0s']
    end_times = jaaba_data['allScores']['t1s']
    scores = jaaba_data['allScores']['scores']
    score_norm = jaaba_data['allScores']['scoreNorm']
    
    start_times_flat = hstack(hstack(hstack(start_times)))
    end_times_flat = hstack(hstack(hstack(end_times)))
    scores_flat = hstack(hstack(hstack(scores)))
    score_norm = hstack(hstack(score_norm))[0][0]
   
    scoreFile = open(join(path, name_file + _csv_file_ext), mode)
    scoreFile.write(delimiter.join(header) + "\n")
    
    if norm:
        #Dirty way of solving problem with ipython notebook, division was not working there        
        score_norm = float(score_norm)
        scores_flat = divide(scores_flat, score_norm)
    
    for idx_animal, start_times_animal in enumerate (start_times_flat):
        start_times_animal= hstack(start_times_animal)
        end_times_animal = hstack(end_times_flat [idx_animal])
        scores_animal = hstack(scores_flat [idx_animal]) 
    
        for idx_time, start_time in enumerate (start_times_animal):
            end_time = end_times_animal[idx_time]
            mean_score = mean(scores_animal[start_time:end_time])            
            # Because we use the convention that the animal is performing the behavior 
            # from frame t to t+1 if it is labeled/classified as performing the behavior 
            # at frame t, allScores.postprocessed{i}(allScores.t1s{i}(j)) will be 0 and 
            # allScores.postprocessed{i}(allScores.t0s{i}(j)) will be 1.
            # that is why I substract one to the end_time
            # In fact in the graphical interface it starts at start_time - 0.5 and ends in 
            # end_time - 0.5
            scoreFile.write(delimiter.join('{}'.format(v) for v in [idx_animal+1, start_time, end_time -1, mean_score, data_type]) + "\n") 

    scoreFile.close()
 
def jaaba_scores_to_intData(input_file, map_jaaba, name_file="JAABA_scores", delimiter="\t", norm=False, data_type="a"):
    """   
    Creates a csv file from a scores file produced using JAABA and in matlab format
    
    :param input_file: path to the JAABA file in matlab format
    :param map_jaaba: path to the mapping files between JAABA data and pergola ontology 
    :param "\t" delimiter: :py:func:`str` Character use to separate values of 
        the same record in file (default "\t").
    :param False norm: set whether data should be normalize (-1,1) using normalization
        factor contained in the file
    :param data_type: :py:func:`str` data type in the file "behavior" e.g. chase
    
    :returns: IntData object
    """
    
    path = ""
    header = ["animal", "startTime", "endTime", "value", "dataType"]
    input_file = check_path(input_file)
    jaaba_data = loadmat(input_file)
        
    # Checking JAABA version
    version_jaaba = hstack(hstack(hstack(jaaba_data['version'])))[0][0]
    
    if version_jaaba != '0.5.1':
        print >>stderr, 'WARNING: JAABA version is not 0.5.1 but %s, this might cause ' \
                        'problems if the structure of JAABA files has changed.' \
                        % (version_jaaba)
    
    # Structure of the file can be find here:
    # http://jaaba.sourceforge.net/ApplyingAClassifier.html#ScoresFile
    start_times = jaaba_data['allScores']['t0s']
    end_times = jaaba_data['allScores']['t1s']
    scores = jaaba_data['allScores']['scores']
    score_norm = jaaba_data['allScores']['scoreNorm']
    
    start_times_flat = hstack(hstack(hstack(start_times)))
    end_times_flat = hstack(hstack(hstack(end_times)))
    scores_flat = hstack(hstack(hstack(scores)))
    score_norm = hstack(hstack(score_norm))[0][0]
    
    temp = NamedTemporaryFile(delete=True)
    temp.write(delimiter.join(header) + "\n")
    
    if norm:
        #Dirty way of solving problem with ipython notebook, division was not working there
        score_norm = float(score_norm)
        scores_flat = divide(scores_flat, score_norm)
         
    for idx_animal, start_times_animal in enumerate (start_times_flat):
        start_times_animal= hstack(start_times_animal)
        end_times_animal = hstack(end_times_flat [idx_animal])
        scores_animal = hstack(scores_flat [idx_animal]) 
    
        for idx_time, start_time in enumerate (start_times_animal):
            end_time = end_times_animal[idx_time]
            mean_score = mean(scores_animal[start_time:end_time])            
            # Because we use the convention that the animal is performing the behavior 
            # from frame t to t+1 if it is labeled/classified as performing the behavior 
            # at frame t, allScores.postprocessed{i}(allScores.t1s{i}(j)) will be 0 and 
            # allScores.postprocessed{i}(allScores.t0s{i}(j)) will be 1.
            # that is why I substract one to the end_time
            # In fact in the graphical interface it starts at start_time - 0.5 and ends in 
            # end_time - 0.5

            temp.write(delimiter.join('{}'.format(v) for v in [idx_animal+1, start_time, end_time -1, mean_score, data_type]) + "\n")

    # rewinds the file handle
    temp.seek(0)

    map_jaaba = check_path(map_jaaba)
    map = MappingInfo(map_jaaba)
    
    int_data_jaaba = IntData(temp.name, map_dict = map.correspondence)     
    temp.close()
    
    return (int_data_jaaba)

def extract_jaaba_features(dir_perframe,  output="csv", map_jaaba=False, delimiter="\t", feature="velmag", path_w=""):
    """   
    Creates a csv file or a IntData object from feature mat files dumped by JAABA in perframe directory in matlab format
    
    :param dir_perframe: path to the JAABA directory where perframe features are dumped
    :param "csv" output: :py:func:`str` sets whether data has to be extracted to a csv or an IntData object
    :param map_jaaba: path to the mapping files between JAABA data and pergola ontology 
    :param "\t" delimiter: :py:func:`str` Character used in the csv output file to separate values of 
        the same record (default "\t").
    :param "velmag" feature: :py:func:`str` data type (feature) to extract e.g. velmag (speed of the center of rotation)
        More features can be found in http://ctrax.sourceforge.net/bmat.html
    :param None path_w: :py:func:`str` path to dump the files
    
    returns: IntData object
    """
    
    input_path = join(dir_perframe, feature + ".mat")
        
    input_file = check_path(input_path)
        
    jaaba_feature = loadmat(input_file)
    
    output_option = ["csv", "IntData"]
    
    if output not in output_option:
            raise ValueError("Option output \'%s\' not allowed. Possible values are %s"%(output_options, ', '.join(['{}'.format(m) for m in output_options])))
    
    temp = NamedTemporaryFile()
    header = ["animal", "startTime", "endTime", "value", "dataType"]
    temp.write(delimiter.join(header) + "\n")
    
    for id_animal, animal_jaaba_feature in enumerate (jaaba_feature['data'][0]):
        animal_jaaba_feature= hstack(animal_jaaba_feature)
        
        for t, v in ndenumerate(animal_jaaba_feature):             
            temp.write(delimiter.join('{}'.format(v) for v in [id_animal+1, t[0], t[0]+1, v, feature]) + "\n")
    
    # rewinds the file handle
    temp.seek(0)
    
    if output == "csv":
        if not path_w: 
            path = getcwd()
            print >>stderr, 'CSV file will be dump into \"%s\" ' \
                           'as not path has been set in path_w' % (path)
        else:
            if exists(path_w):
                path = path_w
            else:
                raise IOError('Provided path does not exists: %s' % path_w)
                
        feature_file = open(join(path, feature + _csv_file_ext), "wb")
                
        copyfileobj(temp, feature_file)
        temp.close()
        
    elif output == "IntData":                        
        map_jaaba = check_path(map_jaaba)
        map = MappingInfo(map_jaaba)
        
        int_data_jaaba = IntData(temp.name, map_dict = map.correspondence)     
        temp.close()
        
        return (int_data_jaaba)
   
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

###############
### Argument parsing
### pergola_rules.py
parent_parser = ArgumentParser(description = 'Script to transform behavioral data into GB readable data', add_help=False)
parent_parser.add_argument('-i', '--input', required=True, metavar="PATH", help='Input file path')
parent_parser.add_argument('-m', '--mapping_file', required=True, metavar="MAPPING_FILE",
                    help='File to set the reciprocity between fields in behavioral file and terms used by Pergola' + \
                    ' and genome browser grammar')
parent_parser.add_argument('-t', '--tracks', required=False, metavar="TRACKS", type=int, nargs='+', 
                    help='List of selected tracks')
parent_parser.add_argument('-l','--list', required=False, metavar="LIST_OF_TRACKS", type=str, nargs='+',
                    help='Numeric list of tracks to be joined in a single genomic like file')### string allowed as some tracks could be named as: track_1, track2....
parent_parser.add_argument('-r', '--range', required=False, type=parse_num_range,
                    help='Numeric range of tracks to be joined in a single genomic like file')
parent_parser.add_argument('-a', '--track_actions', required=False, choices=_tr_act_options,
                    help='Option of action with tracks selected, split_all, join_all,' + \
                         ' join_odd, join_even, join_range or join_list')
parent_parser.add_argument('-dl', '--data_types_list', required=False, metavar="LIST_OF_DATA_TYPES", type=str, nargs='+',
                    help='List of data_types to be joined')
parent_parser.add_argument('-d', '--data_types_actions', required=False, choices=_dt_act_options,
                    help='Unique values of data_types field should be dumped on' + \
                         ' different data structures or not')
parent_parser.add_argument('-f', '--format', required=False, type=str, 
                    help='Write file output format (bed or bedGraph)')
parent_parser.add_argument('-e', '--relative_coord', required=False, action='store_true', 
                    default=False, help='Sets first timepoint' \
                    ' to 0 and make all the others relative to this timepoint')
parent_parser.add_argument('-n', '--intervals_gen', required=False, action='store_true', 
                    default=False, help='Set startChrom and endChrom from just a timepoint in the file' \
                                        'using field set as startChrom')
parent_parser.add_argument('-mi', '--multiply_intervals', metavar='N', type=int, required=False,
                    help='Multiplies value in data_value by the given factor')
parent_parser.add_argument('-nh', '--no_header', required=False, action='store_true', 
                    default=False, help='Data file contains no header')
parent_parser.add_argument('-s', '--fields_read', metavar='FIELDS2READ', type=str, nargs='+',
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
                           default=False, help='Window values average by the window size')

##############
### Argument parsing jaaba_to_pergola.py
jaaba_parser = ArgumentParser(description = 'Script to transform Jaaba annotations into Pergola readable formats', 
                                       add_help=False)

subparsers = jaaba_parser.add_subparsers(help='Calls pergola_rules.py', dest='command')
jaaba_parser_sp = subparsers.add_parser('sp', help="Converts Jaaba data and process it using pergola", parents=[parent_parser])
jaaba_parser_sc = subparsers.add_parser('sc', add_help='Converts scores Jaaba files into csv files')
jaaba_parser_fp = subparsers.add_parser('fp', add_help='Converts Jaaba features using pergola', parents=[parent_parser])
jaaba_parser_fc = subparsers.add_parser('fc', add_help='Converts Jaaba features into csv files')

jaaba_parser_sc.add_argument('-i', '--input', required=True, metavar="PATH", help='Input file path')

jaaba_parser_fc.add_argument('-dj', '--dir_jaaba', required=True, metavar="PATH", help='Path to jaaba features')
jaaba_parser_fc.add_argument('-jf', '--feature', required=True, metavar="LIST_OF_FEATURES", type=str, nargs='+',
                            help='List of features to be extracted, e.g. velmag')
jaaba_parser_fc.add_argument('-dd', '--dumping_dir', required=False, metavar="DUMPING_DIR", help='Input file path')
# jaaba_parser_fp.add_argument('-i', '--input_jaaba_dir', required=True, metavar="PATH", help='Input file path')
jaaba_parser_fp.add_argument('-dj', '--dir_jaaba', required=True, metavar="PATH", help='Path to jaaba features')
jaaba_parser_fp.add_argument('-jf', '--feature', required=True, metavar="LIST_OF_FEATURES", type=str, nargs='+',
                            help='List of features to be extracted, e.g. velmag')
jaaba_parser_fp.add_argument('-dd', '--dumping_dir', required=False, metavar="DUMPING_DIR", help='Input file path')