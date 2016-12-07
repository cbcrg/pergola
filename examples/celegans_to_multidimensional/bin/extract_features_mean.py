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

# ./extract_N2_features.py -i mat_file

# Loading libraries
from argparse import ArgumentParser
from os.path import basename
from sys import stderr, exit
import numpy as np
import h5py
from time import strptime
from calendar import timegm
from csv import writer

parser = ArgumentParser(description='File input arguments')
parser.add_argument('-i','--input', help='Worms data hdf5 format matlab file', required=True)

### Testear este script con el archivo en el terminar para ver si genera lo que quiero
args = parser.parse_args()

print >> stderr, "Input file: %s" % args.input

# # Input file
input_file =  args.input

# input_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/filter_mat_files/N2_ctrl_for_testing/unc-16e109 on food L_2009_12_09__11_54_10___4___5_features.mat'
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
unix_time
# Some phenotypic features show a variability inside control group that depends
# on hourly measures, thus hour of the day is extracted (Yemini et al, 2013) 
hour = str(my_date_object.tm_hour)

# print  >> stderr, "hour ===== %s" % hour

# /info/video/length/time
time_recorded_r = f['info']['video']['length']['time']
time_recorded = time_recorded_r[0][0]

# /info/video/length/frames
frames_r = f['info']['video']['length']['frames']
frames = frames_r[0][0] 

# files were filtered and only include worm videos of at least 20 fps
fps_r = f['info']['video']['resolution']['fps']
fps = fps_r[0][0]

fh = open(hour + "." + file_name + "." + "multivar.csv",'wb')

# fh.write("#genotype;%s\n" % genotype)
# fh.write("#strain;%s\n" % strain)
# fh.write("#age;%s\n" % age)
# fh.write("#habituation;%s\n" % habituation)
# fh.write("#food;%s\n" % food)
# fh.write("#unix_time;%s\n" % unix_time)
# fh.write("#time_recorded;%s\n" % time_recorded)
# fh.write("#frames;%s\n" % frames)
# fh.write("#fps;%s\n" % fps)
# fh.write("#annotations;%s\n" % annotations)

writer_out = writer(fh, dialect = 'excel-tab')

list_header = ['strain', 'unix_time', 'frame_start', 'frame_end', 'length', 'range', 
               'eccentricity', 'wave_length_primary', 'kinks', 'track_length']

# print >> stderr, "Unix time: %s" % unix_time

### rest of the header
## velocity
for body_part in f['worm']['locomotion']['velocity']:
       
    for k in f['worm']['locomotion']['velocity'][body_part]:
            
        list_header.append("velocity_" + body_part + "_" + k)     
    
## locomotion bends
for body_part in f['worm']['locomotion']['bends']:
        
    for k in f['worm']['locomotion']['bends'][body_part]:
        
        list_header.append("bends_" + body_part + "_" + k)                           
         
# writer_out.writerow(list_header)

### Supplementary figure
### Phenotypic features N2
## /worm/morphology/length
# length worm in microns
try:
    length_worm = f['worm']['morphology']['length']
except KeyError:
    raise KeyError ("Worm length is corrupted and can not be retrieved from hdf5 file")

##/worm/path/range 
# Range in microns
try:
    path_range = f['worm']['path']['range']
except KeyError:
    raise KeyError ("Worm path range is corrupted and can not be retrieved from hdf5 file")

# Eccentricity
try:
    eccentricity = f['worm']['posture']['eccentricity']
except KeyError:
    raise KeyError ("Eccentricity is corrupted and can not be retrieved from hdf5 file")

# Primary wave length
try:
    wave_length_primary = f['worm']['posture']['wavelength']['primary']
except KeyError:
    raise KeyError ("Wave length primary is corrupted and can not be retrieved from hdf5 file")

# Kinks 
try:
    kinks = f['worm']['posture']['kinks']
except KeyError:
    raise KeyError ("Kinks is corrupted and can not be retrieved from hdf5 file")

# tracklength 
try:
    track_length = f['worm']['posture']['tracklength']
except KeyError:
    raise KeyError ("Track length is corrupted and can not be retrieved from hdf5 file")

list_v = list()
list_v.append(strain)
list_v.append(unix_time)

for idx, list_feature in enumerate([length_worm, path_range, eccentricity, wave_length_primary, kinks, track_length]):
     list_v.append (np.nanmean(np.absolute(np.array(list_feature))))

for body_part in f['worm']['locomotion']['velocity']:
       
    for k in f['worm']['locomotion']['velocity'][body_part]:             
        try:
            list_feature = f['worm']['locomotion']['velocity'][body_part][k]
        except KeyError:
            raise KeyError ("Field %s is corrupted and can not be retrieved from hdf5 file"
                            % ("velocity_" + body_part + "_" + k))
        
        list_v.append (np.nanmean(np.absolute(np.array(list_feature))))
          
for body_part in f['worm']['locomotion']['bends']:
       
    for k in f['worm']['locomotion']['bends'][body_part]:                    
        try:
            list_feature_b = f['worm']['locomotion']['bends'][body_part][k]            
        except KeyError:
            raise KeyError ("Field %s is corrupted and can not be retrieved from hdf5 file"
                            % ("velocity_" + body_part + "_" + k))
        
        list_v.append (np.nanmean(np.absolute(np.array(list_feature_b))))    

writer_out.writerows([list_v])

fh.close()
  
# exit ("==============================culo")