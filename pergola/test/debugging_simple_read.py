#!/usr/bin/env python

from pergola import mapping
from pergola import intervals
from pergola import parsers

mapping_info = mapping.MappingInfo("/Users/jespinosa/git/pergola/sample_data/feeding_behavior/b2g.txt")
 
mapping_info.write()
 
# load the data into an IntData object that will store the sequence of events
int_data = intervals.IntData("/Users/jespinosa/git/pergola/sample_data/feeding_behavior/feedingBehavior_HF_mice.csv", map_dict=mapping_info.correspondence, delimiter="\t")
 
print (int_data.data[:12])
print (int_data.fieldsB)
print (int_data.fieldsG_dict)
# print (int_data.fieldsG_dict.keys())
print (int_data.dataTypes)
print (int_data.tracks)
int_data.read(relative_coord=True)

#electro for single time point validation

mapping_info_e = mapping.MappingInfo("/Users/jespinosa/git/pergola/pergola/test/electrophysiology/e2p.txt")
mapping_info_e.write()

int_data_e = intervals.IntData("/Users/jespinosa/git/pergola/pergola/test/electrophysiology/electroTest_2f.txt", map_dict=mapping_info_e.correspondence, delimiter="\t")
 
 
 
print (int_data_e.data[:12])
print (int_data_e.fieldsB)
print (int_data_e.fieldsG_dict)
# print (int_data.fieldsG_dict.keys())
print (int_data_e.dataTypes)
print (int_data_e.tracks)
int_data_e.read(multiply_t=1000, relative_coord=True)



