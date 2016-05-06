#!/usr/bin/env nextflow

/*
*  Copyright (c) 2014-2016, Centre for Genomic Regulation (CRG).
*  Copyright (c) 2014-2016, Jose Espinosa-Carrasco and the respective authors.
*
*  This file is part of Pergola.
*
*  Pergola is free software: you can redistribute it and/or modify
*  it under the terms of the GNU General Public License as published by
*  the Free Software Foundation, either version 3 of the License, or
*  (at your option) any later version.
*
*  Pergola is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*  GNU General Public License for more details.
*
*  You should have received a copy of the GNU General Public License
*  along with Pergola.  If not, see <http://www.gnu.org/licenses/>.
*/

/*
* Wormbehavior DB (http://wormbehavior.mrc-lmb.cam.ac.uk/) processed by pergola for paper
* Process mat files downloaded from the DB to extract periods of motion (forward, backward, 
* and turns) in order to intersect them with speed during this periods using pergola
*/    


params.path_files = "$HOME/git/pergola/test/c_elegans_data_test/"

mat_files_path = "${params.path_files}*.mat"
mat_files = Channel.fromPath(mat_files_path)

// read_worm_data.py command example 
// $HOME/git/pergola/test/c_elegans_data_test/read_worm_data.py -i "575 JU440 on food L_2011_02_17__11_00___3___1_features.mat"


// Name of input file and file 
mat_files_name = mat_files.flatten().map { mat_files_file ->      
   def content = mat_files_file
   def name = mat_files_file.name.replaceAll(/ /,'_')
   [ content, name ]
}

mat_files_name.into { mat_files_speed; mat_files_motion; mat_files_turns}

process get_speed {

  input:
  set file ('file_worm'), val (name_file_worm) from mat_files_speed

  
  output:  
  set '*_speed.csv', name_file_worm into speed_files, speed_files_toprint
    
  script:
  println "Matlab file containing worm behavior processed: $name_file_worm"

  """
  extract_worm_speed.py -i $file_worm
  """
}

/*
speed_files_toprint.subscribe {
	println ">>>> ${it[0].name}"	
}
*/
/*
speed_files_name = speed_files.flatten().map { //speed_file_name ->
  file_speed = it[0]  
  mat_file_name = it[1]
  //println speed_file_name.name
  println "file_speed_name -------- mat_file_name"
  //[ speed_file_name, speed_file_name.name ]
  [ file_speed, file_speed_name, mat_file_name ]
}
*/


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
  set file ('speed_file'), val (name_file) from speed_files  
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
  
  //set '*.no_tr.bed', body_part, name_file into bed_speed_no_track_line
  //set '*.no_tr.bedGraph', body_part, name_file into bedGraph_speed_no_track_line
  set name_file, body_part, '*.no_tr.bed' into bed_speed_no_track_line, bed_speed_no_track_line_cp, bed_speed_no_track_line_turns
  set name_file, body_part, '*.no_tr.bedGraph' into bedGraph_speed_no_track_line
  
  //cat ${bed_file}".tmp" | sed 's/-10000/0/g' > ${bed_file}".bedZeros"
  //cat ${bedGraph_file}".tmp" | sed 's/-10000/0/g' > ${bedGraph_file}".bedGraphZeros"
 
  //echo -e "chr1\t0\t100\t.\t-10000\t+\t0\t100\t135,206,250" >> ${bed_file}${name_file}".no_na.bed"
  //echo -e "chr1\t0\t100\t100000" >> ${bedGraph_file}".no_na.bedGraph"
  //cat ${bed_file}${name_file}".no_na.bed" | grep -v "track name" > ${bed_file}".no_tr.bed" || echo -e "chr1\t0\t100\t.\t100000\t+\t0\t100\t135,206,250\n" > ${bed_file}".no_tr.bed"
   
  """
  cat $bed_file | sed 's/track name=\"1_a\"/track name=\"${body_part}_speed\"/g' > ${bed_file}".tmp"
  cat ${bed_file}".tmp" | grep -v "\\-10000" > ${bed_file}${name_file}".no_na.bed"  
  cat ${bed_file}${name_file}".no_na.bed" | grep -v "track name" > ${bed_file}".no_tr.bed" || echo -e "chr1\t0\t100\t.\t-10000\t+\t0\t100\t135,206,250" > ${bed_file}".no_tr.bed"
  
  cat $bedGraph_file | sed 's/track name=\"1_a\"/track name=\"${body_part}_speed\"/g' > ${bedGraph_file}".tmp"
  cat ${bedGraph_file}".tmp" | grep -v "\\-10000" > ${bedGraph_file}".no_na.bedGraph"  
  cat ${bedGraph_file}".no_na.bedGraph" | grep -v "track name" > ${bedGraph_file}".no_tr.bedGraph" || echo -e echo -e "chr1\t0\t100\t100000" > ${bedGraph_file}".no_tr.bedGraph" 
  """			
}

