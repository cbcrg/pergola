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
        global mappings_electro 
        mappings_electro = mapping.MappingInfo(PATH + "/electrophysiology/e2p.txt")
        int_data_electro = intervals.IntData(PATH + "/electrophysiology/electroTest_2f.txt", map_dict=mappings_electro.correspondence)
#         self.assertEqual(int_data_tutorial.min, min, msg_int_data_min) 
        
        
            
if __name__ == '__main__':
    unittest.main()