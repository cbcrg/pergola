#!/usr/bin/env python
#
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

################################################################
### Jose A Espinosa. CSN/CB-CRG Group. June 2016             ###
################################################################
### Script creates BedTools objects from a file containing   ###
### mice feeding behavior and uses tools from pybedtools to  ###
### intersect them with day phases (light/dark).             ###
### Generates a bed file for each track with the result of   ###
### the above described operations.                          ###
################################################################

import pybedtools
from os import path, getcwd, makedirs, chdir
from pergola import mapping
from pergola import intervals
from pergola import tracks
import subprocess

# base_dir = path.dirname(getcwd())
base_dir = getcwd()

out_dir = base_dir + "/results/"

if not path.exists(out_dir):
    makedirs(out_dir)

chdir(out_dir)

statistic = "count"

mapping_data = mapping.MappingInfo("../../../sample_data/feeding_behavior/b2g.txt")

int_data_b1 = intervals.IntData ("../../../sample_data/feeding_beh_CB1_mice/intake_CB1_B1.csv", map_dict=mapping_data.correspondence)
int_data_b2 = intervals.IntData ("../../../sample_data/feeding_beh_CB1_mice/intake_CB1_B2.csv", map_dict=mapping_data.correspondence)
int_data_b3 = intervals.IntData ("../../../sample_data/feeding_beh_CB1_mice/intake_CB1_B3.csv", map_dict=mapping_data.correspondence)
int_data_b4 = intervals.IntData ("../../../sample_data/feeding_beh_CB1_mice/intake_CB1_B4.csv", map_dict=mapping_data.correspondence)

data_read_b1 = int_data_b1.read(relative_coord=True)
data_read_b2 = int_data_b2.read(relative_coord=True)
data_read_b3 = int_data_b3.read(relative_coord=True)
data_read_b4 = int_data_b4.read(relative_coord=True)

# Check longest period of time of batches  
end_time = max (int_data_b1.max - int_data_b1.min, 
                int_data_b2.max - int_data_b2.min, 
                int_data_b3.max - int_data_b3.min, 
                int_data_b4.max - int_data_b4.min) 

data_read_all_batches = tracks.merge_tracks (tracks.merge_tracks (tracks.merge_tracks (data_read_b1, data_read_b2), data_read_b3), data_read_b4)

# print "###############", data_read_all_batches.data[-1] #del
# print "^^^^^^^^^^^^^^^^^^^^^^", data_read_all_batches.list_tracks #del
# print "^^^^^^^^^^^^^^^^^^^^^^", type (data_read_all_batches) #del

list_wt = [item for item in data_read_all_batches.list_tracks if int(item) % 2]
list_KO_cb1 = [item for item in data_read_all_batches.list_tracks if not int(item) % 2]

# print "list of ctrl mice....................", list_wt #del
# print "list of cb1 mice....................", list_KO_cb1 #del

## Dictionary to set colors of each type of food
# food_sc    orange
# food_fat    black
# water    blue
# saccharin    red
data_type_col = {'food_sc': 'orange', 'food_fat':'black'}

bed_dict = dict()

# print "wt mice>>>>>>>", list_wt #del

bed_dict ['wt'] = {}
bed_dict ['KO_cb1'] = {}

bed_dict ['wt']['food_sc'] = data_read_all_batches.convert(mode="bed", data_types=["food_sc"], #dataTypes_actions="all", 
                                                           color_restrictions=data_type_col, tracks=list_wt)
bed_dict ['wt']['food_fat'] = data_read_all_batches.convert(mode="bed", data_types=["food_fat"], #dataTypes_actions="all", 
                                                            color_restrictions=data_type_col, tracks=list_wt)
bed_dict ['KO_cb1']['food_sc'] = data_read_all_batches.convert(mode="bed", data_types=["food_sc"], #dataTypes_actions="all", 
                                                               color_restrictions=data_type_col, tracks=list_KO_cb1)
bed_dict ['KO_cb1']['food_fat'] =  data_read_all_batches.convert(mode="bed", data_types=["food_fat"], #dataTypes_actions="all", 
                                                                 color_restrictions=data_type_col, tracks=list_KO_cb1)                                

mapping_bed = mapping.MappingInfo("../../../test/pybed2perg.txt")

####################
## Generate to BedTool objects containing light and dark phases

## Write phases file
# mapping.write_cytoband(int_data, end = int_data.max - int_data.min, delta=43200, start_phase="light")
mapping.write_cytoband(end = end_time, delta=43200, start_phase="light", path_w=out_dir)