////////

// read_worm_data.py command example 
// $HOME/git/pergola/test/c_elegans_data_test/read_worm_data.py -i "575 JU440 on food L_2011_02_17__11_00___3___1_features.mat"

//./extract_worm_motion.py -i "575 JU440 on food L_2011_02_17__11_00___3___1_features.mat"

process get_motion {
  
  input:
  set file ('file_worm'), val (name_file_worm) from mat_files_motion
  
  output: 
  set name_file_worm, '*.csv' into motion_files, motion_files_cp
    
  script:
  println "Matlab file containing worm behavior processed: $file_worm"

  """
  $HOME/git/pergola/test/c_elegans_data_test/extract_worm_motion.py -i \"$file_worm\"
  """
}

// From 1 mat I get 3 motions (forward, paused, backward)
// I made a channel with matfile1 -> forward
//                       matfile1 -> backward
//                       matfile1 -> paused
//                       matfile2 -> forward ...

motion_files_flat = motion_files.map { name_mat, motion_f ->
        motion_f.collect {            
            [ it, name_mat, it.name ]
        }
    }
    .flatMap()
    
map_motion_path = "$HOME/git/pergola/test/c_elegans_data_test/worms_motion2p.txt"
map_motion = file(map_motion_path)

process motion_to_pergola {
  input:
  set file ('motion_file'), val (name_file), val (name_file_motion) from motion_files_flat
  set worms_motion2p from map_motion
  
  output:
  set name_file, 'tr*.bed', name_file_motion into bed_motion, bed_motion_wr, bed_motion_turns
  set name_file, 'tr*.bedGraph', name_file_motion into bedGraph_motion
  
  """
  pergola_rules.py -i $motion_file -m $worms_motion2p -nt
  pergola_rules.py -i $motion_file -m $worms_motion2p -f bedGraph -w 1 -nt 
  """
} 

//This ones can directly be processed with motion bed file
map_bed_path = "$HOME/git/pergola/test/c_elegans_data_test/bed2pergola.txt"
//map_bed_pergola = file(map_bed_path)
map_bed_pergola = Channel.fromPath(map_bed_path)
map_bed_pergola.into { map_bed_pergola_speed; map_bed_pergola_turn}

// I use filter to delete pairs that do not come from the same original mat file
bed_speed_motion = bed_speed_no_track_line
	.spread(bed_motion)
	.filter { it[0] == it[3] }

process intersect_speed_motion {
	input:
	set val (mat_file_speed), val (body_part), file ('bed_speed_no_tr'), val (mat_motion_file), file ('motion_file'), val (name_file_motion) from bed_speed_motion
	file bed2pergola from map_bed_pergola_speed.first()
	
	output:
	set '*.mean.bed', body_part, mat_file_speed, mat_motion_file, name_file_motion into bed_mean_speed_motion	
	set '*.mean.bedGraph', body_part, mat_file_speed, mat_motion_file, name_file_motion into bedGr_mean_speed_motion
	set '*.intersect.bed', body_part, mat_file_speed, mat_motion_file, name_file_motion into bed_intersect_speed_motion, bed_intersect_speed_motion2p
	
	"""
	$HOME/git/pergola/test/c_elegans_data_test/celegans_speed_i_motion.py -s $bed_speed_no_tr -m $motion_file -b $bed2pergola	
	"""
}

/*
// This version works but it could be even more simplified by the code below
// bed_intersect_speed_motion2p.subscribe { println it }
bed_intersect_speed_motion_plot = bed_intersect_speed_motion2p.map {
	def name = it[1] + "_" + it[3].split("_on_")[0] + "_" + it[4].tokenize(".")[1]
	def file = it [0]	
	[name, file]
}.groupTuple()	
.collectFile(newLine: true) { 
	[ it[0], it[1].collect{ it2 -> it2.text }.join()+'\n' ] 
}.subscribe { println it } 
*/

bed_intersect_speed_motion_plot = bed_intersect_speed_motion2p.collectFile(newLine: false, sort:'none') { 
	def name = it[1] + "_" + it[3].split("_on_")[0] + "_" + it[4].tokenize(".")[1] 
	[ name, it[0].text ] 
}
//.subscribe { println it }

process plot_distro {
  input:
  file intersect_speed_motion from bed_intersect_speed_motion_plot
  
  output:
  set '*.png' into plots_speed_motion
    
  script:
  println ">>>>>>>>>>>>>>>: $intersect_speed_motion"
  	
  """
  export R_LIBS="/software/R/packages"  
  Rscript \$HOME/git/pergola/test/c_elegans_data_test/plot_speed_distribution.R --bed_file=${intersect_speed_motion}
  """
}

