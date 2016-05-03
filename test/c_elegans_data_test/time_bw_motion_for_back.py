#!/usr/bin/env python

# Loading libraries
from argparse import ArgumentParser
from sys import stderr, exit
from pergola import mapping
from pergola import intervals

# Changing path of BedTools binary in the cluster, otherwise map is not available
# I use Pablo installation
from os.path import expanduser
home = expanduser("~")

# In the cluster I use bedtools Pablo installation, because default cluster version has not map
import pybedtools
if home == "/users/cn/jespinosa" :
    pybedtools.helpers.set_bedtools_path('/users/cn/pprieto/soft/bedtools/bedtools2-2.19.1/bin')


parser = ArgumentParser(description='File input arguments')
parser.add_argument('-f','--forward_file', help='forward bed file', required=True)
parser.add_argument('-b','--backward_file', help='backard bed file', required=True)
parser.add_argument('-m','--bed_mapping', help='Mapping pergola file for bed files', required=True)
parser.add_argument('-c','--chrom_sizes', help='pping pergola file for bed files', required=True)

args = parser.parse_args()

print >> stderr, "Forward file: %s" % args.forward_file
print >> stderr, "Backward file: %s" % args.backward_file
print >> stderr, "Mapping file: %s" % args.bed_mapping
print >> stderr, "Chrom_sizes file: %s" % args.chrom_sizes

# # Input files
forward_file =  args.forward_file
backward_file = args.backward_file
bed_mapping = args.bed_mapping
chrom_sizes = args.chrom_sizes

# forward_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/results_motion_GB/575_JU440_on_food_L_2011_02_17__11_00___3___1_features.matfile_worm.backward.csv.motion.bed'
# backward_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/results_motion_GB/575_JU440_on_food_L_2011_02_17__11_00___3___1_features.matfile_worm.forward.csv.motion.bed'
# bed_mapping = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/bed2pergola.txt'

chr_file_n = "chrom.sizes"

mapping_bed = mapping.MappingInfo(bed_mapping)

forward = intervals.IntData(forward_file, map_dict=mapping_bed.correspondence, header=False, 
                                   fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])
forward_read = forward.read(relative_coord=False)
forward_bed_obj = forward_read.convert(mode="bed")['chr1', '.'].create_pybedtools()

backward = intervals.IntData(backward_file, map_dict=mapping_bed.correspondence, header=False, 
                                    fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])
backward_read = backward.read(relative_coord=False)
backward_bed_obj = backward_read.convert(mode="bed")['chr1', '.'].create_pybedtools()

time_bw_motion_bed = forward_bed_obj.cat(backward_bed_obj).complement(g=chrom_sizes)
time_bw_motion_bed.saveas("time_bw_motion.bed")






# backward_bed_obj.merge()




# bed_BedTools.merge(d=120, stream=True, c=(4,5,6,9), o=("distinct","sum","distinct","collapse")).saveas(merged_tr_f)

# speed_BedTools.intersect(motion_BedTools).saveas(tag_file + ".intersect.bed")



# # input_file = '/Users/jespinosa/2016_worm_DB/ju440_all/575 JU440 on food L_2011_02_17__11_00___3___1_features.mat'
# # input_file = '/Users/jespinosa/2016_worm_DB/ju440_all/575 JU440 on food L_2011_02_17__16_43___3___11_features.mat'
# # input_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/N2 Laura on food R_2011_08_04__15_44_14__10_features.mat'
# # input_file = '/Users/jespinosa/git/pergola/test/c_elegans_data_test/N2 on food R_2011_08_04__15_44_14__10_features.mat'
# file_name = basename(input_file).split('.')[0]
# file_name = file_name.replace (" ", "_")

# f = h5py.File(input_file)