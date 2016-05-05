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

# example execution
# ./celegans_speed_i_motion.py -s midbody.575_JU440_on_food_L_2011_02_17__16_43___3___11_features_speed.csv.bed -m 575_JU440_on_food_L_2011_02_17__11_00___3___1_features_forward.csv.bed

# Loading libraries
from argparse import ArgumentParser

from os import path, getcwd
from csv import writer

# Changing path of BedTools binary in the cluster, otherwise map is not available
# I use Pablo installation
from os.path import expanduser
home = expanduser("~")

# In the cluster I use bedtools Pablo installation, because default cluster version has not map
import pybedtools
if home == "/users/cn/jespinosa" :
    pybedtools.helpers.set_bedtools_path('/users/cn/pprieto/soft/bedtools/bedtools2-2.19.1/bin')

from pergola import mapping
from pergola import intervals
from sys import stderr, exit

parser = ArgumentParser(description='File input arguments')
parser.add_argument('-s','--speed', help='Bed file containing speed for one body part of the worn', required=True)
parser.add_argument('-m','--motion', help='Bed file containing worm motion (forward, backward or paused)', required=True)
parser.add_argument('-b','--bed_mapping', help='Mapping pergola file for bed files', required=True)
parser.add_argument('-t', '--tag_out', required=False, type=str, help='Tag output file')

args = parser.parse_args()

if args.tag_out:
    tag_file = args.tag_out
else:
    tag_file = "mean_speed_i_motionDir"

print >> stderr, "Bed speed file: %s" % args.speed
print >> stderr, "Bed motion file: %s" % args.motion
print >> stderr, "Mapping bed to Pergola file: %s" % args.bed_mapping
print >> stderr, "Output tag file: %s" % tag_file

# base_dir = path.dirname(getcwd())
# dir_development = base_dir + "/c_elegans_data_test/"

# # out_dir = base_dir + "/test/"
# out_dir = base_dir + "/c_elegans_data_test/"

# # mapping_bed = mapping.MappingInfo(base_dir + "/test/" + "bed2pergola.txt")
mapping_bed = mapping.MappingInfo(args.bed_mapping)
## mapping_bed = mapping.MappingInfo("/Users/jespinosa/git/pergola/test/c_elegans_data_test/bed2pergola.txt")

# speed bed file
## read file from input args
# bed_speed_file = dir_development + "midbody.575_JU440_on_food_L_2011_02_17__16_43___3___11_features_speed.csv.bed"
# bed_speed_file ='/Users/jespinosa/git/pergola/test/c_elegans_data_test/results_GB/midbody.575_JU440_on_food_L_2011_02_17__11_00___3___1_features.mat.GB.bed'
## bed_speed_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/work/be/c8a7942756ee7053d0f9856e1caa88/bed_speed_no_tr'

## error to debug nextflow Paolo
# bed_speed_file = dir_development + args.speed

bed_speed_file = args.speed

int_data_speed = intervals.IntData(bed_speed_file, map_dict=mapping_bed.correspondence, header=False, 
                                   fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])

speed_data_read = int_data_speed.read(relative_coord=False)
# speed_data_read.data

###################
# Generate to BedTool objects containing motion type (forward, backward, paused)

# motion_bed_file = dir_development +  "575_JU440_on_food_L_2011_02_17__11_00___3___1_features_forward.csv.bed"
# motion_bed_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/work/be/c8a7942756ee7053d0f9856e1caa88/bed_speed_no_tr/motion_file'
## motion_bed_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/work/8a/b26a0fbfb292bb573e582ef842b646/tr_1_dt_a.bed'
# motion_bed_file = dir_development + args.motion
motion_bed_file = args.motion
int_data_motion = intervals.IntData(motion_bed_file, map_dict=mapping_bed.correspondence, header=False, 
                                    fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])

speed_data_read = int_data_speed.read(relative_coord=False)
bed_obj_speed = speed_data_read.convert(mode="bed")
key_s = bed_obj_speed.keys()[0]
# speed_BedTools = bed_obj_speed['chr1', '.'].create_pybedtools()
speed_BedTools = bed_obj_speed[key_s].create_pybedtools()

motion_data_read = int_data_motion.read(relative_coord=False)
bed_obj_motion = motion_data_read.convert(mode="bed")
key_m = bed_obj_motion.keys()[0]
motion_BedTools = bed_obj_motion[key_m].create_pybedtools()
# motion_BedTools = bed_obj_motion['chr1', '.'].create_pybedtools()

speed_BedTools.intersect(motion_BedTools).saveas(tag_file + ".intersect.bed")

# motion_BedTools.map(speed_BedTools, c=5, o="mean", null=0).saveas(out_dir + tag_file + ".mean.bed")
# motion_BedTools.map(speed_BedTools, c=5, o="mean", null=0).saveas(tag_file + ".mean.bed")

speed_means = motion_BedTools.map(speed_BedTools, c=5, o="mean", null=0)
# speed_means.saveas(tag_file + ".mean.bed")

fh = open(tag_file + ".mean.bed",'wb')
fh_bG = open(tag_file + ".mean.bedGraph",'wb')

for i in speed_means:
    # awk '{OFS="\t"; print $1,$2,$3,$4,$10,$6,$7,$8,$9}'
    fh.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (i[0],i[1],i[2],i[3],i[9],i[5],i[6],i[7],i[8]))
    fh_bG.write("%s\t%s\t%s\t%s\n" % (i[0],i[1],i[2],i[9]))

fh.close()
fh_bG.close()