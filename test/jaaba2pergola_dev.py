#!/usr/bin/env python

"""
5 feb 2015

Script to transform Jaaba files in matlab format into pergola files
"""
_csv_ext = ".csv"

from scipy import io
from scipy import nditer
from numpy import hstack
from numpy import mean
from os      import getcwd
from sys     import stderr
from os.path import join, exists

jaaba_data = io.loadmat('/Users/jespinosa/JAABA_MAC_0.5.1/sampledata/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/scores_chase.mat')

start_times = jaaba_data['allScores']['t0s']
end_times = jaaba_data['allScores']['t1s']
scores = jaaba_data['allScores']['scores']

start_times_flat = hstack(hstack(hstack(start_times)))
end_times_flat = hstack(hstack(hstack(end_times)))
scores_flat = hstack(hstack(hstack(scores)))

print "\t".join(["animal", "startTime", "endTime", "value"])

# I can calculate the mean score
for idx_animal, start_times_animal in enumerate (start_times_flat):
    start_times_animal= hstack(start_times_animal)
    end_times_animal = hstack(end_times_flat [idx_animal])
    scores_animal = hstack(scores_flat [idx_animal]) 
    
    for idx_time, start_time in enumerate (start_times_animal):
        end_time = end_times_animal[idx_time]
        mean_score = mean(scores_animal[start_time:end_time])
        print "animal......start_time.....end_time....mean_score", idx_animal+1, start_time, end_time, mean_score  




def write_chr(self, mode="w", path_w=None):
    """
    
    Creates a fasta file of the length of the range of value inside the IntData object
    that will be use for the mapping the data into it
    
    :param mode: :py:func:`str` mode to use by default write
    :param None path_w: :py:func:`str` path to dump the files, by default None 
    
    """
    chrom = 'chr1'
    path = ""
    
    if not path_w: 
        path = getcwd()
        print >>stderr, 'Chromosome fasta like file will be dump into \"%s\" ' \
                       'as it has not been set using path_w' % (path)
    else:
        path = path_w
                            
    genomeFile = open(join(path, chrom + _genome_file_ext), mode)        
    genomeFile.write(">" + chrom + "\n")
    genomeFile.write (_generic_nt * (self.max - self.min) + "\n")
    print "-----------------------", self.max - self.min
    genomeFile.close()
    print >>stderr, 'Genome fasta file created: %s' % (path + "/" + chrom + _genome_file_ext)


def jaaba_scores_to_csv (input_file, name_file="JAABA_scores", mode="w", delimiter="\t", path_w=None):
    """   
    Creates a csv file from a scores file produced using JAABA and in matlab
    format
        
    :param mode: :py:func:`str` mode to use by default write
    :param "\t" delimiter: :py:func:`str` Character use to separate values of 
        the same record in file (default "\t").
    :param None path_w: :py:func:`str` path to dump the files, by default None

    TODO make a dump mode to save the data directly in pergola format
    I will need then the correspondence file, or that input functions or pergola
    allow object and not always files 
    
    """
    chrom = 'chr1'
    path = ""
    
    if not path_w: 
        path = getcwd()
        print >>stderr, 'CSV file will be dump into \"%s\" ' \
                       'as not path has been set in path_w' % (path)
    else:
        if exists(path_w):
            path = path_w
        else:
            raise IOError('Provided path does not exists: %s' % path_w)
     
#                        
#     genomeFile = open(join(path, chrom + _genome_file_ext), mode)        
#     genomeFile.write(">" + chrom + "\n")
#     genomeFile.write (_generic_nt * (self.max - self.min) + "\n")
#     print "-----------------------", self.max - self.min
#     genomeFile.close()
#     print >>stderr, 'Genome fasta file created: %s' % (path + "/" + chrom + _genome_file_ext)

jaaba_scores_to_csv (input_file='/Users/jespinosa/JAABA_MAC_0.5.1/sampledata/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/scores_chase.mat', path_w="/kkk/ldldl/d")
exit ("You correctly transform your JAABA scores into a csv file (pergola readable)")