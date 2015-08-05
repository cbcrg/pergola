#!/usr/bin/env python

"""
5 feb 2015

Script to transform Jaaba files in matlab format into pergola files

Example of how to run this file:

python jaaba2pergola_dev.py
./jaaba2pergola_dev.py 
"""

# from os       import getcwd
# from sys      import stderr
# from os.path  import join, exists
# from scipy    import io #parsers
# from scipy    import nditer
from numpy    import hstack#parsers
from numpy    import mean#parsers
# from pergola  import mapping#parsers
# from pergola  import intervals#parsers
from pergola  import parsers
# from tempfile import NamedTemporaryFile#parsers

# This part has been included in the function
# jaaba_data = io.loadmat('/Users/jespinosa/JAABA_MAC_0.5.1/sampledata/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/scores_chase.mat')


parsers.jaaba_scores_to_csv(input_file='/Users/jespinosa/JAABA_MAC_0.5.1/sampledata_v0.5/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/scores_chase.mat', 
                            path_w='/Users/jespinosa/git/pergola/test', norm=True, data_type="chase")

print ("You correctly transform your JAABA scores into a csv file")

input_jaaba_file = '/Users/jespinosa/JAABA_MAC_0.5.1/sampledata_v0.5/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/scores_chase.mat'
map_file_jaaba = "/Users/jespinosa/git/pergola/test/jaaba2pergola.txt"
int_data_jaaba = parsers.jaaba_scores_to_intData(input_file = input_jaaba_file, map_jaaba = map_file_jaaba, norm=True, data_type="chase")

print int_data_jaaba.min
print int_data_jaaba.max
print int_data_jaaba.tracks
print int_data_jaaba.data

exit ("You correctly transform your JAABA scores into IntData")