light_ph_f = out_dir +  "phases_light.bed"
dark_ph_f = out_dir + "phases_dark.bed"

light_bed = pybedtools.BedTool(light_ph_f)
dark_bed = pybedtools.BedTool(dark_ph_f)

# for (tr, exp_gr), dict_beds  in bed_dict.iteritems():
for exp_group, dict_exp_gr in bed_dict.iteritems():
    print "exp_group.............", exp_group#, exp_gr
# #         print "exp_group------------------", exp_group, data_type
#         
    for data_type, dict_bed in dict_exp_gr.iteritems():
        for tr, bed in dict_bed.iteritems(): 
# #             print "tr------------------", tr
#             print "tr, exp_group------------------", tr, exp_group, data_type, data_type_bed#, bed
            
#             print bed
            bed_BedTools = bed.create_pybedtools()
            
            ## Generates a bed file of a single interval of the size of the whole recording
            list_full_length = [(bed_BedTools[0]["chrom"], bed_BedTools[0]["start"], bed_BedTools[bed_BedTools.count() - 1]["end"], 0)]
            bed_full_length = pybedtools.BedTool(list_full_length)
#             
            # no hace falta esto porque en este caso no calculo el complemento
#             bed_merged_fn = bed_BedTools.merge(d=120, stream=True, c=(4,5,6,9), o=("distinct","sum","distinct","collapse")).saveas().fn
              
            # Creates a new pergola object after merging bouts
#             pybed_intdata = intervals.IntData(bed_merged_fn, map_dict=mapping_bed.correspondence, header=False, fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])
#             pybed_intdata_read = pybed_intdata.read(relative_coord=False)
                   
        #     pybed_tr_merged = pybed_intdata_read.convert(mode="bed", data_types=["food_sc", "food_fat"], data_types_actions="all", color_restrictions=data_type_col)
              
#             bed_merged = pybedtools.BedTool(bed_merged_fn)
        #     print pybed_tr_merged
#             print '*********************tr_' + exp_group + '.' + '.'.join(tr) + ".dark.bed"
#             print '*********************tr_>>>>>>>>>>>>' + tr
            
            ###
            ####### KEEP
            ###
            # Intersect light and dark phases with bouts
#             light_bouts_bed = bed_BedTools.intersect(light_bed).saveas('all_bouts.' + exp_group + '.' + '.'.join(tr) + ".light.bed")
#             dark_bouts_bed = bed_BedTools.intersect(dark_bed).saveas('all_bouts.' + exp_group + '.' + '.'.join(tr) + ".dark.bed")
            light_bouts_bed = bed_BedTools.intersect(light_bed)
            dark_bouts_bed = bed_BedTools.intersect(dark_bed)           
            
            ## Para que me salga mean of means (N2_hourly_mean_measures)
            # celegans_feature_mean.py 
            
            ###################
            # Generate mean value of the whole record after intersecting with phase
            if light_bouts_bed.count() == 0: 
#                 print >> stderr, "No intervals inside the bed file\n"
                # When there is any interval we set the mean to zero
                list_no_intervals = [("chr1", 0, 1, "no_intervals", 0)]
#                 list_full_length = [(phenotypic_feature_bt[0]["chrom"], phenotypic_feature_bt[0]["start"], phenotypic_feature_bt[phenotypic_feature_bt.count() - 1]["end"], 0)]
                bed_no_intervals = pybedtools.BedTool(list_no_intervals).saveas('tr_' + exp_group + '.' + '.'.join(tr) + ".light.bed")  
            else: 
                bed_full_length.map(light_bouts_bed, c=5, o=statistic, null=0).saveas ('tr_' + exp_group + '.' + '.'.join(tr) + ".light.bed")
            
            if dark_bouts_bed.count() == 0: 
#                 print >> stderr, "No intervals inside the bed file\n"
                # When there is any interval we set the mean to zero
                list_no_intervals = [("chr1", 0, 1, "no_intervals", 0)]
                bed_no_intervals = pybedtools.BedTool(list_no_intervals).saveas('tr_' + exp_group + '.' + '.'.join(tr) + ".dark.bed")  
            else: 
                bed_full_length.map(dark_bouts_bed, c=5, o=statistic, null=0).saveas ('tr_' + exp_group + '.' + '.'.join(tr) + ".dark.bed")


# Define command and arguments
command = 'Rscript'
path2script = 'path/to your script/max.R'
script_path = base_dir + "/bin/"

# Variable number of args in a list
args = ['--tag', statistic, '--path2files', out_dir, '--path2plot', out_dir ]
# --tag="mean" --path2files="/Users/jespinosa/phecomp/20140807_pergola/bedtools_ex/starting_regions_file_vs_24h/" --path2plot=
# Build subprocess command
cmd = [command, script_path] + args

