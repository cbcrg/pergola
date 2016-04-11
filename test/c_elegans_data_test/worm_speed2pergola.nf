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
  set 'tr*.bed', body_part, name_file into bed_speed, bed_speed_cp
  set 'tr*.bedGraph', body_part, name_file into bedGraph_speed, bedGraph_speed_cp
  set '*.fa', name_file, name_file into out_fasta
  
  """
  cat $worms_speed2p | sed 's/behavioural_file:$body_part > pergola:dummy/behavioural_file:$body_part > pergola:data_value/g' > mod_map_file   
  pergola_rules.py -i $speed_file -m mod_map_file
  pergola_rules.py -i $speed_file -m mod_map_file -f bedGraph -w 1 
  """
}

bed_speed.subscribe {   
  bed_file = it[0]
  bed_file.copyTo ( it[1] + "." + it[2] + ".bed" )
}

out_fasta.subscribe {   
  fasta_file = it[0]
  fasta_file.copyTo ( it[1] + ".fa" )
}

bedGraph_speed.subscribe {   
  bedGraph_file = it[0]
  bedGraph_file.copyTo ( it[1] + "." + it[2] + ".bedGraph" )
}

process zeros_bed_and_bedGraph {
  input:
  set file ('bed_file'), val(body_part), val(name_file) from bed_speed_cp
  set file ('bedGraph_file'), val(body_part), val(name_file) from bedGraph_speed_cp
  	
  output:
  set '*.bedZeros', body_part, name_file into bed_speed_zeros
  set '*.bedGraphZeros', body_part, name_file into bedGraph_speed_zeros
  
  """
  cat $bed_file | sed 's/-10000/0/g' > ${bed_file}".bedZeros"
  cat $bedGraph_file | sed 's/-10000/0/g' > ${bedGraph_file}".bedGraphZeros" 
  """			
}

bed_speed_zeros.subscribe {   
  bed_file = it[0]
  bed_file.copyTo ( it[1] + "." + it[2] + "_zeros.bed" )
}

bedGraph_speed_zeros.subscribe {   
  bedGraph_file = it[0]
  bedGraph_file.copyTo ( it[1] + "." + it[2] + "_zeros.bedGraph" )
}
