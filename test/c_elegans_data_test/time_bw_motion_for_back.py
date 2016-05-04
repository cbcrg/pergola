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

## All between time intervals
## it includes a first 0 0 interval that is removed
time_bw_motion_bed_fn = forward_bed_obj.cat(backward_bed_obj).complement(g=chrom_sizes).filter(lambda x: x.start > 0).saveas().fn
pybedtools.BedTool(time_bw_motion_bed_fn).saveas("time_bw_motion.bed")

## To calculate specific transitions we need the complement of all the motion intervals
def window2bed(f):
    "Only keeps the result of the intersection using window"
    new = f[9:12]
    return new

size_win = 2

## Forward to forward 
## bedtools window -a A.bed -b B.bed -l 5000 -r 1000 -sw
## both r and l are needed
time_after_forward_fn = forward_bed_obj.window(pybedtools.BedTool(time_bw_motion_bed_fn), l=0, r=size_win).each(window2bed).saveas().fn#.saveas("time_after_for.bed")
forward_bed_obj.window(pybedtools.BedTool(time_after_forward_fn), l=size_win, r=0).each(window2bed).saveas("time_bw_for_for.bed")

## Backward to backward
time_after_backward_fn = backward_bed_obj.window(pybedtools.BedTool(time_bw_motion_bed_fn), l=0, r=size_win).each(window2bed).saveas().fn#.saveas("time_after_back.bed")
backward_bed_obj.window(pybedtools.BedTool(time_after_backward_fn), l=size_win, r=0).each(window2bed).saveas("time_bw_back_back.bed")

## Forward to backward
backward_bed_obj.window(pybedtools.BedTool(time_after_forward_fn), l=size_win, r=0).each(window2bed).saveas("time_bw_for_back.bed")

## Backward to forward
forward_bed_obj.window(pybedtools.BedTool(time_after_backward_fn), l=size_win, r=0).each(window2bed).saveas("time_bw_back_for.bed")
