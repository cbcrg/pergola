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

# example execution
# ./celegans_speed_i_motion.py -p midbody.phenotypic_feature.bed -m motion.bed -b bed_map.txt -t "N2"

# Loading libraries
from argparse import ArgumentParser
from os       import path, getcwd
from csv      import writer
from pergola  import mapping
from pergola  import intervals
from sys      import stderr, exit
import pybedtools

parser = ArgumentParser(description='File input arguments')
parser.add_argument('-p','--phenotypic_file', help='Bed file containing a phenotypic feature of the worn', required=True)
parser.add_argument('-m','--motion_file', help='Bed file containing worm motion (forward, backward or paused)', required=True)
parser.add_argument('-b','--bed_mapping_file', help='Mapping pergola file for bed files', required=True)
parser.add_argument('-t', '--tag_out', required=False, type=str, help='Tag output file')

args = parser.parse_args()

if args.tag_out:
    tag_file = args.tag_out
else:
    tag_file = "mean_speed_i_motionDir"

print >> stderr, "Bed speed file: %s" % args.phenotypic_file
print >> stderr, "Bed motion file: %s" % args.motion_file
print >> stderr, "Mapping bed to Pergola file: %s" % args.bed_mapping_file
print >> stderr, "Output tag file: %s" % tag_file

mapping_bed = mapping.MappingInfo(args.bed_mapping_file)
## mapping_bed = mapping.MappingInfo("/Users/jespinosa/git/pergola/test/c_elegans_data_test/bed2pergola.txt")

bed_ph_file = args.phenotypic_file

int_data_phenotypic = intervals.IntData(bed_ph_file, map_dict=mapping_bed.correspondence, header=False, 
                                   fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])

phenotypic_data_read = int_data_phenotypic.read(relative_coord=False)
bed_obj_phenotypic = phenotypic_data_read.convert(mode="bed")
key_s = bed_obj_phenotypic.keys()[0]
phenotypic_feature_bt = bed_obj_phenotypic[key_s].create_pybedtools()

###################
# Generate to BedTool objects containing motion type (forward, backward, paused)
# motion_bed_file = dir_development +  "575_JU440_on_food_L_2011_02_17__11_00___3___1_features_forward.csv.bed"
# motion_bed_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/work/be/c8a7942756ee7053d0f9856e1caa88/bed_speed_no_tr/motion_file'
## motion_bed_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/work/8a/b26a0fbfb292bb573e582ef842b646/tr_1_dt_a.bed'
# motion_bed_file = dir_development + args.motion
motion_bed_file = args.motion_file
int_data_motion = intervals.IntData(motion_bed_file, map_dict=mapping_bed.correspondence, header=False, 
                                    fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])
motion_data_read = int_data_motion.read(relative_coord=False)
bed_obj_motion = motion_data_read.convert(mode="bed")
key_m = bed_obj_motion.keys()[0]
motion_bt = bed_obj_motion[key_m].create_pybedtools()

# intersect phenotypic features and motions
phenotypic_feature_bt.intersect(motion_bt).saveas(tag_file + ".intersect.bed")

# calculates mean of the phenotypic feature for each period of the given motion
phenotypic_feature_means = motion_bt.map(phenotypic_feature_bt, c=5, o="mean", null=0)

# The result of map is a bed object with the original and the mapped fields (mean), thus we keep only the ones
# that will correspond to a typical bed or bedgraph file
fh = open(tag_file + ".mean.bed",'wb')
fh_bG = open(tag_file + ".mean.bedGraph",'wb')

for i in phenotypic_feature_means:    
    fh.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (i[0],i[1],i[2],i[3],i[9],i[5],i[6],i[7],i[8]))
    fh_bG.write("%s\t%s\t%s\t%s\n" % (i[0],i[1],i[2],i[9]))

fh.close()
fh_bG.close()