# check_output will run the command and store to result
# check_output
subprocess.call (cmd, universal_newlines=True)

# print('The maximum of the numbers is:', x)

#             int_data_phenotypic = intervals.IntData(bed_ph_file, map_dict=mapping_bed.correspondence, header=False, 
#                                    fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])

# phenotypic_data_read = int_data_phenotypic.read(relative_coord=False)
# bed_obj_phenotypic = phenotypic_data_read.convert(mode="bed")
# key_s = bed_obj_phenotypic.keys()[0]
# phenotypic_feature_bt = bed_obj_phenotypic[key_s].create_pybedtools()
# 
# ### Getting mean value of the intervals of the file containing the phenotypic feature:
# ## Generates a bed file of a single interval of the size of the whole bed file
# list_full_length = [(phenotypic_feature_bt[0]["chrom"], phenotypic_feature_bt[0]["start"], phenotypic_feature_bt[phenotypic_feature_bt.count() - 1]["end"], 0)]
# bed_full_length = pybedtools.BedTool(list_full_length)
# 
# ###################
# # Generate mean value of the whol
# if phenotypic_feature_bt.count() == 0: 
#     print >> stderr, "No intervals inside the bed file\n"
#     # When there is any interval we set the mean to zero
#     list_no_intervals = [(phenotypic_feature_bt[0]["chrom"], phenotypic_feature_bt[0]["start"], phenotypic_feature_bt[phenotypic_feature_bt.count() - 1]["end"], 0, 0)]
#     bed_no_intervals = pybedtools.BedTool(list_no_intervals).saveas(tag_file + ".mean_file.bed")  
# else: 
#     bed_full_length.map(phenotypic_feature_bt, c=5, o="mean", null=0).saveas (tag_file + ".mean_file.bed")



# for exp_group in bed_dict:    
#     for data_type, dict_exp_gr in bed_dict[exp_group].iteritems():
# #         print "exp_group------------------", exp_group, data_type
#         
#         for tr, bed in dict_exp_gr.iteritems():
# #             print "tr------------------", tr
# #             print "exp_group------------------", exp_group, data_type
#             bed_BedTools = bed.create_pybedtools()
#             
#             # no hace falta esto porque en este caso no calculo el complemento
# #             bed_merged_fn = bed_BedTools.merge(d=120, stream=True, c=(4,5,6,9), o=("distinct","sum","distinct","collapse")).saveas().fn
#              
#             # Creates a new pergola object after merging bouts
# #             pybed_intdata = intervals.IntData(bed_merged_fn, map_dict=mapping_bed.correspondence, header=False, fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])
# #             pybed_intdata_read = pybed_intdata.read(relative_coord=False)
#                   
#         #     pybed_tr_merged = pybed_intdata_read.convert(mode="bed", data_types=["food_sc", "food_fat"], data_types_actions="all", color_restrictions=data_type_col)
#              
# #             bed_merged = pybedtools.BedTool(bed_merged_fn)
#         #     print pybed_tr_merged
#              
#             # Intersect light and dark phases with bouts
#             light_bouts_bed = bed_BedTools.intersect(light_bed).saveas('tr_' + exp_group + '.' + '.'.join(tr) + ".light.bed")
#             dark_bouts_bed = bed_BedTools.intersect(dark_bed).saveas('tr_' + exp_group + '.' + '.'.join(tr) + ".dark.bed")         
#             
            # EN TODO CASO DEBERIA HACER LA INTERSECCION Y ENTONCES MAPAR EN TODO LA LONGITUD, COMO EN CELEGNAS_FEATURE_I_MOTION.PY 
            # bed_full_length.map(ph_feature_motion_bt, c=5, o="mean", null=0).saveas (tag_file + ".mean_file.bed")
            # PARA QUE ME SALGA LA MEDIA DE TODOS A LAS VEZ
#             light_bed.map (bed_BedTools, c=5, o="mean", null=0).saveas ('tr_' + exp_group + '.' +'.'.join(tr) + ".light.bed")
#             dark_bed.map (bed_BedTools, c=5, o="mean", null=0).saveas ('tr_' + exp_group + '.' +'.'.join(tr) + ".dark.bed")
            
            
#             bed_full_length.map(ph_feature_motion_bt, c=5, o="mean", null=0).saveas (tag_file + ".mean_file.bed")
            
            
            
            
            
#         bedSingle = bed_str_ctrl[key]
#         bedSingle.save_track(path="/Users/jespinosa/Desktop/track_bed/")

