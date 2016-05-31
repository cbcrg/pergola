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
 * Jose Espinosa-Carrasco. CB/CSN-CRG. April 2016
 *
 * Wormbehavior DB (http://wormbehavior.mrc-lmb.cam.ac.uk/) processed by pergola for paper
 * Process mat files downloaded from the DB to extract periods of motion (forward, backward, 
 * and turns) in order to intersect them with speed during this periods using pergola
 */    


params.path_files = "$baseDir/data/"

log.info "C. elegans speed vs motion  - N F  ~  version 0.1"
log.info "========================================="
log.info "c. elegans data    : ${params.path_files}"
log.info "c. elegans tag     : ${params.tag_results}"
log.info "\n"

mat_files_path = "${params.path_files}*.mat"
mat_files = Channel.fromPath(mat_files_path)
params.tag_results = ""
tag_res = "${params.tag_results}"

/*
 * Creates a channel with file content and name of input file without spaces
 */ 
mat_files_name = mat_files.flatten().map { mat_files_file ->      
	def content = mat_files_file
	def name = mat_files_file.name.replaceAll(/ /,'_')
    [ content, name ]
}

mat_files_name.into { mat_files_speed; mat_files_motion; mat_files_turns}

/*
 * Get speed from mat files
 */ 
process get_speed {
	container 'ipython/scipyserver'
  
  	input:
  	set file ('file_worm'), val (name_file_worm) from mat_files_speed
  
  	output:  
  	set '*_speed.csv', name_file_worm into speed_files, speed_files_wr
     
  	script:
  	println "Matlab file containing worm behavior processed: $name_file_worm"

  	"""
  	extract_worm_speed.py -i $file_worm
  	"""
}

/*
 * Transform speed files into bed format files
 */ 
 "$baseDir/tutorial/data/*.fa"
 
map_speed_path = "$baseDir/data/worms_speed2p.txt" 

map_speed=file(map_speed_path)

body_parts =  ['head', 'headTip', 'midbody', 'tail', 'tailTip']

process speed_to_pergola {
	container 'joseespinosa/pergola:celegans'
  
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

/*
 * Changing track name and processing periods with NA that are annotated as -10000 by extract_worm_speed.py 
 */ 
process zeros_bed_and_bedGraph {
	container 'joseespinosa/pergola:celegans'
	
  	input:
  	set file ('bed_file'), val(body_part), val(name_file) from bed_speed
  	set file ('bedGraph_file'), val(body_part), val(name_file) from bedGraph_speed
  	
  	output:
  	set '*.no_na.bed', body_part, name_file into bed_speed_no_nas
  	set '*.no_na.bedGraph', body_part, name_file into bedGraph_speed_no_nas
  
  	set name_file, body_part, '*.no_tr.bed' into bed_speed_no_track_line, bed_speed_no_track_line_cp, bed_speed_no_track_line_turns
  	set name_file, body_part, '*.no_tr.bedGraph' into bedGraph_speed_no_track_line
   
  	"""
  	cat $bed_file | sed 's/track name=\"1_a\"/track name=\"${body_part}_speed\"/g' > ${bed_file}".tmp"
  	cat ${bed_file}".tmp" | grep -v "\\-10000" > ${bed_file}${name_file}".no_na.bed"  
  	cat ${bed_file}${name_file}".no_na.bed" | grep -v "track name" > ${bed_file}".no_tr.bed" || echo -e "chr1\t0\t100\t.\t-10000\t+\t0\t100\t135,206,250" > ${bed_file}".no_tr.bed"
  
  	cat $bedGraph_file | sed 's/track name=\"1_a\"/track name=\"${body_part}_speed\"/g' > ${bedGraph_file}".tmp"
  	cat ${bedGraph_file}".tmp" | grep -v "\\-10000" > ${bedGraph_file}".no_na.bedGraph"  
  	cat ${bedGraph_file}".no_na.bedGraph" | grep -v "track name" > ${bedGraph_file}".no_tr.bedGraph" || echo -e echo -e "chr1\t0\t100\t1" > ${bedGraph_file}".no_tr.bedGraph" 
  	"""			
}

/*
 * Transform motion intervals from mat files (forward, backward and paused)
 */ 
process get_motion {
	container 'ipython/scipyserver'
	  
  	input:
  	set file ('file_worm'), val (name_file_worm) from mat_files_motion
  
  	output: 
  	set name_file_worm, '*.csv' into motion_files, motion_files_wr
    
  	script:
  	println "Matlab file containing worm behavior processed: $file_worm"

  	"""
  	extract_worm_motion.py -i \"$file_worm\"
  	"""
}

/*
 * From one mat file 3 motion (forward, paused, backward) files are obtained
 * A channel is made with matfile1 -> forward
 *                        matfile1 -> backward
 *                        matfile1 -> paused
 *                        matfile2 -> forward ...
 */
motion_files_flat_p = motion_files.map { name_mat, motion_f ->
        motion_f.collect { 
        	def motion = it.name.split("\\.")[1]   
            [ it, name_mat, it.name, motion ]
        }
    }
    .flatMap()

motion_files_flat_p.into { motion_files_flat; motion_files_flat_wr }

map_motion_path = "$baseDir/data/worms_motion2p.txt"
map_motion = file(map_motion_path)

process motion_to_pergola {
	container 'joseespinosa/pergola:celegans'  
  
  	input:
  	set file ('motion_file'), val (name_file), val (name_file_motion), val (motion) from motion_files_flat
  	set worms_motion2p from map_motion
    
  	output:
  	set name_file, 'tr*.bed', name_file_motion into bed_motion, bed_motion_wr, bed_motion_turns
  	//set name_file, 'tr*.bedGraph', name_file_motion into bedGraph_motion
      
  	//pergola_rules.py -i $motion_file -m $worms_motion2p -f bedGraph -w 1
  	//cat tr_1_dt_a.bedGraph | sed 's/track name=\"1_a\"/track name=\"${motion}\"/g' > tr_1_dt_a.bedGraph.tmp
  	//cat tr_1_dt_a.bedGraph.tmp | grep -v 'track name' > tr_1_dt_a.bedGraph
  	
  	"""
  	pergola_rules.py -i $motion_file -m $worms_motion2p
  	cat tr_1_dt_${motion}.bed | sed 's/track name=\"1_a\"/track name=\"${motion}\"/g' > tr_1_dt_${motion}.bed.tmp
  	cat tr_1_dt_${motion}.bed.tmp | grep -v 'track name' > tr_1_dt_${motion}.bed  	
  	"""
} 

map_bed_path = "$baseDir/data/bed2pergola.txt"
map_bed_pergola = Channel.fromPath(map_bed_path)
map_bed_pergola.into { map_bed_pergola_speed; map_bed_pergola_turn}

/*
 * Filter is used to delete pairs that do not come from the same original mat file
 */
bed_speed_motion = bed_speed_no_track_line
	.spread (bed_motion)
	.filter { it[0] == it[3] }
	
process intersect_speed_motion {
	container 'joseespinosa/pergola:celegans'
	
	input:
	set val (mat_file_speed), val (body_part), file ('bed_speed_no_tr'), val (mat_motion_file), file ('motion_file'), val (name_file_motion), val (direction) from bed_speed_motion
	file bed2pergola from map_bed_pergola_speed.first()
	
	output:
	set '*.mean.bed', body_part, mat_file_speed, mat_motion_file, name_file_motion into bed_mean_speed_motion	
	set '*.mean.bedGraph', body_part, mat_file_speed, mat_motion_file, name_file_motion into bedGr_mean_speed_motion
	set '*.intersect.bed', body_part, mat_file_speed, mat_motion_file, name_file_motion into bed_intersect_speed_motion, bed_intersect_speed_motion2p
	set '*.intersect.bedGraph', body_part, mat_file_speed, mat_motion_file, name_file_motion into bedGraph_intersect_speed_motion
	
	"""
	celegans_speed_i_motion.py -s $bed_speed_no_tr -m $motion_file -b $bed2pergola
	"""
}

/*
 * Grouping (collect) bed files in order to plot the distribution by strain, motion direction and body part 
 */
bed_intersect_speed_motion_plot = bed_intersect_speed_motion2p.collectFile(newLine: false, sort:'none') { 
	def name = it[1] + "_" + it[3].split("_on_")[0] + "_" + it[4].tokenize(".")[1]
	//headTip_flp-19ok2460_paused	
	[ name, it[0].text ]
}

/*
 * Plots the distribution of bed containing all intervals by strain, motion and body part
 */
process plot_distro {
	container 'joseespinosa/docker-r-ggplot2:v0.1'

  	input:
  	file intersect_speed_motion from bed_intersect_speed_motion_plot
  
  	output:
  	set '*.png' into plots_speed_motion
    
  	script:
  	println ">>>>>>>>>>>>>>>: $intersect_speed_motion"
  	
  	"""
  	plot_speed_distribution.R --bed_file=${intersect_speed_motion}
  	"""
}

/*
 * Processing mat files in order to obtain intervals annotated as turns
 */

process get_turns {
	container 'ipython/scipyserver'
	
  	input:
  	set file ('file_worm'), val (name_file_worm) from mat_files_turns
  
  	output: 
  	set name_file_worm, '*.csv' into turns_files, turns_files_cp
    
  	script:
  	println "Matlab file containing worm behavior processed: $file_worm"

  	"""
  	extract_worm_turns.py -i \"$file_worm\"
  	"""
}

turn_files_flat = turns_files.map { name_mat, turn_f ->
        turn_f.collect {
        	def turn = it.name.split("\\.")[1]            
            [ it, name_mat, it.name ]
        }
    }
    .flatMap()

map_turn_path = "$baseDir/data/worms_motion2p.txt"
turn_motion=file(map_turn_path)

/*
 * Transforming turns files to bed format
 */
process turns_to_pergola {
	container 'joseespinosa/pergola:celegans'
	
  	input:
  	set file ('turn_file'), val (name_file), val (name_file_turn), val (turn) from turn_files_flat
  	set worms_turn2p from turn_motion
  
  	output:
  	set name_file, 'tr*.bed', name_file_turn into bed_turn, bed_turn_wr
  	//set name_file, 'tr*.bedGraph', name_file_turn into bedGraph_turn
  
  	//pergola_rules.py -i $turn_file -m $worms_turn2p -f bedGraph -w 1 -nt 
  
  	"""
  	pergola_rules.py -i $turn_file -m $worms_turn2p
  	cat tr_1_dt_a.bed | sed 's/track name=\"1_a\"/track name=\"${turn}\"/g' > tr_1_dt_a.bed.tmp
  	cat tr_1_dt_a.bed.tmp | grep -v 'track name' > tr_1_dt_a.bed  	
  	"""
} 


bed_speed_turn = bed_speed_no_track_line_turns
	.spread(bed_turn)
	.filter { it[0] == it[3] }

/*
 * Intersecting turns intervals with speed
 */
process intersect_speed_turn {
	container 'joseespinosa/pergola:celegans'
	
	input:
	set val (mat_file_speed), val (body_part), file ('bed_speed_no_tr'), val (mat_turn_file), file ('turn_file'), val (name_file_turn) from bed_speed_turn
	file bed2pergola from map_bed_pergola_turn.first()
	
	output:
	set '*.mean.bed', body_part, mat_file_speed, mat_turn_file, name_file_turn into bed_mean_speed_turn	
	set '*.mean.bedGraph', body_part, mat_file_speed, mat_turn_file, name_file_turn into bedGr_mean_speed_turn
	set '*.intersect.bed', body_part, mat_file_speed, mat_turn_file, name_file_turn into bed_intersect_speed_turn, bed_intersect_speed_turn2p
	
	"""
	celegans_speed_i_motion.py -s $bed_speed_no_tr -m $turn_file -b $bed2pergola	
	"""
}

/*
 * Plotting speed distribution during different types of turns
 */

/*
 * Channel containning body part, strain, type of turn
 */
bed_intersect_speed_turn_plot = bed_intersect_speed_turn2p.collectFile(newLine: false) { 
	def name = it[1] + "_" + it[3].split("_on_")[0] + "_" + it[4].tokenize(".")[1]
	[ name, it[0].text ] 
}

process plot_distro_turns {
	container 'joseespinosa/docker-r-ggplot2:v0.1'
  	input:
  	file intersect_speed_turn from bed_intersect_speed_turn_plot
  
  	output:
  	set '*.png' into plots_speed_turn
    
  	script:
  	println ">>>>>>>>>>>>>>>: $intersect_speed_turn"
  	
  	"""  
  	export R_LIBS="/software/R/packages"
  	plot_speed_distribution.R --bed_file=${intersect_speed_turn}
  	"""
}

/*
 * Creating folder to keep results
 */
result_dir_csv = file("$baseDir/results_csv$tag_res")

result_dir_csv.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_csv"
}

motion_files_flat_wr.subscribe {   
  csv_file = it[0]
  csv_file.copyTo( result_dir_csv.resolve (  it[1]  + "." + it[3] +  ".csv"  ) )
}

speed_files_wr.subscribe {   
  csv_file = it[0]  
  csv_file.copyTo( result_dir_csv.resolve ( it[0] + ".motion.csv" ) )
}

result_dir_GB = file("$baseDir/results_GB$tag_res")

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
result_dir_mean = file("$baseDir/results_mean$tag_res")

result_dir_mean.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_mean"
}

