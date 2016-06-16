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
 * Process mat files downloaded from the DB to extract new locomotion phenotypes characterized 
 * in the original publication for trp channels KO
 * TODO  explain what pergola does
 */    

params.path_files = "$baseDir/data/"

log.info "C. elegans trp locomotion phenotypes - N F  ~  version 0.1"
log.info "======================================================="
log.info "c. elegans case data       : ${params.path_files}"
log.info "c. elegans ctrl data       : ${params.ctrl_path_files}"
log.info "Tag for results folders    : ${params.tag_results}"
log.info "\n"

N2_ctrl_path = "${params.ctrl_path_files}*.mat"
N2_ctrl_files = Channel.fromPath(N2_ctrl_path)

case_files_path = "${params.path_files}*.mat"
case_files = Channel.fromPath(case_files_path)

params.tag_results = "strain"
tag_res = "${params.tag_results}"

/*
 * Creates a channel with file content and name of input file without spaces
 * Substitutes spaces by "_" in file name
 */ 
ctrl_files_name = N2_ctrl_files.flatten().map { ctrl_files_file ->      
	def content = ctrl_files_file
	def name = ctrl_files_file.name.replaceAll(/ /,'_')
	def tag = "ctrl_worms"
    [ content, name, tag ]
}

case_files_name = case_files.flatten().map { case_files_file ->      
	def content = case_files_file
	def name = case_files_file.name.replaceAll(/ /,'_')
	def tag = "case_worms"
    [ content, name, tag ]
}

// Files tagged joined in a single channel
mat_files_name = case_files_name.mix ( ctrl_files_name )

mat_files_name.into { mat_files_loc; mat_files_motion }

/*
 * Get locomotion phenotypic features from mat files
 */ 
process get_feature {
	container 'ipython/scipyserver'
  	
  	input:
  	set file ('file_worm'), val (name_file_worm), val (exp_group) from mat_files_loc
  
  	output:  
  	set '*_speed.csv', name_file_worm, exp_group into locomotions_files, locomotion_files_wr
  	
  	script:
  	println "Matlab file containing worm behavior processed: $name_file_worm"

  	"""
  	extract_worm_speed.py -i $file_worm
  	"""
}

/*
 * Transform locomotion files into bed format files
 */ 

map_speed_path = "$baseDir/data/worms_speed2p.txt" 

map_speed=file(map_speed_path)
//body_parts =  ['head', 'headTip', 'midbody', 'tail', 'tailTip']
body_parts =  ['head', 'headTip', 'midbody', 'tail', 'tailTip', 'foraging_speed', 'tail_motion', 'crawling']

