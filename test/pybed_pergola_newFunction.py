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

mapping_data = mapping.MappingInfo("/Users/jespinosa/git/pergola/sample_data/feeding_behavior/b2g.txt")

int_data = intervals.IntData("/Users/jespinosa/git/pergola/sample_data/feeding_behavior/feedingBehavior_HF_mice.csv", map_dict=mapping_data.correspondence)

data_read = int_data.read(relative_coord=True)

#####################
###### NUEVO
# Generate a chr.size file in order to calculate complement of merged meals
chr_file_n = "chrom"
mapping.write_chr_sizes (data_read, path_w=w_dir, file_n=chr_file_n)

chr_file = w_dir + chr_file_n + ".sizes"
print "*******************", chr_file

data_type_col = {'food_sc': 'orange', 'food_fat':'blue'}

bed_str = data_read.convert(mode="bed", data_types=["food_sc", "food_fat"], dataTypes_actions="all", color_restrictions=data_type_col)
# print bed_str
bed_tr1_food_sc = bed_str[('1', 'food_sc')]

type (bed_tr1_food_sc)


# fff = bed_tr1_food_sc.create_pybedtools()
# for i in fff: print i


# for i in  bed_tr1_food_sc: print i

bedTools_tr1 = bed_tr1_food_sc.new_create_pybedtools()
type(bedTools_tr1)

# for i in bedTools_tr1: print(i)

dict_bed_merged = {}

#############
# For each track merge meals
for tr, bed in bed_str.iteritems():
# for bed in bed_str:
    bed_BedTools = bed.new_create_pybedtools()
    bed_merged = bed_BedTools.merge(d=120, stream=True, c=(4,5,6,9), o=("distinct","sum","distinct","collapse"))
    # dict_bed_merged[tr] = bed_merged
    # print bed_merged
    # '.join(tup)
    # bed_merged.saveas(''.join(tr) + "upstream_regions.bed")
    ## COMPLEMENT
    bed_merged_comp = bed_merged.complement(g=chr_file)
    print bed_merged_comp.head(5) 
    # dict_bed_merged[tr] = bed_merged