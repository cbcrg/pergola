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
from bcbio     import isatab #la puedo poner en otra libreria para que no me joda pergola_rules #modify 
                            #creo que quiero decir que asi pergola_rules tiene esta dependencia quiza mejor no tenerla porque es una libreria rara
from os        import makedirs
from os.path   import join, exists, isdir
from urllib2   import urlopen, HTTPError
# from scipy     import io
from scipy.io     import loadmat
from numpy     import hstack, mean, divide
from tempfile  import NamedTemporaryFile
from mapping   import MappingInfo, check_path
from intervals import IntData

_csv_file_ext = ".csv"

_dt_act_options = ['all', 'one_per_channel']
_tr_act_options = ['split_all', 'join_all', 'join_odd', 'join_even']

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
### ISA=Tab Stuff
def parse_isatab_assays(isatab_dir):
    """ 
    Read all files contained in isatab format to be processed by pergola
    
    :param isatab_dir: :py:func:`str` containing the path to isatab data folder
    
    :return: :py:func:`dict` of files to be processed by pergola
     
    TODO: This functions needs that the assays to be process are tag some way
    """
    dict_files = dict()
    
#     if not path.isdir(isatab_dir):
    if not isdir(isatab_dir):
        raise ValueError ("Argument input must be a folder containning data in isatab format")
    
    rec = isatab.parse(isatab_dir) 
    
    #Sample name are the key shared by both study and assay
    for i in rec.studies:
#         print "studies are", i
#         print "..................",i.assays
#         print i.assays.node['metadata']
        for j in i.assays:
#             print "assays are:", j
#             print "-----------", j.nodes
            for file in j.nodes.keys():
#                 print j.nodes[file].metadata['Sample Name'][0]
                key = j.nodes[file].metadata['Sample Name'][0]
#                 print "key.................", key
#                 print "---------------type", type (dict_files)
#                 print "-------------------------",type (key)
                dict_files[key] = file
#                 print "file to process is ------------------",file
    return dict_files

def check_assay_pointer(pointer, download_path):
    """
    Checks whether the argument pointer is the path to a local file or it is a URL
    If it is a URL it downloads the file to $HOME/.pergola if it has not been previously downloaded 
        
    :param pointer: :py:func:`str` path to a file or URL
    :param download_path: :py:func:`str` path to download files if they are specified as an URL  
    
    :returns: path of file to be processed        
    """
    try:
        url_file = urlopen(pointer)
         
#         if not path.exists(download_path):
        if not exists(download_path):
            makedirs(download_path)
         
        file_name = pointer.split('/')[-1]
#         path_file = path.join(download_path, file_name)
        path_file = join(download_path, file_name)
        
        #Check whether file is already created
        if not exists(path_file):
            local_file = open(path_file, "w")
            local_file.write(url_file.read())
            print "\nFile %s has been correctly downloaded to %s"%(file_name, download_path)
            return (path_file) 
        else:
            print "\nFile has already been downloaded before"
            return (path_file)
        
    except ValueError, HTTPError:
        try:
            f = open(pointer)
            print "\nFile %s is already in system"%pointer
            return (pointer)
        except IOError:
            raise IOError("Pointer inside isatab assays table is either a file in your system or a valid URL")

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
        scores_flat_test = divide(scores_flat, score_norm)
         
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
    
    temp = NamedTemporaryFile()
    temp.write(delimiter.join(header) + "\n")
    
    if norm:
        scores_flat_test = divide(scores_flat, score_norm)
         
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

###############
### Argument parsing
    
parent_parser = ArgumentParser(description = 'Script to transform behavioral data into GB readable data', add_help=False)
parent_parser.add_argument('-i', '--input', required=True, metavar="PATH", help='Input file path')
parent_parser.add_argument('-m', '--mapping_file', required=True, metavar="MAPPING_FILE",
                    help='File to set the reciprocity between fields in behavioral file and terms used by Pergola' + \
                    'and genome browser grammar')
parent_parser.add_argument('-t', '--tracks', required=False, metavar="TRACKS", type=int, nargs='+', 
                    help='List of selected tracks')
parent_parser.add_argument('-l','--list', required=False, metavar="LIST_OF_TRACKS", type=str, nargs='+',
                    help='Numeric list of tracks to be joined in a single genomic like file')### string allowed as some tracks could be named as: track_1, track2....
parent_parser.add_argument('-r', '--range', required=False, type=parse_num_range,
                    help='Numeric range of tracks to be joined in a single genomic like file')
parent_parser.add_argument('-a', '--track_actions', required=False, choices=_tr_act_options,
                    help='Option of action with tracks selected, split_all, join_all,' + \
                         ' join_odd, join_even, join_range or join_list')
parent_parser.add_argument('-dl', '--dataTypes_list', required=False, metavar="LIST_OF_DATA_TYPES", type=str, nargs='+',
                    help='List of dataTypes to be joined')
parent_parser.add_argument('-d', '--dataTypes_actions', required=False, choices=_dt_act_options,
                    help='Unique values of dataTypes field should be dumped on' + \
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
                    help='Multiplies value in dataValue by the given factor')
parent_parser.add_argument('-nh', '--no_header', required=False, action='store_true', 
                    default=False, help='Data file contains no header')
parent_parser.add_argument('-s', '--fields_read', metavar='FIELDS2READ', type=str, nargs='+',
                    help='List of fields to read from input file')
parent_parser.add_argument('-w', '--window_size', required=False, metavar="WINDOW_SIZE", type=int, 
                    help='Window size for bedGraph intervals')
parent_parser.add_argument('-nt', '--no_track_line', required=False, action='store_true',
                    default=False, help='Track line no included in the bed file')
parent_parser.add_argument('-fs', '--field_separator', required=False, type=str,
                    default=False, help='Input file field separator')