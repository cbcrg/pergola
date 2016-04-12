#!/usr/bin/env python

# Loading libraries
from argparse import ArgumentParser
from scipy.io  import loadmat
import h5py
from time import strptime
from calendar import timegm
from sys import stderr
import numpy as np
from csv import writer
from os.path import basename

parser = ArgumentParser(description='File input arguments')
parser.add_argument('-i','--input', help='Worms data hdf5 format matlab file', required=True)

args = parser.parse_args()

print ("Input file: %s" % args.input)
print >> stderr, "Input file: %s" % args.input

# Input files
input_file =  args.input
# input_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/575 JU440 on food L_2011_02_17__11_00___3___1_features.mat' #del
# print >> stderr, "Input file: %s" % input_file #del

file_name = basename(input_file).split('.')[0]
file_name = file_name.replace (" ", "_")

f = h5py.File(input_file)

### INFO
sex_r = f['info']['experiment']['worm']['sex']
sex = str(''.join(unichr(c) for c in sex_r))

habituation_r = f['info']['experiment']['worm']['habituation']
habituation = str(''.join(unichr(c) for c in habituation_r))

# annotations (empty)
annotations_r = f['info']['experiment']['environment']['annotations']
annotations = str(''.join(c.astype(str) for c in annotations_r))

# info/experiment/worm/genotype
genotype_r = f['info']['experiment']['worm']['genotype'] #type u2
genotype = str(''.join(unichr(c) for c in genotype_r))

# /info/experiment/worm/strain
strain_r = f['info']['experiment']['worm']['strain']
strain = str(''.join(unichr(c) for c in strain_r))

# age worm
# /info/experiment/worm/age
age_r = f['info']['experiment']['worm']['age'] #type u2
age = str(''.join(unichr(c) for c in age_r))

# /info/experiment/environment/food
food_r = f['info']['experiment']['environment']['food'] #type u2
food = str(''.join(unichr(c) for c in food_r))

# /info/experiment/environment/timestamp
timestamp_r = f['info']['experiment']['environment']['timestamp'] #type u2
timestamp = str(''.join(unichr(c) for c in timestamp_r))

# HH:MM:SS.mmmmmm
my_date_object = strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
unix_time = timegm(my_date_object) # utc based # correct!!!

# /info/video/length/time
time_recorded_r = f['info']['video']['length']['time']
time_recorded = time_recorded_r[0][0]

# /info/video/length/frames
frames_r = f['info']['video']['length']['frames']
frames = frames_r[0][0] 

fps_r = f['info']['video']['resolution']['fps']
fps = fps_r[0][0]

##############
## WORM DATA
# head_v = f['worm']['locomotion']['velocity']['head']['speed']
# headTip_v = f['worm']['locomotion']['velocity']['headTip']['speed']
# midbody_v = f['worm']['locomotion']['velocity']['midbody']['speed']
# tail_v = f['worm']['locomotion']['velocity']['tail']['speed']
# tailTip_v = f['worm']['locomotion']['velocity']['tailTip']['speed']

# tailTip_v[frames-1][0]
# tail_v[frames-1][0]
# midbody_v[frames-1][0]
# head_v[frames-1][0]
# tail_v[frames-1][0]
# headTip_v[frames-1][0]
# tailTip_v[frames-1][0]

## http://stackoverflow.com/questions/31523985/opening-a-corrupted-pytables-hdf5-file
# I damage somehow some of the velocity, when this happens download again the files
# tail_v_ary = np.array(tail_v, dtype='float64')
# midbody_v_ary = np.array(midbody_v, dtype='float64')

velocity_keys = ['head', 'headTip', 'midbody', 'tail', 'tailTip']

# fh = open("/Users/jespinosa/git/pergola/test/c_elegans_data_test/output.csv",'wb')

fh = open(file_name + "_speed.csv",'wb')

fh.write("#genotype;%s\n" % genotype)
fh.write("#strain;%s\n" % strain)
fh.write("#age;%s\n" % age)
fh.write("#habituation;%s\n" % habituation)
fh.write("#food;%s\n" % food)
fh.write("#unix_time;%s\n" % unix_time)
fh.write("#time_recorded;%s\n" % time_recorded)
fh.write("#frames;%s\n" % frames)
fh.write("#fps;%s\n" % fps)
fh.write("#annotations;%s\n" % annotations)

writer_out = writer(fh, dialect = 'excel-tab')

writer_out.writerow(['frame_start', 'frame_end']  + sorted(velocity_keys))
# from os import getcwd, chdir
# getcwd()
# chdir("/Users/jespinosa/git/pergola/test/c_elegans_data_test/")

# range already substract one to frames 
#for frame in range(0, int(frames)):
for frame in range(0, 100):    #del #debug
    list_v = list()
    list_v.extend ([frame, frame+1])
    
    for velocity_k in sorted(velocity_keys):
        try:
            v = f['worm']['locomotion']['velocity'][velocity_k]['speed'][frame][0] 
        except KeyError:
            raise KeyError ("Velocity field %s is corrupted and can not be retrieved from hdf5 file"
                            % (velocity_k, frame))
                            
        if np.isnan(v) : v = -10000
        # This can not be done because I am processing all speed at the same time
        # if np.isnan(v) : continue
        
        list_v.append (v)    
    # print frame
    # print list_v
    
    writer_out.writerows([list_v])

fh.close()

f['worm']['locomotion']['velocity']['midbody']['speed'][13104][0]

# for velocity_k in velocity_keys:
#     print velocity_k
#     v_speed = f['worm']['locomotion']['velocity'][velocity_k]['speed'] 
#     v_speed [np.isnan(v_speed)]= -10000
    
#     for v in v_speed[0:10]:
#         print str(v[0])
    
#     # print v_speed[0:10] #del
#     import csv
#     RESULTS = [
#                 ['apple','cherry','orange','pineapple','strawberry']
#                 ]
#     resultFile = open("output.csv",'wb')
#     wr = csv.writer(resultFile, dialect='excel')
#     wr.writerows(RESULTS)


# for v in tailTip_v[0:10]:
#     print str(v[0])
    
# tailTip_v[np.isnan(tailTip_v)] = -10000

# # How to replace nan by mean values
# # http://stackoverflow.com/questions/18689235/numpy-array-replace-nan-values-with-average-of-columns