process feature_to_pergola {
	container 'joseespinosa/pergola:celegans'
  
  	input:
  	set file ('speed_file'), val (name_file), val (exp_group) from locomotions_files 
  	file worms_speed2p from map_speed
  	each body_part from body_parts
  
  	output: 
  	set '*.no_na.bed', body_part, name_file into bed_loc_no_nas
  	set '*.no_na.bedGraph', body_part, name_file into bedGraph_loc_no_nas
  	
  	set name_file, body_part, '*.no_tr.bed', exp_group into bed_loc_no_track_line, bed_loc_no_track_line_cp
  	set name_file, body_part, '*.no_tr.bedGraph', exp_group into bedGraph_loc_no_track_line
  	
  	set '*.fa', body_part, name_file, val(exp_group) into out_fasta  	
  	
  	"""  	
  	cat $worms_speed2p | sed 's/behavioural_file:$body_part > pergola:dummy/behavioural_file:$body_part > pergola:data_value/g' > mod_map_file
  	pergola_rules.py -i $speed_file -m mod_map_file
  	pergola_rules.py -i $speed_file -m mod_map_file -f bedGraph -w 1
  	
  	# This is done just because is easy to see in the display of the genome browsers
  	cat tr*.bed | sed 's/track name=\"1_a\"/track name=\"${body_part}\"/g' > bed_file.tmp
  	
  	cat tr*.bedGraph | sed 's/track name=\"1_a\"/track name=\"${body_part}\"/g' > bedGraph_file.tmp
  	
  	# delete values that were assigned as -10000 to skip na of the original file
  	# to avoid problems if a file got a feature with a feature always set to NA I add this code (short files for examples)
  	cat bed_file.tmp | grep -v "\\-10000" > ${name_file}".no_na.bed"  
  	cat ${name_file}".no_na.bed" | grep -v "track name" > ${name_file}.no_tr.bed || echo -e "chr1\t0\t100\t.\t-10000\t+\t0\t100\t135,206,250" > ${name_file}".no_tr.bed"
  	rm bed_file.tmp
  	
  	cat bedGraph_file.tmp | grep -v "\\-10000" > ${name_file}".no_na.bedGraph"  
  	cat ${name_file}".no_na.bedGraph" | grep -v "track name" > ${name_file}".no_tr.bedGraph" || echo -e echo -e "chr1\t0\t100\t1" > ${name_file}".no_tr.bedGraph"
  	rm bedGraph_file.tmp 
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
  	println "Matlab file containing worm motion processed: $name_file_worm"

  	"""
  	extract_worm_motion.py -i \"$file_worm\"
  	"""
}

//motion_files_wr.subscribe { println (it) }

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
	container 'cbcrg/pergola:latest'  
  
  	input:
  	set file ('motion_file'), val (name_file), val (name_file_motion), val (motion) from motion_files_flat
  	set worms_motion_map from map_motion
    
  	output:
  	set name_file, 'tr*.bed', name_file_motion into bed_motion, bed_motion_wr
  	  	
  	"""
  	pergola_rules.py -i $motion_file -m $worms_motion_map
  	cat tr_1_dt_${motion}.bed | sed 's/track name=\"1_a\"/track name=\"${motion}\"/g' > tr_1_dt_${motion}.bed.tmp
  	cat tr_1_dt_${motion}.bed.tmp | grep -v 'track name' > tr_1_dt_${motion}.bed
  	rm tr_1_dt_${motion}.bed.tmp  	
  	"""
} 

map_bed_path = "$baseDir/data/bed2pergola.txt"
map_bed_pergola = Channel.fromPath(map_bed_path)
map_bed_pergola.into { map_bed_pergola_loc; map_bed_pergola_bG; map_bed_pergola_turn}

/*
 * Filter is used to delete pairs that do not come from the same original mat file
 */
//bed_motion.subscribe { println ("=========" + it) }  
//bed_loc_no_track_line.subscribe { println ("********" + it) }

bed_loc_motion = bed_loc_no_track_line
	.spread (bed_motion)
	.filter { it[0] == it[4] }

/*
 * Using bedtools intersect motion with phenotypic feature bed files
 */
process intersect_loc_motion {
	container 'cbcrg/pergola:latest'
	
	input:
	set val (mat_file_loc), val (pheno_feature), file ('bed_loc_no_tr'), val (exp_group), val (mat_motion_file), file (motion_file), val (name_file_motion), val (direction) from bed_loc_motion
	file bed2pergola from map_bed_pergola_loc.first()
	
	output:
	set '*.mean.bed', pheno_feature, mat_file_loc, mat_motion_file, name_file_motion, exp_group into bed_mean_speed_motion	
	set '*.mean.bedGraph', pheno_feature, mat_file_loc, mat_motion_file, name_file_motion, exp_group into bedGr_mean_loc_motion
	set '*.intersect.bed', pheno_feature, mat_file_loc, mat_motion_file, name_file_motion, exp_group into bed_intersect_loc_motion, bed_intersect_loc_motion2p, bed_intersect_l_m
	set '*.mean_file.bed', pheno_feature, mat_file_loc, mat_motion_file, name_file_motion, exp_group into mean_intersect_loc_motion

	"""
	celegans_feature_i_motion.py -p $bed_loc_no_tr -m $motion_file -b $bed2pergola
	"""
}

/*
 * Intersected bed files transformed to bedgraph format for heatmaps visualizations
 */
process inters_to_bedGr {
	container 'cbcrg/pergola:latest'
	
	input:
	set file (file_bed_inters), val (pheno_feature), val (mat_file_loc), val (mat_motion_file), val (name_file_motion), val (exp_group) from bed_intersect_l_m
	file bed2pergola from map_bed_pergola_bG.first()
	
	output:
	set '*.bedGraph', pheno_feature, mat_file_loc, mat_motion_file, name_file_motion, exp_group into bedGraph_intersect_loc_motion
	
	"""		
	if [ -s $file_bed_inters ]
	then		
		pergola_rules.py -i $file_bed_inters -m $bed2pergola -nh -s chrm start end nature value strain start_rep end_rep color -f bedGraph -w 1
	else
		touch tr_chr1_d.bedGraph
    fi 	
	"""
}


/*
 * Grouping (collect) bed files in order to plot the distribution by strain, motion direction and body part 
 */
bed_intersect_loc_motion_plot = bed_intersect_loc_motion2p.collectFile(newLine: false, sort:'none') { 
	def name = it[3].split("_on_")[0] + "." + it[1] + "." +  it[4].tokenize(".")[1] + "." +  it[5]
	[ name, it[0].text]	
}.map {  
	def strain =  it.name.split("\\.")[0]	
	def pheno_feature =  it.name.split("\\.")[1]	
	def direction =  it.name.split("\\.")[2]
	def exp_group =  it.name.split("\\.")[3]
	def name_file = it.name.replaceAll('.case_worms', '').replaceAll('.ctrl_worms', '')

 	[ it, strain, pheno_feature, direction, name_file, exp_group ]
}

/*
 * Grouping (collect) bed files in order to plot the distribution by mean of means "boxplot"
 */
 /*
//Not implemented by the moment
mean_intersect_loc_motion_plot = mean_intersect_loc_motion.collectFile(newLine: false, sort:'none') { 
	def name = it[3].split("_on_")[0] + "." + it[1] + "." +  it[4].tokenize(".")[1] + "." +  it[5]
	[ name, it[0].text]	
}.map {  
	def strain =  it.name.split("\\.")[0]	
	def pheno_feature =  it.name.split("\\.")[1]	
	def direction =  it.name.split("\\.")[2]
	def exp_group =  it.name.split("\\.")[3]
	def name_file = it.name.replaceAll('.case_worms', '').replaceAll('.ctrl_worms', '')

 	[ it, strain, pheno_feature, direction, name_file, exp_group ]
}
*/

/*
 * Tagging files for plotting
 */
process tag_bed_mean_files {
	input: 
	set file ('bed_file'), val (strain), val (pheno_feature), val (direction), val (strain_beh_dir), val (exp_group) from bed_intersect_loc_motion_plot
	
	output:
	set '*.bed', strain, pheno_feature, direction, exp_group into bed_tagged_for_case, bed_tagged_for_ctrl
	
	"""
	# Adds to the bed file a tag for being used inside the R dataframe
	awk '{ print \$0, \"\\t$pheno_feature\\t$direction\\t$strain\" }' ${bed_file} > ${strain_beh_dir}.bed  
	"""
}

case_bed_tagged = bed_tagged_for_case.filter { it[4] == 'case_worms' }
ctrl_bed_tagged = bed_tagged_for_ctrl.filter { it[4] == 'ctrl_worms' }

/*
 * Matching the control group for each strain in the data set
 */
case_ctrl_bed = case_bed_tagged
	.spread (ctrl_bed_tagged)
	//same feature and motion direction
	.filter { it[2] == it[7] && it[3] == it[8] }
	.map { [ it[0], it[1], it[2], it[3], it[5] ] }	

/*
 * Plots the distribution of bed containing all intervals by strain, motion and body part compairing the distro of ctrl and case strain
 */
process plot_distro {
	container 'joseespinosa/docker-r-ggplot2:v0.1'

  	input:
  	set file (intersect_feature_motion), strain, pheno_feature, direction, file (intersect_feature_motion_ctrl) from case_ctrl_bed
  
  	output:
  	set '*.png', strain, pheno_feature, direction into plots_pheno_feature_case_ctrl
    
  	"""
  	plot_pheno_feature_distro.R --bed_file=${intersect_feature_motion} --bed_file_ctrl=${intersect_feature_motion_ctrl}  	
  	"""
}

result_dir_distro_ctrl_case = file("$baseDir/plots_distro_ctrl_case_$tag_res")
 
result_dir_distro_ctrl_case.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_distro_ctrl_case"
}

plots_pheno_feature_case_ctrl.subscribe {		
	it[0].copyTo( result_dir_distro_ctrl_case.resolve ( it[1] + "." + it[2] + "." + it[3] + ".png" ) )	   
}

/*
 * Creating folder to keep bed files to visualize data
 */
result_dir_GB = file("$baseDir/results_GB_$tag_res")

result_dir_GB.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_GB"
} 

out_fasta.subscribe {  
  fasta_file = it[0]
  fasta_file.copyTo( result_dir_GB.resolve ( it[2] + ".fa" ) )
}

result_dir_bed = file("$baseDir/results_bed_$tag_res")

result_dir_bed.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_bed"
} 

bed_loc_no_nas.subscribe {   
  bed_file = it[0]
  bed_file.copyTo ( result_dir_bed.resolve ( it[1] + "." + it[2] + ".GB.bed" ) )
}

result_dir_bedGraph = file("$baseDir/results_bedGraph_$tag_res")

result_dir_bedGraph.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_bedGraph"
} 

bedGraph_loc_no_nas.subscribe {   
  bedGraph_file = it[0]
  bedGraph_file.copyTo (result_dir_bedGraph.resolve ( it[1] + "." + it[2] + ".GB.bedGraph" ) )
}

bed_motion_wr.subscribe {
  bed_file = it[1]
  bed_file.copyTo ( result_dir_bed.resolve ( it[0] + it[2] + ".GB.bed" ) )
}

bed_intersect_loc_motion.subscribe {   
  bed_file = it[0]
  bed_file.copyTo ( result_dir_bed.resolve ( "intersect." + it[1] + "." + it[3] + "." + it[4] + ".GB.bed" ) )
}

bedGraph_intersect_loc_motion.subscribe {
  bedGraph_file = it[0]
  bedGraph_file.copyTo ( result_dir_bedGraph.resolve ( "intersect." + it[1] + "." + it[3] + "." + it[4] + ".bedGraph" ) )
}
