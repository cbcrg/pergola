#!/usr/bin/env python

################################################################
### Jose A Espinosa. CSN/CB-CRG Group. April 2016            ###
################################################################
### Script reads c elegans behavioral DB data in bed format  ###
### generated using pergola_rules.py containing speed for    ###   
### a given body part and and intersect it with intervals    ###  
### encoding motion of the same animal (backward, formward,  ###
### paused). Once files are intersected the mean speed is    ###
### is calculated for the given motion type                  ###
################################################################

# Loading libraries
from argparse import ArgumentParser
import pybedtools
from os import path, getcwd
from pergola import mapping
from pergola import intervals
from sys import stderr, exit

parser = ArgumentParser(description='File input arguments')
parser.add_argument('-s','--speed', help='Bed file containing speed for one body part of the worn', required=True)
parser.add_argument('-m','--motion', help='Bed file containing worm motion (forward, backward or paused)', required=True)
parser.add_argument('-t', '--tag_out', required=False, type=str, help='Tag output file')

args = parser.parse_args()

if args.tag_out:
    tag_file = args.tag_out
else:
    tag_file = "mean_speed_i_motionDir"
    
print >> stderr, "Bed speed file: %s" % args.speed
print >> stderr, "Bed motion file: %s" % args.motion
print >> stderr, "Output tag file: %s" % tag_file

base_dir = path.dirname(getcwd())
dir_development = base_dir + "/c_elegans_data_test/"

# out_dir = base_dir + "/test/"
out_dir = base_dir + "/c_elegans_data_test/"

mapping_bed = mapping.MappingInfo(base_dir + "/" + "bed2pergola.txt")

# speed bed file
# read file from input args
# bed_speed_file = dir_development + "midbody.575_JU440_on_food_L_2011_02_17__16_43___3___11_features_speed.csv.bed"
bed_speed_file = dir_development + args.speed

int_data_speed = intervals.IntData(bed_speed_file, map_dict=mapping_bed.correspondence, header=False, 
                                   fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])

speed_data_read = int_data_speed.read(relative_coord=False)
# speed_data_read.data

###################
# Generate to BedTool objects containing motion type (forward, backward, paused)

# motion_bed_file = dir_development +  "575_JU440_on_food_L_2011_02_17__11_00___3___1_features_forward.csv.bed"
motion_bed_file = dir_development + args.motion

int_data_motion = intervals.IntData(motion_bed_file, map_dict=mapping_bed.correspondence, header=False, 
                                    fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])

speed_data_read = int_data_speed.read(relative_coord=False)
bed_obj_speed = speed_data_read.convert(mode="bed")
speed_BedTools = bed_obj_speed['chr1', '.'].create_pybedtools()

motion_data_read = int_data_motion.read(relative_coord=False)
bed_obj_motion = motion_data_read.convert(mode="bed")
motion_BedTools = bed_obj_motion['chr1', '.'].create_pybedtools()

motion_BedTools.map(speed_BedTools, c=5, o="mean", null=0).saveas(out_dir + tag_file + ".bed")