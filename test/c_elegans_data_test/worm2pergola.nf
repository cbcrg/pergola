#!/usr/bin/env nextflow

/*
#################################################################################
### Jose Espinosa-Carrasco. CB/CSN-CRG. April 2016                            ###
#################################################################################
### Code : 04.07                                                              ### 
### Worm DB processed by pergola for paper                                    ###
#################################################################################
*/

//path_files = "$HOME/2016_worm_DB/ju440_all/"
path_files = "$HOME/git/pergola/test/c_elegans_data_test/"

body_parts =  ['head', 'headTip', 'midbody', 'tail', 'tailTip']

mat_files_path = "${path_files}*.mat"
mat_files = Channel.fromPath(mat_files_path)
 
process get_speed {
  
  input:
  file file_worm from mat_files
  
  output: 
  file '*_speed.csv' into speed_files
  
  script:
  println "Options for SR calculation are: $file_worm"

  """
  $HOME/git/pergola/test/c_elegans_data_test/read_worm_data.py -i \"$file_worm\"
  """
}

//pergola command
//575 JU440 on food L_2011_02_17__11_00___3___1_features_speed.csv

// pergola_rules.py -i "575 JU440 on food L_2011_02_17__11_00___3___1_features_speed.csv" -m worms_speed2p.txt
//-d one_per_channel 
//-nt -nh -s

map_speed_path = "$HOME/git/pergola/test/c_elegans_data_test/worms_speed2p.txt"

map_speeds=file(map_speed_path)

process speed_to_pergola {
  input:
  file speed_file from speed_files
  file worms_speed2p from map_speeds
    
  output:
  stdout result
  
  """
  pergola_rules.py -i $speed_file -m $worms_speed2p
  """
} 

//val body_part from body_parts
  


