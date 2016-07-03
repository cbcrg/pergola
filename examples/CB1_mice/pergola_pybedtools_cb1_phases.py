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

from argparse import ArgumentParser
from os import path, getcwd, makedirs, chdir
from shutil import rmtree
from sys import stderr
import subprocess
import pybedtools
from pergola import mapping
from pergola import intervals
from pergola import tracks

_stats_available = ['mean', 'count', 'sum', 'max', 'min', 'median' ]

parser = ArgumentParser(description='Statistic to calculate from the data')
parser.add_argument('-s','--statistic', help='Choose one of the possible statistical available on Bedtools map option',
                     required=True, choices=_stats_available)

args = parser.parse_args()

print >> stderr, "Statistic to be calculated: %s" % args.statistic

# Statistic to calculate
statistic = args.statistic

mapping_data = mapping.MappingInfo("../../sample_data/feeding_behavior/b2g.txt")
 
int_data_b1 = intervals.IntData ("../../sample_data/feeding_beh_CB1_mice/intake_CB1_B1.csv", map_dict=mapping_data.correspondence)
int_data_b2 = intervals.IntData ("../../sample_data/feeding_beh_CB1_mice/intake_CB1_B2.csv", map_dict=mapping_data.correspondence)
int_data_b3 = intervals.IntData ("../../sample_data/feeding_beh_CB1_mice/intake_CB1_B3.csv", map_dict=mapping_data.correspondence)
int_data_b4 = intervals.IntData ("../../sample_data/feeding_beh_CB1_mice/intake_CB1_B4.csv", map_dict=mapping_data.correspondence)

mapping_bed = mapping.MappingInfo("../../test/pybed2perg.txt")

# base_dir = path.dirname(getcwd())
base_dir = getcwd()
 
out_dir = base_dir + "/results/" + statistic + "/"
 
if path.exists(out_dir):    
    rmtree(out_dir)

makedirs(out_dir)

chdir(out_dir)
 
data_read_b1 = int_data_b1.read(relative_coord=True)
data_read_b2 = int_data_b2.read(relative_coord=True)
data_read_b3 = int_data_b3.read(relative_coord=True)
data_read_b4 = int_data_b4.read(relative_coord=True)
 
# Check the longest period of time of any batches  
end_time = max (int_data_b1.max - int_data_b1.min, 
                int_data_b2.max - int_data_b2.min, 
                int_data_b3.max - int_data_b3.min, 
                int_data_b4.max - int_data_b4.min) 
 
data_read_all_batches = tracks.merge_tracks (tracks.merge_tracks (tracks.merge_tracks (data_read_b1, data_read_b2), data_read_b3), data_read_b4)
 
list_wt = [item for item in data_read_all_batches.list_tracks if int(item) % 2]
list_KO_cb1 = [item for item in data_read_all_batches.list_tracks if not int(item) % 2]
 
## Dictionary to set colors of each type of food
# food_sc    orange
# food_fat    black
# water    blue
# saccharin    red
data_type_col = {'food_sc': 'orange', 'food_fat':'black'}
 
bed_dict = dict()
 
bed_dict ['wt'] = {}
bed_dict ['KO_cb1'] = {}
 
bed_dict ['wt']['food_sc'] = data_read_all_batches.convert(mode="bed", data_types=["food_sc"],
                                                           color_restrictions=data_type_col, tracks=list_wt)
bed_dict ['wt']['food_fat'] = data_read_all_batches.convert(mode="bed", data_types=["food_fat"],
                                                            color_restrictions=data_type_col, tracks=list_wt)
bed_dict ['KO_cb1']['food_sc'] = data_read_all_batches.convert(mode="bed", data_types=["food_sc"],
                                                               color_restrictions=data_type_col, tracks=list_KO_cb1)
bed_dict ['KO_cb1']['food_fat'] =  data_read_all_batches.convert(mode="bed", data_types=["food_fat"],
                                                                 color_restrictions=data_type_col, tracks=list_KO_cb1)                                
 
####################
## Generate to BedTool objects containing light and dark phases
 
## Write phases file
# mapping.write_cytoband(int_data, end = int_data.max - int_data.min, delta=43200, start_phase="light")
mapping.write_cytoband(end = end_time, delta=43200, start_phase="light", path_w=out_dir)
 
