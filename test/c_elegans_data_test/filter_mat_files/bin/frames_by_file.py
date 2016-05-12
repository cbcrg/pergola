#!/usr/bin/env python

# Loading libraries
from argparse import ArgumentParser
from os.path import basename
from sys import stderr
import h5py

parser = ArgumentParser(description='File input arguments')
parser.add_argument('-i','--input', help='Worms data hdf5 format matlab file', required=True)

args = parser.parse_args()

print ("Input file: %s" % args.input)
print >> stderr, "Input file: %s" % args.input

# Input file
input_file =  args.input

file_name = basename(input_file)

f = h5py.File(input_file)

# files were filetered and only include worm videos of at least 20 fps
fps_r = f['info']['video']['resolution']['fps']
fps = fps_r[0][0]

if fps < 20:
    print "===============", file_name

# 14-15 minutes long    
frames_r = f['info']['video']['length']['frames']
frames = frames_r[0][0] 

f['info'].keys()
f['info']['video'].keys()
f['info']['video']['length'].keys()
time_min = f['info']['video']['length']['time'][0][0]/60

if time_min < 14:
    print  "===============", file_name


"575 JU440 on food L_2010_11_25__11_38_16___7___1_features.mat" 
# if 

# n_frames = int(frames)

# if n_frames <   