// Creating intersect results folder
result_dir_intersect = file("$baseDir/results_intersect$tag_res")

result_dir_intersect.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_intersect"
}

// Creating motion results folder
result_dir_motion_GB = file("$baseDir/results_motion_GB$tag_res")

result_dir_motion_GB.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_motion_GB"
}

bed_motion_wr.subscribe {
  it[1].copyTo ( result_dir_motion_GB.resolve ( it[0] + it[2] + ".motion.bed" ))
}

bed_mean_speed_motion.subscribe {
  bed_mean_file = it[0]
  bed_mean_file.copyTo ( result_dir_mean.resolve ( it[1] + "." + it[2] + "." + it[4] + ".mean.bed" ) )
}

bed_intersect_speed_motion.subscribe {
  bed_int_file = it[0]
  bed_int_file.copyTo ( result_dir_intersect.resolve ( it[1] + "." + it[2] + "." + it[4] + ".intersect.bed" ) )
}

bedGraph_intersect_speed_motion.subscribe {
  bedGraph_int_file = it[0]
  bedGraph_int_file.copyTo ( result_dir_intersect.resolve ( it[1] + "." + it[2] + "." + it[4] + ".intersect.bedGraph" ) )
}

bedGr_mean_speed_motion.subscribe {
  bedGr_mean_file = it[0]
  bedGr_mean_file.copyTo ( result_dir_mean.resolve ( it[1] + "." + it[2] + "." + it[4] + ".mean.bedGraph" ) )
}

