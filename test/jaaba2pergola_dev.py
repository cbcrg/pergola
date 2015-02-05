#!/usr/bin/env python

"""
5 feb 2015

Script to transform Jaaba files in matlab format into pergola files
"""

from scipy import io
from scipy import nditer
from numpy import hstack
from numpy import mean

mat = io.loadmat('/Users/jespinosa/JAABA_MAC_0.5.1/sampledata/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/scores_chase.mat')
#                  ,struct_as_record=False)
#                  squeeze_me=False, chars_as_strings=False, mat_dtype=True, struct_as_record=True, matlab_compatible=True) 
#                  struct_as_record=True)
#                  , squeeze_me=False)


start_times = mat['allScores']['t0s']
end_times = mat['allScores']['t1s']
scores = mat['allScores']['scores']

start_times_flat = hstack(hstack(hstack(start_times)))
end_times_flat = hstack(hstack(hstack(end_times)))
scores_flat = hstack(hstack(hstack(scores)))

# I can calculate the mean score
for idx_animal, start_times_animal in enumerate (start_times_flat):
    start_times_animal= hstack(start_times_animal)
    end_times_animal = hstack(end_times_flat [idx_animal])
    scores_animal = hstack(scores_flat [idx_animal]) 
    
    for idx_time, start_time in enumerate (start_times_animal):
        end_time = end_times_animal[idx_time]
        mean_score = mean(scores_animal[start_time:end_time])
        print "animal......start_time.....end_time....mean_score", idx_animal+1, start_time, end_time, mean_score  
        
# # ...     print x,
exit ("You are out")