// Creating motion results folder
result_dir_plots_motion_speed = file("$baseDir/plots_motion_speed")

result_dir_plots_motion_speed.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_plots_motion_speed"
}

plots_speed_motion.subscribe {   
  it.copyTo( result_dir_plots_motion_speed.resolve ( it.name ) )
}

/*
// map transform one thing into another
// we do not need it, because the declaration is implicit
// subscribed does nothing because it is like a for but you do not transform anything
bed_intersect_speed_motion2plot = bed_intersect_speed_motion2p.map { it ->
	def pattern = it[4] =~/^file_worm_(.*)\.csv$/
	def motion_dir = pattern[0][1]	
	//println "=======" + it[1] + "++++" + it[2] + "++++" + it[4]
	println "=======******" + motion_dir	
	//println "=======******" + it[0] + "\n" + it[1] + "\n" + it[2] + "\n" + it[3] + "\n" + it[4] + "\n" + motion_dir	
	[ it[0], it[1], it[2], it[3], it[4], motion_dir ] 
}

*/

/*
# Esto lo puedo hacer despues porque solo tengo que ir a la carpeta donde este de intersection file y hacer los plots 

worm_strains = ['575_JU440', 'N2', 'flp-19ok2460', 'flp-20ok2964', 'ins-15ok3444I', 'nlp-14tm1880X' ]
*/
	
// Creating results folder
result_dir_GB = file("$baseDir/results_GB")

result_dir_GB.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_GB"
}

out_fasta.subscribe {   
  fasta_file = it[0]
  //fasta_file.copyTo ( it[1] + ".fa" )
  fasta_file.copyTo( result_dir_GB.resolve ( it[1] + ".fa" ) )
}

bed_speed_no_nas.subscribe {   
  bed_file = it[0]
  //bed_file.copyTo ( it[1] + "." + it[2] + ".GB.bed" )
  bed_file.copyTo ( result_dir_GB.resolve ( it[1] + "." + it[2] + ".GB.bed" ) )
}

bedGraph_speed_no_nas.subscribe {   
  bedGraph_file = it[0]
  //bedGraph_file.copyTo ( it[1] + "." + it[2] + ".GB.bedGraph" )
  bedGraph_file.copyTo (result_dir_GB.resolve ( it[1] + "." + it[2] + ".GB.bedGraph" ) )
}

// Creating mean results folder
result_dir_mean = file("$baseDir/results_mean")

result_dir_mean.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_mean"
}

// Creating intersect results folder
result_dir_intersect = file("$baseDir/results_intersect")

result_dir_intersect.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_intersect"
}

// Creating motion results folder
result_dir_motion_GB = file("$baseDir/results_motion_GB")

result_dir_motion_GB.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_motion_GB"
}

//set name_file, 'tr*.bed', name_file_motion into bed_motion, bed_motion_wr
bed_motion_wr.subscribe {
  //println ".......******************    0      " + it[0] + "." + it[2] + ".motion.bed"
  it[1].copyTo ( result_dir_motion_GB.resolve ( it[0] + it[2] + ".motion.bed" ))
}

//set '*.mean.bed', body_part, mat_file_speed, mat_motion_file, name_file_motion into bed_mean_speed_motion
bed_mean_speed_motion.subscribe {
  bed_mean_file = it[0]
  bed_mean_file.copyTo ( result_dir_mean.resolve ( it[1] + "." + it[2] + "." + it[4] + ".mean.bed" ) )
}

bed_intersect_speed_motion.subscribe {
  bed_int_file = it[0]
  bed_int_file.copyTo ( result_dir_intersect.resolve ( it[1] + "." + it[2] + "." + it[4] + ".intersect.bed" ) )
}

bedGr_mean_speed_motion.subscribe {
  bedGr_mean_file = it[0]
  bedGr_mean_file.copyTo ( result_dir_mean.resolve ( it[1] + "." + it[2] + "." + it[4] + ".mean.bedGraph" ) )
}

// Turns 
process get_turns {
  
  input:
  set file ('file_worm'), val (name_file_worm) from mat_files_turns
  
  output: 
  set name_file_worm, '*.csv' into turns_files, turns_files_cp
    
  script:
  println "Matlab file containing worm behavior processed: $file_worm"

  """
  $HOME/git/pergola/test/c_elegans_data_test/extract_worm_turns.py -i \"$file_worm\"
  """
}

turn_files_flat = turns_files.map { name_mat, turn_f ->
        turn_f.collect {            
            [ it, name_mat, it.name ]
        }
    }
    .flatMap()
    
