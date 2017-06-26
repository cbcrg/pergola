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
# parser.add_argument('-m','--motion_file', help='Bed file containing worm motion (forward, backward or paused)', required=True)
parser.add_argument('-m','--bed_mapping_file', help='Mapping pergola file for bed files', required=True)
parser.add_argument('-t', '--tag_out', required=False, type=str, help='Tag output file')

args = parser.parse_args()

if args.tag_out:
    tag_file = args.tag_out
else:
    tag_file = "mean_speed_i_motionDir"

print >> stderr, "Bed speed file: %s" % args.phenotypic_file
print >> stderr, "Mapping bed to Pergola file: %s" % args.bed_mapping_file
print >> stderr, "Output tag file: %s" % tag_file

mapping_bed = mapping.MappingInfo(args.bed_mapping_file)
# mapping_bed = mapping.MappingInfo("/Users/jespinosa/git/pergola/test/c_elegans_data_test/bed2pergola.txt")

bed_ph_file = args.phenotypic_file

# bed_ph_file = '/Users/jespinosa/git/pergola/examples/N2_hourly_mean_measures/bin/bed_debug.bed'
int_data_phenotypic = intervals.IntData(bed_ph_file, map_dict=mapping_bed.correspondence, header=False, 
                                   fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])

phenotypic_data_read = int_data_phenotypic.read(relative_coord=False)
bed_obj_phenotypic = phenotypic_data_read.convert(mode="bed")
key_s = bed_obj_phenotypic.keys()[0]
phenotypic_feature_bt = bed_obj_phenotypic[key_s].create_pybedtools()

### Getting mean value of the intervals of the file containing the phenotypic feature:
## Generates a bed file of a single interval of the size of the whole bed file
list_full_length = [(phenotypic_feature_bt[0]["chrom"], phenotypic_feature_bt[0]["start"], phenotypic_feature_bt[phenotypic_feature_bt.count() - 1]["end"], 0)]
bed_full_length = pybedtools.BedTool(list_full_length)

###################
# Generate mean value of the whole period
if phenotypic_feature_bt.count() == 0: 
    print >> stderr, "No intervals inside the bed file\n"
    # When there is any interval we set the mean to zero
    list_no_intervals = [(phenotypic_feature_bt[0]["chrom"], phenotypic_feature_bt[0]["start"], phenotypic_feature_bt[phenotypic_feature_bt.count() - 1]["end"], 0, 0)]
    bed_no_intervals = pybedtools.BedTool(list_no_intervals).saveas(tag_file + ".mean_file.bed")  
else: 
    bed_full_length.map(phenotypic_feature_bt, c=5, o="mean", null=0).saveas (tag_file + ".mean_file.bed")