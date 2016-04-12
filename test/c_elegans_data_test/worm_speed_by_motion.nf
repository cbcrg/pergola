#!/usr/bin/env nextflow

/*
#################################################################################
### Jose Espinosa-Carrasco. CB/CSN-CRG. April 2016                            ###
#################################################################################
### Code : 04.12                                                              ### 
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

process get_speed {
  
  input:
  file file_worm from mat_files_speed
  
  output: 
  file '*_speed.csv' into speed_files
  
  script:
  println "Matlab file containing worm behavior processed: $file_worm"

  """
  $HOME/git/pergola/test/c_elegans_data_test/extract_worm_speed.py -i \"$file_worm\"
  """
}

speed_files_name = speed_files.flatten().map { speed_file_name ->   
  println speed_file_name.name
  
  [ speed_file_name, speed_file_name.name ]
}

// pergola command

// pergola_rules.py -i "575 JU440 on food L_2011_02_17__11_00___3___1_features_speed.csv" -m worms_speed2p.txt
"575 JU440 on food L_2011_02_17__11_00___3___1_features_speed.csv"
//-d one_per_channel 
//-nt -nh -s

map_speed_path = "$HOME/git/pergola/test/c_elegans_data_test/worms_speed2p.txt"
map_speed=file(map_speed_path)

body_parts =  ['head', 'headTip', 'midbody', 'tail', 'tailTip']

process speed_to_pergola {
  input:
  set file ('speed_file'), val (name_file) from speed_files_name  
  file worms_speed2p from map_speed
  each body_part from body_parts
  
  output: 
  set 'tr*.bed', body_part, name_file into bed_speed
  set 'tr*.bedGraph', body_part, name_file into bedGraph_speed
  set '*.fa', name_file, name_file into out_fasta
  
  """
  cat $worms_speed2p | sed 's/behavioural_file:$body_part > pergola:dummy/behavioural_file:$body_part > pergola:data_value/g' > mod_map_file   
  pergola_rules.py -i $speed_file -m mod_map_file
  pergola_rules.py -i $speed_file -m mod_map_file -f bedGraph -w 1 
  """
}

process zeros_bed_and_bedGraph {
  input:
  set file ('bed_file'), val(body_part), val(name_file) from bed_speed
  set file ('bedGraph_file'), val(body_part), val(name_file) from bedGraph_speed
  	
  output:
  set '*.no_na.bed', body_part, name_file into bed_speed_no_nas
  set '*.no_na.bedGraph', body_part, name_file into bedGraph_speed_no_nas
  
  set '*.no_tr.bed', body_part, name_file into bed_speed_no_track_line
  set '*.no_tr.bedGraph', body_part, name_file into bedGraph_speed_no_track_line
  
  //cat ${bed_file}".tmp" | sed 's/-10000/0/g' > ${bed_file}".bedZeros"
  //cat ${bedGraph_file}".tmp" | sed 's/-10000/0/g' > ${bedGraph_file}".bedGraphZeros"
 
  """
  cat $bed_file | sed 's/track name=\"1_a\"/track name=\"${body_part}_speed\"/g' > ${bed_file}".tmp"
  cat ${bed_file}".tmp" | grep -v "\\-10000" > ${bed_file}".no_na.bed"
  cat ${bed_file}".no_na.bed" | grep -v "track name" > ${bed_file}".no_tr.bed"
  
  cat $bedGraph_file | sed 's/track name=\"1_a\"/track name=\"${body_part}_speed\"/g' > ${bedGraph_file}".tmp"
  cat ${bedGraph_file}".tmp" | grep -v "\\-10000" > ${bedGraph_file}".no_na.bedGraph"
  cat ${bedGraph_file}".no_na.bedGraph" | grep -v "track name" > ${bed_file}".no_tr.bedGraph"  
  """			
}

// read_worm_data.py command example 
// $HOME/git/pergola/test/c_elegans_data_test/read_worm_data.py -i "575 JU440 on food L_2011_02_17__11_00___3___1_features.mat"

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
  set 'tr*.bedGraph', name_file into bedGraph_motion
  
  """
  pergola_rules.py -i $motion_file -m $worms_motion2p -nt
  pergola_rules.py -i $motion_file -m $worms_motion2p -f bedGraph -w 1 -nt 
  """
} 


//This ones can directly be processed with motion bed file
map_bed_path = "$HOME/git/pergola/test/c_elegans_data_test/bed2pergola.txt"
map_bed_pergola = file(map_bed_path)


process intersect_speed_motion {
	input:
	set file ('bed_speed_no_tr'), val (body_part), val(speed_name) from bed_speed_no_track_line
	set file ('motion_file'), val (motion_name) from bed_motion
	file bed2pergola from map_bed_pergola
	
	output:
	set '*.mean.bed', body_part, speed_name, motion_name into bed_mean_speed_motion
	
	"""
	$HOME/git/pergola/test/c_elegans_data_test/celegans_speed_i_motion.py -s $bed_speed_no_tr -m $motion_file -b $bed2pergola 
	"""
}