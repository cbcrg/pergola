#  Copyright (c) 2014-2018, Centre for Genomic Regulation (CRG).
#  Copyright (c) 2014-2018, Jose Espinosa-Carrasco and the respective authors.
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
from scripts.pergola_rules import pergola_rules
from pergola.jaaba_parsers import jaaba_scores_to_csv, jaaba_scores_to_intData
from os      import path, chdir, mkdir
from sys     import stderr
from shutil  import rmtree

# Getting the path to test files
PATH = path.abspath(path.split(path.realpath(__file__))[0])
print path.split(path.realpath(__file__))
PATH_DATA = path.join(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))), "sample_data", '')

TEST = path.join(PATH, "uni_test", '' )

class TestTutorial(unittest.TestCase):
    """
    Testing that everything in the tutorial run smoothly        
    """ 
     
    def setUp(self):
        if not path.exists(TEST):
            mkdir(TEST)
        chdir(TEST)
        
    def test_01_correspondence_info (self):
        """
        Testing that ontology file is correctly read
        """
#         print >> stderr,"====================== test 1"
        global mappings_tutorial, exp2, exp3, exp4
        # mappings_tutorial = mapping.MappingInfo(PATH + "/feeding/f2p.txt")
        mappings_tutorial = mapping.MappingInfo(PATH_DATA + "/feeding_behavior/b2p.txt")

        msg_mappings = "Equivalences set in tutorial mapping file are not correct."
        self.assertEqual(mappings_tutorial.correspondence['EndT'], 'end', msg_mappings)
        
    def test_02_read_int_data(self):
        """
        Testing the creation of intData object using tutorial data
        """ 
#         print >> stderr,"====================== test 2"
        global data_read
        
        # Min value from tutorial file
        min = 1335985200
        max = 1337799586
        msg_int_data_min= "Min value does not correspond to tutorial files."
        msg_int_data_max= "Max value does not correspond to tutorial files."

        # int_data_tutorial = intervals.IntData(PATH + "/feeding/feeding_behavior_HF_mice.csv", map_dict=mappings_tutorial.correspondence)
        int_data_tutorial = intervals.IntData(PATH_DATA + "/feeding_behavior/feeding_behavior_HF_mice.csv", map_dict=mappings_tutorial.correspondence)

        self.assertEqual(int_data_tutorial.min, min, msg_int_data_min) 
        self.assertEqual(int_data_tutorial.max, max, msg_int_data_max)

        data_read = int_data_tutorial.read(relative_coord='False', intervals=False, multiply_t=1)

    def test_03_bed(self):
        """
        Testing the creation of bed files
        """ 
#         print >> stderr,"====================== test 3"
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
#         print >> stderr,"====================== test 4"
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

    def test_05_bedGraph_noBinning(self):
        """
        Testing the creation of bedGraph files without window binning
        """
#         print >> stderr,"====================== test 5"
        write_format='bedGraph'

        bed_str =  data_read.convert(mode=write_format, window=False)

        bedSingle_1_food_fat = bed_str[('2','food_fat')]
        bedSingle_1_food_sc = bed_str[('1','food_sc')]
        bedSingle_1_water = bed_str[('3','water')]

        # track containing minimum time value in order to check relative_coord
        bedSingle_16_food_sc = bed_str[('16','food_sc')]

        bedSingle_1_food_fat.save_track(track_line=True)
        bedSingle_1_food_sc.save_track(track_line=True)
        bedSingle_1_water.save_track(track_line=True)

        bedSingle_16_food_sc.save_track(track_line=True)

    def test_06_bedGraph_Binning(self):
        """
        Testing the creation of bedGraph files without window binning
        """
