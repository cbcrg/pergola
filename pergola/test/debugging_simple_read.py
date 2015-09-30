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
print "debugging_simple_read---- min value in int_data_feeding ------------------------", int_data.min
print "debugging_simple_read---- max value in int_data_feeding ------------------------", int_data.max
track_data = int_data.read(relative_coord=True)
print "track object files are============+++++++++++++++++++", track_data.fields
track_data.convert(mode="bed")

#electro for single time point validation

mapping_info_e = mapping.MappingInfo("/Users/jespinosa/git/pergola/pergola/test/electrophysiology/e2p.txt")
mapping_info_e.write()

print ("debugging_simple_read correspondence.........................................................",mapping_info_e.correspondence.values())

int_data_e = intervals.IntData("/Users/jespinosa/git/pergola/pergola/test/electrophysiology/electroTest_2f.txt", map_dict=mapping_info_e.correspondence, delimiter="\t")
int_data_e_int = intervals.IntData("/Users/jespinosa/git/pergola/pergola/test/electrophysiology/electroTest_2f.txt", map_dict=mapping_info_e.correspondence, delimiter="\t")
  
print ("debugging_simple_read keys fieldsG_dict................",int_data_e.fieldsG_dict.keys())
print ("debugging_simple_read****************************************", int_data_e)
print ("debugging_simple_read", int_data_e.data[:12])
print ("debugging_simple_read",int_data_e.fieldsB)
print ("debugging_simple_read",int_data_e.fieldsG_dict)
print ("min in electrophysiology================================", int_data_e.min)
print ("min in electrophysiology================================", int_data_e.max)
# print (int_data.fieldsG_dict.keys())
print ("debugging_simple_read",int_data_e.dataTypes)
print ("debugging_simple_read",int_data_e.tracks)
# int_data_e.read(multiply_t=1000, relative_coord=True)# este tiene que petar no endChrom
print ("debugging_simple_read",int_data_e_int.data)
tracks_data_e = int_data_e_int.read(multiply_t=1000, intervals=True)
print "debugging_simple_read", tracks_data_e
print "debugging_simple_read", int_data_e_int.range_values
print "debugging_simple_read", tracks_data_e.range_values
print "debugging_simple_read", tracks_data_e.max
print "debugging_simple_read", tracks_data_e.data[0]




