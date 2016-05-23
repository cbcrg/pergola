#!/usr/bin/env python

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

# ./extract_trp_features.py -i mat_file

# Loading libraries
from argparse import ArgumentParser
from os.path import basename
from sys import stderr
import numpy as np
import h5py
from time import strptime
from calendar import timegm
from csv import writer

parser = ArgumentParser(description='File input arguments')
parser.add_argument('-i','--input', help='Worms data hdf5 format matlab file', required=True)
# parser.add_argument('-n','--name', help='Name of the matlab file', required=True)

args = parser.parse_args()

print >> stderr, "Input file: %s" % args.input
# print >> stderr, "Input file: %s" % args.name

# # Input file
input_file =  args.input

# input_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/filter_mat_files/mat_worm_data/575 JU440 on food L_2010_11_25__11_38_16___7___1_features.mat'
# input_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/filter_mat_files/mat_worm_data/ocr_4_tm2173.mat'
# input_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/filter_mat_files/mat_worm_data/ocr-4 tm2173 on food L_dummy.mat'
file_name = basename(input_file)

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
genotype_r = f['info']['experiment']['worm']['genotype']
genotype = str(''.join(unichr(c) for c in genotype_r))

# /info/experiment/worm/strain
strain_r = f['info']['experiment']['worm']['strain']
strain = str(''.join(unichr(c) for c in strain_r))

# age worm
# /info/experiment/worm/age
age_r = f['info']['experiment']['worm']['age']
age = str(''.join(unichr(c) for c in age_r))

# /info/experiment/environment/food
food_r = f['info']['experiment']['environment']['food']
food = str(''.join(unichr(c) for c in food_r))

# /info/experiment/environment/timestamp
timestamp_r = f['info']['experiment']['environment']['timestamp']
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

# files were filtered and only include worm videos of at least 20 fps
fps_r = f['info']['video']['resolution']['fps']
fps = fps_r[0][0]

fh = open(file_name + "_loc.csv",'wb')

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

writer_out.writerow(['frame_start', 'frame_end', 'foraging_speed', 'tail_motion', 'crawling'])

# Supplementary figure 6 b (foraging speed when reversing)
# foraging angle speed --> /worm/locomotion/bends/foraging/angleSpeed
# reversing --> backward periods 
# The two info should be intersect

# foraging angle speed
try:
    foraging_speed = f['worm']['locomotion']['bends']['foraging']['angleSpeed']
except KeyError:
    raise KeyError ("Foraging angle speed is corrupted and can not be retrieved from hdf5 file")
                            
# tail motion                            
# This one!!!
# f['worm']['locomotion']['velocity']['head']['direction'][1000][0]
try:
#     tail_motion = f['worm']['locomotion']['velocity']['tail']['direction']
    tail_motion = f['worm']['locomotion']['velocity']['tail']['speed'] #OK
except KeyError:
    raise KeyError ("Tail motion is corrupted and can not be retrieved from hdf5 file")

# Crawling
try:
    crawling = f['worm']['locomotion']['bends']['midbody']['amplitude']
except KeyError:
    raise KeyError ("Crawling is corrupted and can not be retrieved from hdf5 file")
 
for frame in range(0, int(frames)):
# for frame in range(0, 100):    #debug
    list_v = list()
    list_v.extend ([frame, frame+1])
    
    v_fs = abs(foraging_speed[frame][0]) 
    v_tm = abs(tail_motion[frame][0])
    v_c = abs(crawling[frame][0])
    
    if np.isnan(v_fs) : v_fs = -10000
    if np.isnan(v_tm) : v_tm = -10000
    if np.isnan(v_c) : v_c = -10000
    
    list_v.append (v_fs)
    list_v.append (v_tm)
    list_v.append (v_c)

    writer_out.writerows([list_v])

fh.close()

