"""

unittest for pergola functions

"""

import unittest
from pergola import mapping
from pergola import intervals
from os import path

# Getting the path to test files
PATH = path.abspath(path.split(path.realpath(__file__))[0])

class TestTutorial(unittest.TestCase):
    """
    Testing that everything in the tutorial run smoothly        
    """ 
        
    def test_correspondence_info (self):
        """
        Testing that ontology file is correctly read
        """
        global mappings_tutorial, exp2, exp3, exp4
        mappings_tutorial = mapping.MappingInfo(PATH + "/feeding/tutorial/b2g.txt")
        
        msg_mappings = "Equivalences set in tutorial mapping file are not correct."
        self.assertEqual(mappings_tutorial.correspondence['EndT'], 'chromEnd', msg_mappings)
        
    def test_read_int_data(self):
        """
        Testing the creation of intData object using tutorial data
        """ 
        global int_data_tutorial
        
        # Min value from tutorial file
        min = 1335985200
        max = 1337766069
        msg_int_data_min= "Min value does not correspond to tutorial files."
        msg_int_data_max= "Max value does not correspond to tutorial files."
        
        int_data_tutorial = intervals.IntData(PATH + "/feeding/tutorial/feedingBehavior_HF_mice.csv", map_dict=mappings_tutorial.correspondence)
        self.assertEqual(int_data_tutorial.min, min, msg_int_data_min) 
        self.assertEqual(int_data_tutorial.max, max, msg_int_data_max) 
     
    def test_only_one_time_point(self):
        """
        Testing if files with just one coordinate for time are read correctly
        """ 
        global int_data_electro, mappings_electro 
        msg_mappings = "Equivalences set in electrophysiology mapping file are not correct."
        
        mappings_electro = mapping.MappingInfo(PATH + "/electrophysiology/e2p.txt")
        keys_electro = ['track', 'dataTypes', 'dataValue', 'chromStart']        
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