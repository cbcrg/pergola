#  Copyright (c) 2014-2016, Centre for Genomic Regulation (CRG).
#  Copyright (c) 2014-2016, Jose Espinosa-Carrasco and the respective authors.
#
#  This file is part of Pergola.
#
#  Pergola is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pergola is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Pergola.  If not, see <http://www.gnu.org/licenses/>.

"""
unittest for pergola functions

"""

import unittest
from pergola import mapping
from pergola import intervals
from os      import path
from sys     import stderr

# Getting the path to test files
PATH = path.abspath(path.split(path.realpath(__file__))[0])

class TestTutorial(unittest.TestCase):
    """
    Testing that everything in the tutorial run smoothly        
    """ 
        
    def test_01_correspondence_info (self):
        """
        Testing that ontology file is correctly read
        """
        global mappings_tutorial, exp2, exp3, exp4
        mappings_tutorial = mapping.MappingInfo(PATH + "/feeding/b2g.txt")
        
        msg_mappings = "Equivalences set in tutorial mapping file are not correct."
        self.assertEqual(mappings_tutorial.correspondence['EndT'], 'end', msg_mappings)
        
    def test_02_read_int_data(self):
        """
        Testing the creation of intData object using tutorial data
        """ 
        global data_read
        
        # Min value from tutorial file
        min = 1335985200
        max = 1337766069
        msg_int_data_min= "Min value does not correspond to tutorial files."
        msg_int_data_max= "Max value does not correspond to tutorial files."
        
        int_data_tutorial = intervals.IntData(PATH + "/feeding/feeding_behavior_HF_mice.csv", map_dict=mappings_tutorial.correspondence)
        
        self.assertEqual(int_data_tutorial.min, min, msg_int_data_min) 
        self.assertEqual(int_data_tutorial.max, max, msg_int_data_max)
        
        data_read = int_data_tutorial.read(relative_coord='False', intervals=False, multiply_t=1)
        
    def test_03_bed(self):
        """
        Testing the creation of bed files
        """ 
        write_format='bed'
         
#         data_read = int_data_tutorial.read(relative_coord='False', intervals=False, multiply_t=1)
        bed_str =  data_read.convert(mode=write_format)
          
#         for key in bed_str:
#             print key
        bedSingle_1_food_fat = bed_str[('2','food_fat')]
        bedSingle_1_food_sc = bed_str[('1','food_sc')]
        bedSingle_1_water = bed_str[('3','water')]
         
        # track containing minimum time value in order to check relative_coord   
        bedSingle_16_food_sc = bed_str[('16','food_sc')]
         
        bedSingle_1_food_fat.save_track(track_line=True, bed_label=True)                
        bedSingle_1_food_sc.save_track(track_line=True, bed_label=True)   
        bedSingle_1_water.save_track(track_line=True, bed_label=True)
         
        bedSingle_16_food_sc.save_track(track_line=True, bed_label=True)
             
    def test_04_gff(self):
        """
        Testing the creation of gff files
        """ 
        write_format='gff'
        
        
        bed_str =  data_read.convert(mode=write_format)
         
#         for key in bed_str:
#             print key
        bedSingle_1_food_fat = bed_str[('2','food_fat')]
        bedSingle_1_food_sc = bed_str[('1','food_sc')]
        bedSingle_1_water = bed_str[('3','water')]
        
        # track containing minimum time value in order to check relative_coord   
        bedSingle_16_food_sc = bed_str[('16','food_sc')]
        
        bedSingle_1_food_fat.save_track(track_line=True, bed_label=True)                
        bedSingle_1_food_sc.save_track(track_line=True, bed_label=True)   
        bedSingle_1_water.save_track(track_line=True, bed_label=True)
        
        bedSingle_16_food_sc.save_track(track_line=True, bed_label=True)    
            
    def test_only_one_time_point(self):
        """
        Testing if files with just one coordinate for time are read correctly
        """ 
        global int_data_electro, mappings_electro 
        msg_mappings = "Equivalences set in electrophysiology mapping file are not correct."
        
        mappings_electro = mapping.MappingInfo(PATH + "/electrophysiology/e2p.txt")
        keys_electro = ['track', 'data_types', 'data_value', 'start']        
        fields = mappings_electro.correspondence.values()
        
        self.assertEqual(keys_electro, fields, msg_mappings)
        
        min = 0
        max = 0.3
        msg_int_data_min= "Min value in electrophysiology data intData not correctly read."
        msg_int_data_max= "Max value in electrophysiology data intData not correctly read."
        
        int_data_electro = intervals.IntData(PATH + "/electrophysiology/electroTest_2f.txt", map_dict=mappings_electro.correspondence)
        
        self.assertEqual(int_data_electro.min, min, msg_int_data_min) 
        self.assertEqual(int_data_electro.max, max, msg_int_data_max) 
        
    def test_track_electro(self):
        global tracks_data_electro
        msg_track_electro = "Track electrophysiology not correctly read"
        
        max = 300
        tracks_data_electro = int_data_electro.read(multiply_t=1000, intervals=True)
        self.assertEqual(tracks_data_electro.max, max, msg_track_electro)
        
        print >> stderr, "Test 4................." #del  
        
        first_item = (0.0, '-30.98', 'a', '1', 9.0) 
        first_item_read = tracks_data_electro.data[0]
        self.assertEqual(tracks_data_electro.max, max, msg_track_electro)
        self.assertEqual(first_item_read, first_item, msg_track_electro) 

# mapping_info_e = mapping.MappingInfo("/Users/jespinosa/git/pergola/pergola/test/electrophysiology/e2p.txt")
# mapping_info_e.write()
#  
# int_data_e = intervals.IntData("/Users/jespinosa/git/pergola/pergola/test/electrophysiology/electroTest_2f.txt", map_dict=mapping_info_e.correspondence, delimiter="\t")
# int_data_e_int = intervals.IntData("/Users/jespinosa/git/pergola/pergola/test/electrophysiology/electroTest_2f.txt", map_dict=mapping_info_e.correspondence, delimiter="\t")
#   
#   
# print ("debugging_simple_read", int_data_e.data[:12])
# print ("debugging_simple_read",int_data_e.fieldsB)
# print ("debugging_simple_read",int_data_e.fieldsG_dict)
# # print (int_data.fieldsG_dict.keys())
# print ("debugging_simple_read",int_data_e.dataTypes)
# print ("debugging_simple_read",int_data_e.tracks)
# # int_data_e.read(multiply_t=1000, relative_coord=True)# este tiene que petar no endChrom
# print ("debugging_simple_read",int_data_e_int.data)
# tracks_data_e = int_data_e_int.read(multiply_t=1000, intervals=True)
# print "debugging_simple_read", tracks_data_e
        
if __name__ == '__main__':
    unittest.main()