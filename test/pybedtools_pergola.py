#!/usr/bin/env python

################################################################
### Jose A Espinosa. CSN/CB-CRG Group. Feb 2015              ###
################################################################
### Script creating pybedtools objects directly from pergola ###
################################################################

import pybedtools
# pybedtools.helpers.set_bedtools_path('/Users/jespinosa/software/bedTools/bedtools2/bin/')

import sys

# os.chdir(path)

my_path_to_modules = "/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/"
sys.path.append(my_path_to_modules)

from pergola import mapping
from pergola import intervals

mapping_data = mapping.MappingInfo("/Users/jespinosa/git/pergola/sample_data/feeding_behavior/b2g.txt")

int_data = intervals.IntData("/Users/jespinosa/git/pergola/sample_data/feeding_behavior/feedingBehavior_HF_mice.csv", map_dict=mapping_data.correspondence)

data_read = int_data.read(relative_coord=True)

data_type_col = {'food_sc': 'orange', 'food_fat':'blue'}

bed_str = data_read.convert(mode="bed", data_types=["food_sc", "food_fat"], dataTypes_actions="all", color_restrictions=data_type_col)

bed_tr1_food_sc = bed_str[('1', 'food_sc')]

# Esto es del propio codigo de bedtools
# If *from_string* is True, then you can pass a string that contains
# the contents of the BedTool you want to create.  This will treat all
# spaces as TABs and write to tempfile, treating whatever you pass as
# *fn* as the contents of the bed file.  This also strips empty lines.

# print (bed_tr1_food_sc)
bedTools_tr1 = bed_tr1_food_sc.create_pybedtools()
# print (bedTools_tr1)

bed_tr2_food_fat = bed_str[('2', 'food_fat')]

bedTools_tr2 = bed_tr2_food_fat.create_pybedtools()
# print (bedTools_tr2)

# pybedtools.helpers.set_bedtools_path("/Users/jespinosa/software/bedTools/bedtools2/bin/")

# Intersect example
# c = bedTools_tr2.intersect(bedTools_tr1) 
# print (c)

# Meal modelling 120 s
# mergeBed -i ${track} -d 120 -S + -c 4,5,6,9 -o distinct,sum,distinct,collapse -delim ";" > ${filename}_joined.bed
c_short = pybedtools.BedTool(bedTools_tr2 [1:5])
c = pybedtools.BedTool(bedTools_tr2 [1:5])
for i in c_short: print(i)
# for i in c: print(i)

c_values = c_short.merge(d=100, stream=True, column=4)
# c = c_short.merge(d=100, stream=True)

# for i in c: print(i)
for i in c_values: print(i)

# fn = BedTool(iter(fn)).saveas().fn

# a = pybedtools.BedTool(bed_tr1_food_sc, from_string=True)

# # print (a)

# bed_tr2_food_fat = bed_str[('2', 'food_fat')]
# bed_file_single.save_track(name_file = "files_data")

# # podria crear una funcion que hiciera un temporal dentro de bed
# # este metodo solo seria llamado desde el metodo
# # bed.create_pybedtools

# bed_file_single.
# f = NamedTemporaryFile(delete=False)

# b = pybedtools.BedTool(bed_tr2_food_fat, from_string=True)
# # print (b)
# # c = a[2:4]

# # intersecting
# c = a.intersect(b) 
# print (c)
# # 




