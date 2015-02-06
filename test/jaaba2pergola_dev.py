#!/usr/bin/env python

"""
5 feb 2015

Script to transform Jaaba files in matlab format into pergola files
"""
_csv_file_ext = ".csv"

from scipy   import io
from scipy   import nditer
from numpy   import hstack
from numpy   import mean
from os      import getcwd
from sys     import stderr
from os.path import join, exists

jaaba_data = io.loadmat('/Users/jespinosa/JAABA_MAC_0.5.1/sampledata/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/scores_chase.mat')

def jaaba_scores_to_csv (input_file, name_file="JAABA_scores", mode="w", delimiter="\t", path_w=None, norm=False, data_type="a"):
    """   
    Creates a csv file from a scores file produced using JAABA and in matlab
    format
        
    :param mode: :py:func:`str` mode to use by default write
    :param "\t" delimiter: :py:func:`str` Character use to separate values of 
        the same record in file (default "\t").
    :param None path_w: :py:func:`str` path to dump the files, by default None
    :param False norm: set whether data should be normalize (-1,1) using normalization
        factor contained in the file
    :param data_type: :py:func:`str` data type in the file "behavior" e.g. chase
    
    TODO make a dump mode to save the data directly in pergola format
    I will need then the correspondence file, or that input functions or pergola
    allow object and not always files 
    
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
    
    jaaba_data = io.loadmat(input_file)
    
    # Checking JAABA version
    version_jaaba = hstack(hstack(hstack(jaaba_data['version'])))[0][0]
    
    if version_jaaba != '0.5.1':
        print >>stderr, 'JAABA version is not 0.5.1 but %s, this might cause' \
                        'problems is the file structure changed' \
                        % (path + "/" + chrom + _genome_file_ext)
    
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
    scoreFile.write("\t".join(header) + "\n")
    
    if norm:
        scores_flat = scores_flat /score_norm
         
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
            scoreFile.write("\t".join('{}'.format(v) for v in [idx_animal+1, start_time, end_time -1, mean_score, data_type]) + "\n") 

    scoreFile.close()
    
# jaaba_scores_to_csv (input_file='/Users/jespinosa/JAABA_MAC_0.5.1/sampledata/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/scores_chase.mat', path_w='/Users/jespinosa/git/pergola/test')
jaaba_scores_to_csv (input_file='/Users/jespinosa/JAABA_MAC_0.5.1/sampledata_v0.5/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/scores_chase.mat', 
                     path_w='/Users/jespinosa/git/pergola/test', norm=True, data_type="chase")
exit ("You correctly transform your JAABA scores into a csv file (pergola readable)")