// Files used for motion can be used for turns (same format)
map_turn_path = "$HOME/git/pergola/test/c_elegans_data_test/worms_motion2p.txt"
turn_motion=file(map_turn_path)

process turns_to_pergola {
  input:
  set file ('turn_file'), val (name_file), val (name_file_turn) from turn_files_flat
  set worms_turn2p from turn_motion
  
  output:
  set name_file, 'tr*.bed', name_file_turn into bed_turn, bed_turn_wr
  set name_file, 'tr*.bedGraph', name_file_turn into bedGraph_turn
  
  """
  pergola_rules.py -i $turn_file -m $worms_turn2p -nt
  pergola_rules.py -i $turn_file -m $worms_turn2p -f bedGraph -w 1 -nt 
  """
} 

// Calculate mean speed of the two types of turns
// TO DO
// Calculate mean speed of the two types of turns during forward, backward and paused motion, regardless of 

// Igual puedo utilizar lo anterior para hacer esto o anyadirlo en lo de antes
bed_speed_turn = bed_speed_no_track_line_turns
	.spread(bed_turn)
	.filter { it[0] == it[3] }

process intersect_speed_turn {
	input:
	set val (mat_file_speed), val (body_part), file ('bed_speed_no_tr'), val (mat_turn_file), file ('turn_file'), val (name_file_turn) from bed_speed_turn
	file bed2pergola from map_bed_pergola_turn.first()
	
	output:
	set '*.mean.bed', body_part, mat_file_speed, mat_turn_file, name_file_turn into bed_mean_speed_turn	
	set '*.mean.bedGraph', body_part, mat_file_speed, mat_turn_file, name_file_turn into bedGr_mean_speed_turn
	set '*.intersect.bed', body_part, mat_file_speed, mat_turn_file, name_file_turn into bed_intersect_speed_turn, bed_intersect_speed_turn2p
	
	"""
	$HOME/git/pergola/test/c_elegans_data_test/celegans_speed_i_motion.py -s $bed_speed_no_tr -m $turn_file -b $bed2pergola	
	"""
}

//Some turns files are empty, I add a fake interval inside extract_worm_turns.py

// Creating turns results folder

// Creating mean results folder
result_dir_mean_turn = file("$baseDir/results_mean_turn")

result_dir_mean_turn.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_mean_turn"
}

bed_mean_speed_turn.subscribe {
  bed_mean_file = it[0]
  bed_mean_file.copyTo ( result_dir_mean_turn.resolve ( it[1] + "." + it[2] + "." + it[4] + ".mean.bed" ) )
}

bedGr_mean_speed_turn.subscribe {
  bedGr_mean_file = it[0]
  bedGr_mean_file.copyTo ( result_dir_mean_turn.resolve ( it[1] + "." + it[2] + "." + it[4] + ".mean.bedGraph" ) )
}

// Creating motion results folder
result_turn_GB = file("$baseDir/results_turn_periods")

result_turn_GB.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_turn_GB"
}

//set name_file, 'tr*.bed', name_file_turn into bed_turn, bed_turn_wr
bed_turn_wr.subscribe {
  //println ".......******************    0      " + it[0] + "." + it[2] + ".turn.bed"
  it[1].copyTo ( result_turn_GB.resolve ( it[0] + it[2] + ".turn.bed" ))
}

// Creating intersect results folder
result_dir_intersect_turns = file("$baseDir/results_intersect_turns")

result_dir_intersect_turns.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_intersect_turns"
}

bed_intersect_speed_turn.subscribe {
  bed_int_file = it[0]
  bed_int_file.copyTo ( result_dir_intersect_turns.resolve ( it[1] + "." + it[2] + "." + it[4] + ".intersect.bed" ) )
}

// Channel containning body part, strain, type of turn
bed_intersect_speed_turn_plot = bed_intersect_speed_turn2p.collectFile(newLine: false) { 
	def name = it[1] + "_" + it[3].split("_on_")[0] + "_" + it[4].tokenize(".")[1]
	[ name, it[0].text ] 
}

process plot_distro_turns {
  input:
  file intersect_speed_turn from bed_intersect_speed_turn_plot
  
  output:
  set '*.png' into plots_speed_turn
    
  script:
  println ">>>>>>>>>>>>>>>: $intersect_speed_turn"
  	
  """  
  export R_LIBS="/software/R/packages"
  Rscript \$HOME/git/pergola/test/c_elegans_data_test/plot_speed_distribution.R --bed_file=${intersect_speed_turn}
  """
}

result_dir_plots_turn_speed = file("$baseDir/plots_turn_speed")

result_dir_plots_turn_speed.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_plots_turn_speed"
}

plots_speed_turn.subscribe {   
  it.copyTo( result_dir_plots_turn_speed.resolve ( it.name ) )
}