#         print >> stderr,"====================== test 6"

        write_format='bedGraph'

        bed_str =  data_read.convert(mode=write_format, window=300)

        bedSingle_1_food_fat = bed_str[('2','food_fat')]
        bedSingle_1_food_sc = bed_str[('1','food_sc')]
        bedSingle_1_water = bed_str[('3','water')]

        # track containing minimum time value in order to check relative_coord
        bedSingle_16_food_sc = bed_str[('16','food_sc')]

        bedSingle_1_food_fat.save_track(track_line=True)
        bedSingle_1_food_sc.save_track(track_line=True)
        bedSingle_1_water.save_track(track_line=True)

        bedSingle_16_food_sc.save_track(track_line=True)

    def test_07_pergola_rules(self):
        """
        Testing pergola_rules script
        """
#         print >> stderr,"====================== test 7"

        data_in = PATH_DATA + "/feeding_behavior/feeding_behavior_HF_mice.csv"
        map_in = PATH_DATA + "/feeding_behavior/b2p.txt"
        pergola_rules(path=data_in, map_file_path=map_in, )

    def test_08_jaaba_to_pergola(self):
        """
        Testing jaaba_to_pergola script
        """
#         print >> stderr,"====================== test 8"

        data_in = PATH_DATA + "/jaaba_example/scores_chase_ctrl_pBDPGAL4.mat"
        jaaba_scores_to_csv(input_file=data_in, path_w=TEST, name_file="file_out", norm=True, data_type="chase")
        map_j = PATH_DATA + "/jaaba_example/jaaba2pergola.txt"
        int_data_j = jaaba_scores_to_intData(input_file=data_in, map_jaaba=map_j, name_file="JAABA_scores", delimiter="\t", norm=True, data_type="a")
        # print >> stderr, "Min value jaaba====== %d" % int_data_j.min

    def test_only_one_time_point(self):
        """
        Testing if files with just one coordinate for time are read correctly
        """
#         print >> stderr,"====================== test 9"

        global int_data_electro, mappings_electro
        msg_mappings = "Equivalences set in electrophysiology mapping file are not correct."

        mappings_electro = mapping.MappingInfo(PATH_DATA + "/electrophysiology/e2p.txt")
        keys_electro = ['track', 'data_types', 'data_value', 'start']
        fields = mappings_electro.correspondence.values()

        self.assertEqual(keys_electro, fields, msg_mappings)

        min = 0
        max = 0.3
        msg_int_data_min= "Min value in electrophysiology data intData not correctly read."
        msg_int_data_max= "Max value in electrophysiology data intData not correctly read."

        int_data_electro = intervals.IntData(PATH_DATA + "/electrophysiology/electro_test_2f.txt", map_dict=mappings_electro.correspondence)

        self.assertEqual(int_data_electro.min, min, msg_int_data_min)
        self.assertEqual(int_data_electro.max, max, msg_int_data_max)

    def test_track_electro(self):
#         print >> stderr,"====================== test 10"

        global tracks_data_electro
        msg_track_electro = "Track electrophysiology not correctly read"

        max = 302
        tracks_data_electro = int_data_electro.read(multiply_t=1000, intervals=True)
        self.assertEqual(tracks_data_electro.max, max, msg_track_electro)

        first_item = (0.0, '-30.98', 'a', '1', 9.0)
        first_item_read = tracks_data_electro.data[0]
        self.assertEqual(tracks_data_electro.max, max, msg_track_electro)
        self.assertEqual(first_item_read, first_item, msg_track_electro)

    def test_read_int_data_from_xls(self):
        """
        Testing the creation of intData object using data in xls format
        """
        # print >> stderr,"====================== test 11"

        # Min value from tutorial file
        min = 1335985200
        max = 1337766069
        msg_int_data_min = "Min value does not correspond to tutorial files."
        msg_int_data_max = "Max value does not correspond to tutorial files."

        int_data_tutorial = intervals.IntData(PATH_DATA + "/feeding_behavior/feeding_behavior_HF_mice.xlsx",
                                              map_dict=mappings_tutorial.correspondence)

        self.assertEqual(int_data_tutorial.min, min, msg_int_data_min)
        self.assertEqual(int_data_tutorial.max, max, msg_int_data_max)

        data_read = int_data_tutorial.read(relative_coord='False', intervals=False, multiply_t=1)

    def tearDown(self):
        rmtree (TEST)
        
if __name__ == '__main__':
    unittest.main()