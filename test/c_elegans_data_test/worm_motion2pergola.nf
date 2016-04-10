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

mat_files_path = "${path_files}*.mat"
mat_files = Channel.fromPath(mat_files_path)

// read_worm_data.py command example 
// $HOME/git/pergola/test/c_elegans_data_test/read_worm_data.py -i "575 JU440 on food L_2011_02_17__11_00___3___1_features.mat"

mat_files.into { mat_files_speed; mat_files_motion }


//./extract_worm_motion.py -i "575 JU440 on food L_2011_02_17__11_00___3___1_features.mat"

process get_motion {
  
  input:
  file file_worm from mat_files_motion
  
  output: 
  file '*.csv' into motion_files
  
  script:
  println "Matlab file containing worm behavior processed: $file_worm"

  """
  $HOME/git/pergola/test/c_elegans_data_test/extract_worm_motion.py -i \"$file_worm\"
  """
}

motion_files_name = motion_files.flatten().map { motion_file_name ->   
  println motion_file_name.name
  
  [ motion_file_name, motion_file_name.name ]
}

map_motion_path = "$HOME/git/pergola/test/c_elegans_data_test/worms_motion2p.txt"
map_motion=file(map_motion_path)

process motion_to_pergola {
  input:
  set file ('motion_file'), val (name_file) from motion_files_name
  set worms_motion2p from map_motion
  
  output:
  set 'tr*.bed', name_file into bed_motion
  
  """
  pergola_rules.py -i $motion_file -m $worms_motion2p
  """
} 

bed_motion.subscribe {   
  bed_file = it[0]
  bed_file.copyTo ( it[1] + ".bed" )
}

