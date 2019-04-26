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

from scipy.io  import loadmat
from os.path   import join, exists
from mapping   import MappingInfo, check_path
from tempfile  import NamedTemporaryFile

from intervals import IntData
from numpy     import hstack, ndenumerate, mean, divide 
from shutil    import copyfileobj

_csv_file_ext = ".csv"

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
        # Dirty way of solving problem with ipython notebook, division was not working there
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
        # Dirty way of solving problem with ipython notebook, division was not working there
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