light_ph_f = out_dir +  "phases_light.bed"
dark_ph_f = out_dir + "phases_dark.bed"
 
light_bed = pybedtools.BedTool(light_ph_f)
dark_bed = pybedtools.BedTool(dark_ph_f)

## Reading experimental phases from csv file
mapping_data_phases = mapping.MappingInfo("../../data/f2g.txt")
 
int_exp_phases = intervals.IntData ("../../data/exp_phases.csv", map_dict=mapping_data_phases.correspondence)
data_read_exp_phases = int_exp_phases.read(relative_coord=True)

d_exp_phases_bed2file = data_read_exp_phases.convert(mode="bed", data_types_actions="all")
d_exp_phases_bed2file[d_exp_phases_bed2file.keys()[0]].save_track(bed_label="True", path=base_dir + "/results/", name_file="exp_phases")

d_exp_phases_bed = data_read_exp_phases.convert(mode="bed", data_types_actions='one_per_channel')

# basal_bed = exp_phases_bed['1', 'Basal'].create_pybedtools()
# nicotine_bed = exp_phases_bed['1', 'Nicotine_withdrawal'].create_pybedtools()
# withdrawal_bed = exp_phases_bed['1', 'Nicotine_treatment'].create_pybedtools()

for exp_group, dict_exp_gr in bed_dict.iteritems():
       
    for data_type, dict_bed in dict_exp_gr.iteritems():
        for tr, bed in dict_bed.iteritems(): 
            bed_BedTools = bed.create_pybedtools()
             
            ## Generates a bed file of a single interval of the size of the whole recording
            list_full_length = [(bed_BedTools[0]["chrom"], bed_BedTools[0]["start"], bed_BedTools[bed_BedTools.count() - 1]["end"], 0)]
            bed_full_length = pybedtools.BedTool(list_full_length)                         
            
            for key, bed_phase in d_exp_phases_bed.iteritems():
                phase = key[1]
                
                if not path.isfile(phase + ".bed"):
                    bed_phase.create_pybedtools().saveas(phase + ".bed")
                                
                light_bouts_bed = bed_BedTools.intersect(pybedtools.BedTool(phase + ".bed")).intersect(light_bed)
                dark_bouts_bed = bed_BedTools.intersect(pybedtools.BedTool(phase + ".bed")).intersect(dark_bed)
                
                ###################
                # Generate mean value of the whole record after intersecting with phase
                if light_bouts_bed.count() == 0: 
                    # When there is any interval we set the mean to zero
                    list_no_intervals = [("chr1", 0, 1, "no_intervals", 0)]
                    bed_no_intervals = pybedtools.BedTool(list_no_intervals).saveas('tr_' + exp_group + '.' + '.'.join(tr) + ".light." + phase + ".bed")  
                else: 
                    bed_full_length.map(light_bouts_bed, c=5, o=statistic, null=0).saveas ('tr_' + exp_group + '.' + '.'.join(tr) + ".light." + phase + ".bed")
                 
                if dark_bouts_bed.count() == 0: 
                    list_no_intervals = [("chr1", 0, 1, "no_intervals", 0)]
                    bed_no_intervals = pybedtools.BedTool(list_no_intervals).saveas('tr_' + exp_group + '.' + '.'.join(tr) + ".dark." + phase + ".bed")  
                else: 
                    bed_full_length.map(dark_bouts_bed, c=5, o=statistic, null=0).saveas ('tr_' + exp_group + '.' + '.'.join(tr) + ".dark." + phase + ".bed")


# Define command and arguments
command = 'Rscript'

## Command template in local
# Rscript /Users/jespinosa/git/pergola/examples/CB1_mice/bin/stats_analysis_CB1.R --path2files="/Users/jespinosa/git/pergola/examples/CB1_mice/results/" 
# --path2plot="/Users/jespinosa/git/pergola/examples/CB1_mice/results/" --tag="mean"

script_path = base_dir + "/bin/plots_CB1_phase.R"

args = [ '--stat=' + statistic, '--path2files=' + out_dir, '--path2plot=' + out_dir ] 
cmd = [command, script_path] + args

# subprocess.call (cmd, universal_newlines=True)
subprocess.call (cmd, universal_newlines=True)
