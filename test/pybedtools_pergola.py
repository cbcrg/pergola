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
type (bed_tr1_food_sc)
# for i in bed_tr1_food_sc: print i

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

# Subseting of bed file for testing meal merging
c = pybedtools.BedTool(bedTools_tr2 [1:5])
type (c)
for i in c: print(i)

############# Working command
###### c_values = c_short.merge(d=100, stream=True, c=5, o="sum")
# c_short = pybedtools.BedTool(bedTools_tr2 [1:5])
# c_values_ok = c_short.merge(d=100, stream=True, c=5, o="sum")
# for i in c_values_ok: print(i)

################################
# Meal modelling 120 s
# mergeBed -i ${track} -d 120 -S + -c 4,5,6,9 -o distinct,sum,distinct,collapse -delim ";" > ${filename}_joined.bed
# mergeBed -i tr_1_dt_food_sc.bed -d 120 -c 5 -o sum  > tr_merge.bed

# bed short for testing
b_short = pybedtools.BedTool(bedTools_tr2 [1:5])

# si lo voy a leer tambien con pergola quiza no me haria falta que tuviera todos los campos
# lo podria leer solo con los intervalos y los valores 
# Algo asi
# b_values_test = b_short.merge(d=100, stream=True, c=(5), o=("sum"))

# collapse (i.e., print a delimited list (duplicates allowed))
# distinct the same no duplicates allowed
# c_values_test = c_short.merge(d=100, stream=True, c=(4,5), o=("distinct", "sum"))
b_values_test = b_short.merge(d=100, stream=True, c=(4,5,6,9), o=("distinct","sum","distinct","collapse"))

type (b_values_test)
for i in b_values_test: print(i)

## Merge implemented for example in paper
# Tips in https://pythonhosted.org/pybedtools/3-brief-examples.html
# result = g.filter(featuretype_filter, featuretype).saveas()
b_short = pybedtools.BedTool(bedTools_tr2 [1:5])
merged_bed_fn = b_short.merge(d=120, stream=True, c=(4,5,6,9), o=("distinct","sum","distinct","collapse")).saveas().fn

print (merged_bed_fn)

mapping_bed = mapping.MappingInfo("/Users/jespinosa/git/pergola/test/pybed2perg.txt")

pybed_intdata = intervals.IntData(merged_bed_fn, map_dict=mapping_bed.correspondence, header=False, fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])

pybed_intdata_read = pybed_intdata.read(relative_coord=False)
data_type_col = {'food_fat':'blue'}
pybed_tr = pybed_intdata_read.convert(mode="bed", data_types=["food_sc", "food_fat"], dataTypes_actions="all", color_restrictions=data_type_col)
print (pybed_tr)
py_bed_tr1 = pybed_tr [('chr1', 'food_fat')]

py_bed_tr1.save_track(path="/Users/jespinosa/git/pergola/test/", name_file="py_bed_tr")

for i in py_bed_tr1: print (i)



# self.save_track (path = path_bed, name_file=name_bed)

# bed_tr1_food_sc = bed_str[('1', 'food_sc')]





# for i in pybed_intdata_read.data: print (i)
# print (data_read.data)

# print (pybed_intdata_read)

# data_type_col = {'food_sc': 'orange', 'food_fat':'blue'}

# bed_str = pybed_intdata_read.convert(mode="bed", data_types=["food_sc", "food_fat"], dataTypes_actions="all", color_restrictions=data_type_col)
# print (bed_str)

# # Intersect example
# # c = bedTools_tr2.intersect(bedTools_tr1) 
# # print (c)