result_dir_plots_motion_speed = file("$baseDir/plots_motion_speed$tag_res")

result_dir_plots_motion_speed.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_plots_motion_speed"
}

plots_speed_motion.subscribe {   
  it.copyTo( result_dir_plots_motion_speed.resolve ( it.name ) )
}

// Creating turns results folder

// Creating mean results folder
result_dir_mean_turn = file("$baseDir/results_mean_turn$tag_res")

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
result_turn_GB = file("$baseDir/results_turn_periods$tag_res")

result_turn_GB.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_turn_GB"
}

//set name_file, 'tr*.bed', name_file_turn into bed_turn, bed_turn_wr
bed_turn_wr.subscribe {
  it[1].copyTo ( result_turn_GB.resolve ( it[0] + it[2] + ".turn.bed" ))
}

// Creating intersect results folder
result_dir_intersect_turns = file("$baseDir/results_intersect_turns$tag_res")

result_dir_intersect_turns.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_intersect_turns"
}

bed_intersect_speed_turn.subscribe {
  bed_int_file = it[0]
  bed_int_file.copyTo ( result_dir_intersect_turns.resolve ( it[1] + "." + it[2] + "." + it[4] + ".intersect.bed" ) )
}

result_dir_plots_turn_speed = file("$baseDir/plots_turn_speed$tag_res")

result_dir_plots_turn_speed.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_plots_turn_speed"
}

plots_speed_turn.subscribe {   
  it.copyTo( result_dir_plots_turn_speed.resolve ( it.name ) )
}
