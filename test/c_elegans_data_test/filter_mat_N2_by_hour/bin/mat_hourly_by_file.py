#!/usr/bin/env python

# Loading libraries
from argparse import ArgumentParser
from os.path import basename
from sys import stderr
import h5py

parser = ArgumentParser(description='File input arguments')
parser.add_argument('-i','--input', help='Worms data hdf5 format matlab file', required=True)
parser.add_argument('-n','--name', help='Name of the matlab file', required=True)

args = parser.parse_args()


print >> stderr, "Input file: %s" % args.input
print >> stderr, "Input file: %s" % args.name

print ("File processed: %s" % args.name)

# Input file
input_file =  args.input

# file_name = basename(input_file)
file_name = args.name

f = h5py.File(input_file)

# files were filetered and only include worm videos of at least 20 fps
fps_r = f['info']['video']['resolution']['fps']
fps = fps_r[0][0]

if fps < 20:
    print "fps < 20 =============== ", file_name

# 14-15 minutes long    
frames_r = f['info']['video']['length']['frames']
frames = frames_r[0][0] 

f['info'].keys()
f['info']['video'].keys()
f['info']['video']['length'].keys()
time_min = f['info']['video']['length']['time'][0][0]/60

if time_min < 14:
    print  "time_min < 14 =============== ", file_name

# /info/experiment/environment/timestamp
timestamp_r = f['info']['experiment']['environment']['timestamp']
timestamp = str(''.join(unichr(c) for c in timestamp_r))

# HH:MM:SS.mmmmmm
my_date_object = strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')

# Some phenotypic features show a variability inside control group that depends
# on hourly measures, thus hour of the day is extracted (Yemini et al, 2013) 
hour = str(my_date_object.tm_hour)
file_name_h =  hour + "." + file_name

print "Time recording time: ", file_name_h
