#!/usr/bin/env python

################################################################
### Jose A Espinosa. CSN/CB-CRG Group. Feb 2015              ###
################################################################
### Script creating pybedtools objects directly from pergola ###
################################################################

import pybedtools

bedG=pybedtools.BedTool("/Users/jespinosa/git/pergola/test/shortPos.bedGraph")
# print bedG

w_dir = "/Users/jespinosa/git/pergola/test/"

##############
# Here I try to create a BedTool Object using new_create_pybedtools
from pergola import mapping
from pergola import intervals
# from itertools import tee
mapping_data = mapping.MappingInfo("/Users/jespinosa/git/pergola/sample_data/feeding_behavior/b2g.txt")

int_data = intervals.IntData("/Users/jespinosa/git/pergola/sample_data/feeding_behavior/feedingBehavior_HF_mice.csv", map_dict=mapping_data.correspondence)

data_read = int_data.read(relative_coord=True)

###################
# Write phases file 
# phases_light.bed
# phases_dark.bed

# Write phases file
mapping.write_cytoband(int_data, end=data_read.max)

light_ph_f = w_dir + "phases_light.bed"
dark_ph_f = w_dir + "phases_dark.bed"
light_bed = pybedtools.BedTool(light_ph_f)
dark_bed = pybedtools.BedTool(dark_ph_f)

#####################
###### NUEVO
# Generate a chr.size file in order to calculate complement of merged meals
chr_file_n = "chrom"
mapping.write_chr_sizes (data_read, path_w=w_dir, file_n=chr_file_n)

chr_file = w_dir + chr_file_n + ".sizes"
print "*******************", chr_file

# Dictionary of colors
data_type_col = {'food_sc': 'orange', 'food_fat':'blue'}

bed_str = data_read.convert(mode="bed", data_types=["food_sc", "food_fat"], dataTypes_actions="all", color_restrictions=data_type_col)
# print bed_str
# bed_tr1_food_sc = bed_str[('1', 'food_sc')]

# type (bed_tr1_food_sc)


# fff = bed_tr1_food_sc.create_pybedtools()
# for i in fff: print i


# for i in  bed_tr1_food_sc: print i

# bedTools_tr1 = bed_tr1_food_sc.new_create_pybedtools()
# type(bedTools_tr1)

# for i in bedTools_tr1: print(i)

dict_bed_merged = {}
mapping_bed = mapping.MappingInfo("/Users/jespinosa/git/pergola/test/pybed2perg.txt")

# Habituation phase
hab_bed = pybedtools.BedTool("/Users/jespinosa/phecomp/20140807_pergola/bedtools_ex/intermeal_duration/data/exp_phases_hab.bed")
# Development phase
dev_bed = pybedtools.BedTool("/Users/jespinosa/phecomp/20140807_pergola/bedtools_ex/intermeal_duration/data/exp_phases_dev.bed")
# print (dev_bed)

#############
# For each track merge meals
for tr, bed in bed_str.iteritems():
# for bed in bed_str:
    bed_BedTools = bed.new_create_pybedtools()
    bed_merged_fn = bed_BedTools.merge(d=120, stream=True, c=(4,5,6,9), o=("distinct","sum","distinct","collapse")).saveas().fn
    # bed_BedTools.merge(d=120, stream=True, c=(4,5,6,9), o=("distinct","sum","distinct","collapse")).saveas(''.join(tr) + "upstream_regions.bed")

    # dict_bed_merged[tr] = bed_merged
    # print bed_merged
    # '.join(tup)
    # print ('tr_' + '_'.join(tr) + '_merged.bed')
    print ('Processing track *************** '+'tr_' + '_'.join(tr))
    # print ('*******',''.join(tr) + "upstream_regions.bed")
    # print ('*******', bed_merged_fn)
    pybed_intdata = intervals.IntData(bed_merged_fn, map_dict=mapping_bed.correspondence, header=False, fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])
    pybed_intdata_read = pybed_intdata.read(relative_coord=False)
        
    # data_type_col = {'food_fat':'blue'}
    pybed_tr = pybed_intdata_read.convert(mode="bed", data_types=["food_sc", "food_fat"], dataTypes_actions="all", color_restrictions=data_type_col)
    
    ## COMPLEMENT
    bed_merged_comp = pybedtools.BedTool(bed_merged_fn).complement(g=chr_file)
    # bed_merged_comp.saveas('tr_' + '_'.join(tr) + 'comp.bed')
    # print 'tr_' + '_'.join(tr) + 'comp.bed'
    
    ## Intersection with light, dark and experimental phases
    # light_bed, light_bed2 = tee(light_bed)
    light_intermeals_bed = bed_merged_comp.intersect(light_bed).intersect(dev_bed)
    # print light_intermeals_bed.head(5)
    
    # print light_intermeals_bed.head(5)
    
    # to relative coordinates
    # light_bed.saveas('bed_light.bed')
    
    # print (":::::::::::", tr)
    # dict_bed_merged[tr] = bed_merged_comp
    
    # bed_merged.saveas(''.join(tr) + "upstream_regions.bed")
    ## COMPLEMENT
    # bed_merged_comp = bed_merged.complement(g=chr_file)
    # print bed_merged_comp.head(5) 
    # dict_bed_merged[tr] = bed_merged