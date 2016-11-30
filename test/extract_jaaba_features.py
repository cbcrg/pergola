#!/usr/bin/env python

# from scipy.io  import loadmat
# from numpy     import hstack, ndenumerate#, mean, divide
# from os.path   import join, exists, abspath, split, realpath
# from pergola.mapping   import MappingInfo, check_path #del change
# from shutil    import copyfileobj
# from tempfile  import NamedTemporaryFile #del
# from pergola.intervals import IntData #del
from pergola  import parsers

# parsers.jaaba_features_to_intData(input_file='Users/jespinosa/JAABA_MAC_0.5.1/sampledata_v0.5/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/scores_chase.mat', 
#                             path_w='/Users/jespinosa/git/pergola/test', norm=True, data_type="chase")

# jaaba_features_to_intData(dir_perframe, map_jaaba,  delimiter="\t", feature="velmag", output="csv", path_w=""):
map_file_jaaba = "/Users/jespinosa/git/pergola/test/jaaba2pergola.txt"
 
parsers.extract_jaaba_features(dir_perframe='/Users/jespinosa/JAABA_MAC_0.5.1/sampledata_v0.5/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/perframe/', map_jaaba="",
                               delimiter="\t", feature="velmag", output="csv", path_w='/Users/jespinosa/git/pergola/test')

map_file_jaaba = "/Users/jespinosa/git/pergola/test/jaaba2pergola.txt"
# int_data_jaaba = parsers.jaaba_scores_to_intData(input_file = input_jaaba_file, map_jaaba = map_file_jaaba, norm=True, data_type="chase")

int_data_jaaba = parsers.extract_jaaba_features(dir_perframe='/Users/jespinosa/JAABA_MAC_0.5.1/sampledata_v0.5/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/perframe/', 
                                           feature="velmag", map_jaaba=map_file_jaaba, output="IntData")
# map_jaaba = map_file_jaaba,

print int_data_jaaba.min
print int_data_jaaba.max
print int_data_jaaba.tracks
# print int_data_jaaba.data

#     _csv_file_ext = ".csv" #del
#     name_file = feature 


# # HACER UN 
# input_file = '/Users/jespinosa/JAABA_MAC_0.5.1/sampledata_v0.5/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/perframe/absdtheta.mat'
# input_file
# 
# jaaba_feature = loadmat(input_file)
# 
# # class(start_times = jaaba_feature['data'])
# 
# len_f = jaaba_feature['data'][0][1].size
# id_worm = 1
# worm_jaaba_feature = hstack(jaaba_feature['data'][0][id_worm])
# 
# single_value_first = hstack(worm_jaaba_feature)[0]
# 
# print(single_value_first)
# 
# single_value_last = hstack(worm_jaaba_feature)[len_f-1]
# 
# print(single_value_last )
# 
# type(worm_jaaba_feature)
# 
# for v in enumerate(worm_jaaba_feature):
#     print v
#     print "a"


# def jaaba_features_to_intData(input_file, map_jaaba, name_file="JAABA_scores", delimiter="\t" feature="velmag"):

# def jaaba_features_to_intData(dir_perframe, map_jaaba=False,  delimiter="\t", feature="velmag", output="csv", path_w=""):
#     """   
#     Creates a csv file from feature mat files dumped by JAABA and in matlab format
#      
#     :param input_file: path to the JAABA file in matlab format
#     :param map_jaaba: path to the mapping files between JAABA data and pergola ontology 
#     :param "\t" delimiter: :py:func:`str` Character use to separate values of 
#         the same record in file (default "\t").
#     :param data_type: :py:func:`str` data type (feature) to extract e.g. velmag (speed of the center of rotation)
#         More features can be found in http://ctrax.sourceforge.net/bmat.html
#      
#     returns: IntData object
#     """
#              
#     dir_perframe = '/Users/jespinosa/JAABA_MAC_0.5.1/sampledata_v0.5/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/perframe/'
#     feature="velmag"    
#     input_path = join(dir_perframe, feature + ".mat")
#          
#     input_file = check_path(input_path)
#          
#     jaaba_feature = loadmat(input_file)
#      
#     len_f = jaaba_feature['data'][0][1].size
#     animal_n = jaaba_feature['data'][0].size
# # if track_action not in _tr_act_options:
# #         raise ValueError("Track_action \'%s\' not allowed. Possible values are %s"%(track_action,', '.join(['{}'.format(m) for m in _tr_act_options])))
#     output_option = ["csv", "IntData"]
#      
#     if output not in output_option:
#             raise ValueError("Option output \'%s\' not allowed. Possible values are %s"%(output_options, ', '.join(['{}'.format(m) for m in output_options])))
#      
#     temp = NamedTemporaryFile()
#     header = ["animal", "startTime", "endTime", "value", "dataType"]
#     temp.write(delimiter.join(header) + "\n")
#      
#     for id_animal, animal_jaaba_feature in enumerate (jaaba_feature['data'][0]):
#         animal_jaaba_feature= hstack(animal_jaaba_feature)
#          
#         for t, v in ndenumerate(animal_jaaba_feature):             
#             temp.write(delimiter.join('{}'.format(v) for v in [id_animal+1, t[0], t[0]+1, v, feature]) + "\n")
#      
#     # rewinds the file handle
#     temp.seek(0)
#      
# #     path_w='/Users/jespinosa/git/pergola/test'
#     if output == "csv":
#         _csv_file_ext = "csv" #del
#         if not path_w: 
#             path = getcwd()
#             print >>stderr, 'CSV file will be dump into \"%s\" ' \
#                            'as not path has been set in path_w' % (path)
#         else:
#             if exists(path_w):
#                 path = path_w
#             else:
#                 raise IOError('Provided path does not exists: %s' % path_w)
#                  
#         feature_file = open(join(path, feature + "." + _csv_file_ext), "wb")
#                  
#         copyfileobj(temp, feature_file)
#         temp.close()
#          
#     elif output == "IntData":
#         if not map_jaaba:
#             PATH = abspath(split(realpath(__file__))[0])
#             map_jaaba = PATH + "/jaaba2pergola.txt"
# #             map_jaaba = PATH + 
#              
#         map_jaaba = check_path(map_jaaba)
#         map = MappingInfo(map_jaaba)
#          
#         int_data_jaaba = IntData(temp.name, map_dict = map.correspondence)     
#         temp.close()
#          
#         return (int_data_jaaba)
   


        
