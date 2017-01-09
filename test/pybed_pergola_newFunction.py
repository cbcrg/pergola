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
total_time = int_data.max - int_data.min
mapping.write_cytoband(end = total_time, delta=43200, start_phase="dark")
light_ph_f = out_dir +  "phases_light.bed"
dark_ph_f = out_dir + "phases_dark.bed"
all_phases = out_dir + "phases.bed"

light_bed = pybedtools.BedTool(light_ph_f)
dark_bed = pybedtools.BedTool(dark_ph_f)
all_phases_bed = pybedtools.BedTool(all_phases)

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


hab_bed = exp_ph_bed [('1_2', 'Habituation phase')].create_pybedtools()
dev_bed = exp_ph_bed [('1_2', 'Development phase')].create_pybedtools()

# def comp_with_value (comp_int):    
# #     int + (int[2]-int[1])
# #     print int(comp_int[2]) - int(comp_int[1])
#     score = int(comp_int[2]) - int(comp_int[1])
#     comp_int.score = score
#     return comp_int


def comp_with_value(f):
    """
    adds 10 bp to the stop
    """
    score = int(f[2]) - int(f[1])
    return (f, score)


def gen(bed_comp):
    for i in bed_comp:
        score = int(i[2])-int(i[1])
        new_i = (i[0], i[1], i[2], ".", score) 
        
        yield new_i

def reorder(bed_comp_phases):
    for i in bed_comp_phases:        
        new_i = (i[0], i[1], i[2], i[5]) 
        
        yield new_i
                
# For each track merge feeding acts that are separated by less than 120 seconds (thus generating feeding bouts track)
# Calculates the complement of feeding bouts (intermeal intervals) and intersect them with day and experimental phases
# Dumping results into bed files
for tr, bed in bed_str.iteritems():
    bed_BedTools = bed.create_pybedtools()
    bed_merged_fn = bed_BedTools.merge(d=120, stream=True, c=(4,5,6,9), o=("distinct","sum","distinct","collapse")).saveas().fn
    
    pybed_intdata = intervals.IntData(bed_merged_fn, map_dict=mapping_bed.correspondence, header=False, fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])
    pybed_intdata_read = pybed_intdata.read(relative_coord=False)
        
    pybed_tr = pybed_intdata_read.convert(mode="bed", data_types=["food_sc", "food_fat"], dataTypes_actions="all", color_restrictions=data_type_col)
    
    ## Complement
    bed_merged_comp = pybedtools.BedTool(bed_merged_fn).complement(g=chr_file)
    bed_merged_comp_to_map = pybedtools.BedTool(gen(bed_merged_comp))
    
#     print bed_merged_comp_to_map

#     hab_light_intermeals_bed = bed_merged_comp.intersect(hab_bed).intersect(light_bed)#.saveas('tr_' + '_'.join(tr) + "_compl_hab_light.bed")
#     hab_dark_intermeals_bed = bed_merged_comp.intersect(hab_bed).intersect(dark_bed)#.saveas('tr_' + '_'.join(tr) + "_compl_hab_dark.bed")
#     dev_light_intermeals_bed = bed_merged_comp.intersect(dev_bed).intersect(light_bed)#.saveas('tr_' + '_'.join(tr) + "_compl_dev_light.bed")
#     dev_dark_intermeals_bed = bed_merged_comp.intersect(dev_bed).intersect(dark_bed)#.saveas('tr_' + '_'.join(tr) + "_compl_dev_dark.bed")
#     
#     light_intermeals_bed = bed_merged_comp_to_map.map(light_bed, c=5, o="mean", null=0)
    all_phases_tr = all_phases_bed.map(bed_merged_comp_to_map, c=5, o="mean", null=0)
    pybedtools.BedTool(reorder(all_phases_tr)).saveas('tr_' + '_'.join(tr) + "_compl_phases.bedGraph")
         
        
#     .saveas('tr_' + '_'.join(tr) + "_compl_phases.bed")
#     all_phases_bed.map(bed_merged_comp_to_map, c=5, o="mean", null=0).saveas('tr_' + '_'.join(tr) + "_compl_phases.bed")
    
#     speed_means = motion_BedTools.map(speed_BedTools, c=5, o="mean", null=0)
    
    #.saveas('tr_' + '_'.join(tr) + "_compl_light.bed")
#     motion_BedTools.map(speed_BedTools, c=5, o="mean", null=0).saveas(out_dir + tag_file + ".mean.bed")
    
#     dark_intermeals_bed = bed_merged_comp_to_map.map(dark_bed, o="mean").saveas('tr_' + '_'.join(tr) + "_compl_dark.bed")
    
    
    
    
    
    
    
    
#     light_intermeals_bed = bed_merged_comp.intersect(light_bed)#.saveas('tr_' + '_'.join(tr) + "_compl_light.bed")
#     dark_intermeals_bed = bed_merged_comp.intersect(dark_bed)#.saveas('tr_' + '_'.join(tr) + "_compl_dark.bed")
#     
#     print light_intermeals_bed
# #     print hab_light_intermeals_bed
#     pybedtools.BedTool(gen(light_intermeals_bed)).saveas('tr_' + '_'.join(tr) +'_light_intermeals.bed')
#     pybedtools.BedTool(gen(dark_intermeals_bed)).saveas('tr_' + '_'.join(tr) +'_dark_intermeals.bed')

    
    
#     bed_full_length.map(phenotypic_feature_bt, c=5, o="mean", null=0).saveas (tag_file + ".mean_file.bed")