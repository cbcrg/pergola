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

# Loading libraries
from argparse import ArgumentParser
from scipy.io  import loadmat
import h5py
from time import strptime
from calendar import timegm
from sys import stderr, exit
import numpy as np
from csv import writer
from os.path import basename
# input_file = "/users/cn/jespinosa/2016_worm_DB/matfiles_all/N2 on food R_2010_02_25__09_43_19___6___1_features.mat" #no 899
# input_file = "/users/cn/jespinosa/2016_worm_DB/matfiles_all/N2 on food R_2010_02_25__09_43_09___2___1_features.mat" #no 23112
# input_file = "/users/cn/jespinosa/2016_worm_DB/matfiles_all/N2 on food R_2010_02_25__09_43_43___4___1_features.mat" #no 23883
# input_file = "/users/cn/jespinosa/2016_worm_DB/matfiles_all/N2 on food L_2010_02_25__09_43___3___1_features.mat" #si 23575.0
# input_file = "file_worm"
parser = ArgumentParser(description='File input arguments')
parser.add_argument('-i','--input', help='Worms data hdf5 format matlab file', required=True)

args = parser.parse_args()

# print ("Input file: %s" % args.input)
print >> stderr, "Input file: %s" % args.input

# # Input files
input_file =  args.input
# input_file = '/Users/jespinosa/2016_worm_DB/ju440_all/575 JU440 on food L_2011_02_17__11_00___3___1_features.mat'
# input_file = '/Users/jespinosa/2016_worm_DB/ju440_all/575 JU440 on food L_2011_02_17__16_43___3___11_features.mat'
# input_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/N2 Laura on food R_2011_08_04__15_44_14__10_features.mat'
# input_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/N2 on food R_2011_08_04__15_44_14__10_features.mat'
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

def get_interv (ary_refs_start, ary_refs_end, writer_obj):
    
    list_interv = list()
    
    for i in range(1, len(ary_refs_start)):
        ref_start = ary_refs_start[i]
        ref_end = ary_refs_end[i]
        
        writer_obj.writerow([f[ref_start][0][0], f[ref_end][0][0], 1000])
        list_interv.append([f[ref_start][0][0], f[ref_end][0][0]])
    
    return (list_interv)

turn_keys = ['omegas', 'upsilons']
# turn_k ='omegas'
# turn_k ='upsilons'
for turn_k in sorted(turn_keys):
    
    fh = open(file_name + "." + turn_k + ".csv",'wb')
    
    fh.write("#genotype;%s\n" % genotype)
    fh.write("#strain;%s\n" % strain)
    fh.write("#age;%s\n" % age)
    fh.write("#habituation;%s\n" % habituation)
    fh.write("#food;%s\n" % food)
    fh.write("#unix_time;%s\n" % unix_time)
    fh.write("#time_recorded;%s\n" % time_recorded)
    fh.write("#frames;%s\n" % frames) # 23575
    fh.write("#fps;%s\n" % fps)
    fh.write("#annotations;%s\n" % annotations)
    
    writer_out = writer(fh, dialect = 'excel-tab')
    
    # header
    writer_out.writerow(['frame_start', 'frame_end', 'value'])
    
    # Some files are corrupted inside this structure
    # This exception writes a fake turn interval avoiding nextflow to stop
    #     ary_start_refs = f['worm']['locomotion']['turns'][turn_k]['frames']['start'][0]
    #     ary_end_refs = f['worm']['locomotion']['turns'][turn_k]['frames']['end'][0]
    try:
        ary_start_refs = f['worm']['locomotion']['turns'][turn_k]['frames']['start'][0]
        ary_end_refs = f['worm']['locomotion']['turns'][turn_k]['frames']['end'][0]
    
    except ValueError:    
        print >> stderr, "@@@extract_worm_turn.py: \"%s\" mat hdf5 format file turns information seems to be corrupted" % input_file
        print >> stderr, "@@@extract_worm_turn.py:  A fake interval 0, 10, 1000 is generated inside: \"%s\"" % (file_name + "." + turn_k + ".csv")
        writer_out.writerow([0, 10, 1000])
        fh.close()
        pass
    else:
        list_data = get_interv (ary_start_refs, ary_end_refs, writer_out)
    
        if list_data == [] : writer_out.writerow([0, 10, 1000])
    
        fh.close()
