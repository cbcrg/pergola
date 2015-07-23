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
        global exp1, exp2, exp3, exp4
        exp_1 = mapping.OntologyInfo(PATH + "/feeding/tutorial/b2g.txt")
        
        self.assertEqual(exp_1.correspondence['EndT'], 'chromEnd')

    
if __name__ == '__main__':
    unittest.main()