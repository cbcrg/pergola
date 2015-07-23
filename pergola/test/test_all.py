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
        
    def test_ontology_info (self):
        """
        Testing that ontology file is correctly read
        """
        global correspondence_tutorial, exp2, exp3, exp4
        correspondence_tutorial = mapping.OntologyInfo(PATH + "/feeding/tutorial/b2g.txt")
        
        self.assertEqual(correspondence_tutorial.correspondence['EndT'], 'chromEnd')

    def test_read_int_data(self):
        """
        Testing the creation of intData object using tutorial data
        """ 
        global int_data_tutorial
        int_data_tutorial = intervals.IntData(PATH + "/feeding/tutorial/feedingBehavior_HF_mice.csv", ontology_dict=correspondence_tutorial.correspondence)
        
if __name__ == '__main__':
    unittest.main()