# bed_str = data_read_all_batches.convert(mode="bed", data_types=["food_sc", "food_fat"], data_types_actions="all", color_restrictions=data_type_col)
# bed_str = data_read_all_batches.convert(mode="bed", data_types=["food_sc", "food_fat"], data_types_actions="all", color_restrictions=data_type_col)


# mapping_bed = mapping.MappingInfo(out_dir + "/pybed2perg.txt")

# 
# # Experimentals phases
# # Habituation phase (before high-fat food introduction)
# # Development phase (after high-fat food introduction)

# mapping_file_data_exp_ph = mapping.MappingInfo(base_dir + "/sample_data/feeding_behavior/f2g.txt")
# exp_ph_data = intervals.IntData(base_dir + "/sample_data/feeding_behavior/phases_exp.csv", map_dict=mapping_file_data_exp_ph.correspondence)
# data_exp_ph_tr = exp_ph_data.read(relative_coord=True)  
# exp_ph_bed = data_exp_ph_tr.convert(mode="bed", dataTypes_actions="all", tracks_merge=exp_ph_data.tracks)
# 
# hab_bed = exp_ph_bed [('1_2', 'Habituation phase')].new_create_pybedtools()
# dev_bed = exp_ph_bed [('1_2', 'Development phase')].new_create_pybedtools()
# 
## For each track merge feeding acts that are separated by less than 120 seconds (thus generating feeding bouts track)
## Calculates the complement of feeding bouts (intermeal intervals) and intersect them with day and experimental phases
## Dumping results into bed files
########################
# for tr, bed in bed_str.iteritems():
# #     print "tr------------------", tr
#     bed_BedTools = bed.create_pybedtools()
#     bed_merged_fn = bed_BedTools.merge(d=120, stream=True, c=(4,5,6,9), o=("distinct","sum","distinct","collapse")).saveas().fn
#     
#     # Creates a new pergola object after merging bouts
#     pybed_intdata = intervals.IntData(bed_merged_fn, map_dict=mapping_bed.correspondence, header=False, fields_names=['chrm', 'start', 'end', 'nature', 'value', 'strain', 'color'])
#     pybed_intdata_read = pybed_intdata.read(relative_coord=False)
#          
# #     pybed_tr_merged = pybed_intdata_read.convert(mode="bed", data_types=["food_sc", "food_fat"], data_types_actions="all", color_restrictions=data_type_col)
#     
#     bed_merged = pybedtools.BedTool(bed_merged_fn)
# #     print pybed_tr_merged
#     
#     # Intersect light and dark phases with bouts
#     light_bouts_bed = bed_merged.intersect(light_bed).saveas('tr_' + '_'.join(tr) + "_light.bed")
#     dark_bouts_bed = bed_merged.intersect(dark_bed).saveas('tr_' + '_'.join(tr) + "_dark.bed")
#    
#########################
#     hab_light_intermeals_bed = bed_merged_comp.intersect(hab_bed).intersect(light_bed).saveas('tr_' + '_'.join(tr) + "_compl_hab_light.bed")
#     hab_dark_intermeals_bed = bed_merged_comp.intersect(hab_bed).intersect(dark_bed).saveas('tr_' + '_'.join(tr) + "_compl_hab_dark.bed")
#     dev_light_intermeals_bed = bed_merged_comp.intersect(dev_bed).intersect(light_bed).saveas('tr_' + '_'.join(tr) + "_compl_dev_light.bed")
#     dev_dark_intermeals_bed = bed_merged_comp.intersect(dev_bed).intersect(dark_bed).saveas('tr_' + '_'.join(tr) + "_compl_dev_dark.bed")

#     
#     ## Complement
#     bed_merged_comp = pybedtools.BedTool(bed_merged_fn).complement(g=chr_file)
# 
#     hab_light_intermeals_bed = bed_merged_comp.intersect(hab_bed).intersect(light_bed).saveas('tr_' + '_'.join(tr) + "_compl_hab_light.bed")
#     hab_dark_intermeals_bed = bed_merged_comp.intersect(hab_bed).intersect(dark_bed).saveas('tr_' + '_'.join(tr) + "_compl_hab_dark.bed")
#     dev_light_intermeals_bed = bed_merged_comp.intersect(dev_bed).intersect(light_bed).saveas('tr_' + '_'.join(tr) + "_compl_dev_light.bed")
#     dev_dark_intermeals_bed = bed_merged_comp.intersect(dev_bed).intersect(dark_bed).saveas('tr_' + '_'.join(tr) + "_compl_dev_dark.bed")