#!/usr/bin/env python

################################################################
### Jose A Espinosa. CSN/CB-CRG Group. Feb 2015              ###
################################################################
### Script creating pybedtools objects directly from pergola ###
################################################################

import pybedtools

bedG=pybedtools.BedTool("/Users/jespinosa/git/pergola/test/shortPos.bedGraph")
print bedG

##############
# Here I try to create a BedTool Object using new_create_pybedtools
from pergola import mapping
from pergola import intervals

mapping_data = mapping.MappingInfo("/Users/jespinosa/git/pergola/sample_data/feeding_behavior/b2g.txt")

int_data = intervals.IntData("/Users/jespinosa/git/pergola/sample_data/feeding_behavior/feedingBehavior_HF_mice.csv", map_dict=mapping_data.correspondence)

data_read = int_data.read(relative_coord=True)

#####################
###### NUEVO



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

for i in bedTools_tr1: print(i)

