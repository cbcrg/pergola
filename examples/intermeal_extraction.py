#!/usr/bin/env python

################################################################
### Jose A Espinosa. CSN/CB-CRG Group. Jan 2016              ###
################################################################
### Script creates BedTools objects from a file containing   ###
### mice feeding behavior and uses tools from pybedtools to  ###
### extract intermeals intervals (complement) and intersect  ###
### them with day and experimental phases.                   ###
### Generates a bed file for each track with the result of   ###
### the above described operations.                          ###
################################################################

import pybedtools
from os import path, getcwd
from pergola import mapping
from pergola import intervals

base_dir = path.dirname(getcwd())
out_dir = base_dir + "/test/"

mapping_data = mapping.MappingInfo(base_dir + "/sample_data/feeding_behavior/b2g.txt")

int_data = intervals.IntData(base_dir + "/sample_data/feeding_behavior/feedingBehavior_HF_mice.csv", map_dict=mapping_data.correspondence)

data_read = int_data.read(relative_coord=True)

###################
# Generate to BedTool objects containing light and dark phases

# Write phases file
mapping.write_cytoband(int_data, end = int_data.max - int_data.min, delta=43200, start_phase="dark")

light_ph_f = out_dir +  "phases_light.bed"
dark_ph_f = out_dir + "phases_dark.bed"
light_bed = pybedtools.BedTool(light_ph_f)
dark_bed = pybedtools.BedTool(dark_ph_f)

# Generate a chr.size file in order to calculate complement of merged meals
chr_file_n = "chrom"
mapping.write_chr_sizes (data_read, path_w=out_dir, file_n=chr_file_n)
chr_file = out_dir + chr_file_n + ".sizes"

# Dictionary to set colors of each type of food
data_type_col = {'food_sc': 'orange', 'food_fat':'blue'}

bed_str = data_read.convert(mode="bed", data_types=["food_sc", "food_fat"], data_types_actions="all", color_restrictions=data_type_col)
mapping_bed = mapping.MappingInfo(out_dir + "/pybed2perg.txt")

# Experimentals phases
# Habituation phase (before high-fat food introduction)
# Development phase (after high-fat food introduction)
mapping_file_data_exp_ph = mapping.MappingInfo(base_dir + "/sample_data/feeding_behavior/f2g.txt")
exp_ph_data = intervals.IntData(base_dir + "/sample_data/feeding_behavior/phases_exp.csv", map_dict=mapping_file_data_exp_ph.correspondence)
data_exp_ph_tr = exp_ph_data.read(relative_coord=True)  
exp_ph_bed = data_exp_ph_tr.convert(mode="bed", dataTypes_actions="all", tracks_merge=exp_ph_data.tracks)


hab_bed = exp_ph_bed [('1_2', 'Habituation phase')].new_create_pybedtools()
dev_bed = exp_ph_bed [('1_2', 'Development phase')].new_create_pybedtools()

# For each track merge feeding acts that are separated by less than 120 seconds (thus generating feeding bouts track)
# Calculates the complement of feeding bouts (intermeal intervals) and intersect them with day and experimental phases
# Dumping results into bed files
for tr, bed in bed_str.iteritems():
    bed_BedTools = bed.new_create_pybedtools()
    bed_merged_fn = bed_BedTools.merge(d=120, stream=True, c=(4,5,6,9), o=("distinct","sum","distinct","collapse")).saveas().fn
    
    pybed_intdata = intervals.IntData(bed_merged_fn, map_dict=mapping_bed.correspondence, header=False, fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])
    pybed_intdata_read = pybed_intdata.read(relative_coord=False)
        
    pybed_tr = pybed_intdata_read.convert(mode="bed", data_types=["food_sc", "food_fat"], dataTypes_actions="all", color_restrictions=data_type_col)
    
    ## Complement
    bed_merged_comp = pybedtools.BedTool(bed_merged_fn).complement(g=chr_file)

    hab_light_intermeals_bed = bed_merged_comp.intersect(hab_bed).intersect(light_bed).saveas('tr_' + '_'.join(tr) + "_compl_hab_light.bed")
    hab_dark_intermeals_bed = bed_merged_comp.intersect(hab_bed).intersect(dark_bed).saveas('tr_' + '_'.join(tr) + "_compl_hab_dark.bed")
    dev_light_intermeals_bed = bed_merged_comp.intersect(dev_bed).intersect(light_bed).saveas('tr_' + '_'.join(tr) + "_compl_dev_light.bed")
    dev_dark_intermeals_bed = bed_merged_comp.intersect(dev_bed).intersect(dark_bed).saveas('tr_' + '_'.join(tr) + "_compl_dev_dark.bed")