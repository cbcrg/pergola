#!/usr/bin/env python

################################################################
### Jose A Espinosa. CSN/CB-CRG Group. Jan 2016              ###
################################################################
###    ###
###   ###
###   ###
###                    ###
###    ###
###                           ###
################################################################

from pergola import mapping, intervals, tracks
from os import path, getcwd

base_dir = path.dirname(getcwd())
out_dir = base_dir + "/test/"

mapping_data = mapping.MappingInfo(base_dir + "/sample_data/feeding_behavior/b2g.txt")

int_data = intervals.IntData(base_dir + "/sample_data/feeding_behavior/feedingBehavior_HF_mice.csv", map_dict=mapping_data.correspondence)

# Dictionary to set colors of each type of food
data_type_col = {'food_sc': 'orange', 'food_fat':'blue'}

data_read = int_data.read(relative_coord=True)

# for i in data_read.data: print i

data_read.data_types
data_read.fields

# bed_str = data_read.convert(mode="bed")
# bedGraph_str = data_read.convert(mode="bedGraph")
gff_str = data_read.convert(mode="gff", data_types=["food_sc", "food_fat"], data_types_actions="all", color_restrictions=data_type_col)

print gff_str

tr_1_gff = gff_str[('1', 'food_sc')]
tr_1_gff_BedTools = tr_1_gff.create_pybedtools()

for l in tr_1_gff_BedTools: print l

tr_1_gff.save_track()


