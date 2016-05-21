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
log.info "========================================="
log.info "c. elegans case data    : ${params.path_files}"
log.info "c. elegans ctrl data    : ${params.ctrl_path_files}"
log.info "\n"

case_files_path = "${params.path_files}*.mat"
case_files = Channel.fromPath(case_files_path)

N2_ctrl_path = "${params.ctrl_path_files}*.mat"
N2_ctrl_files = Channel.fromPath(N2_ctrl_path)

/*
 * Creates a channel with file content and name of input file without spaces
 * Substitutes spaces by "_" in file name
 */ 
case_files_name = case_files.flatten().map { case_files_file ->      
	def content = case_files_file
	def name = case_files_file.name.replaceAll(/ /,'_')
	def tag = "case_worms"
    [ content, name, tag ]
}

ctrl_files_name = N2_ctrl_files.flatten().map { ctrl_files_file ->      
	def content = ctrl_files_file
	def name = ctrl_files_file.name.replaceAll(/ /,'_')
	def tag = "ctrl_worms"
    [ content, name, tag ]
}

// Files joined in a single channel
mat_files_name = case_files_name.mix ( ctrl_files_name )

mat_files_name.into { mat_files_loc; mat_files_motion }

/*
 * Get locomotion phenotypic features from mat files
 */ 
process get_pheno_measure {
	container 'ipython/scipyserver'
  
  	input:
  	set file ('file_worm'), val (name_file_worm), val (exp_group) from mat_files_loc
  
  	output:  
  	set '*_loc.csv', name_file_worm, exp_group into locomotions_files, locomotion_files_wr
     
  	script:
  	println "Matlab file containing worm behavior processed: $name_file_worm"

  	"""
  	extract_trp_features.py -i $file_worm  	
  	"""
}

/*
 * Transform locomotion files into bed format files
 */ 

map_features_path = "$baseDir/data/trp_features_map.txt" 

map_features = file(map_features_path)

phenotypic_features =  ['foraging_speed', 'tail_motion', 'crawling']

process locomotion_to_pergola {
	container 'cbcrg/pergola:latest'
  
  	input:
  	set file ('loc_file'), val (name_file), val (exp_group) from locomotions_files
  	file map_features2p from map_features
  	each pheno_feature from phenotypic_features
  
  	output: 
  	set '*.no_na.bed', pheno_feature, name_file into bed_loc_no_nas
  	set '*.no_na.bedGraph', pheno_feature, name_file into bedGraph_loc_no_nas
  	
  	set name_file, pheno_feature, '*.no_tr.bed', exp_group into bed_loc_no_track_line, bed_loc_no_track_line_cp, bed_loc_no_track_line_turns
  	set name_file, pheno_feature, '*.no_tr.bedGraph', exp_group into bedGraph_loc_no_track_line
  	
  	set '*.fa', pheno_feature, name_file, val(exp_group) into out_fasta
  
  	"""  
  	cat $map_features2p | sed 's/behavioural_file:$pheno_feature > pergola:dummy/behavioural_file:$pheno_feature > pergola:data_value/g' > feat_map_file
  	pergola_rules.py -i $loc_file -m feat_map_file
  	pergola_rules.py -i $loc_file -m feat_map_file -f bedGraph -w 1 
  	
  	# This is done just because is easy to see in the display of the genome browsers
  	cat tr*.bed | sed 's/track name=\"1_a\"/track name=\"${pheno_feature}\"/g' > bed_file.tmp
  	
  	cat tr*.bedGraph | sed 's/track name=\"1_a\"/track name=\"${pheno_feature}\"/g' > bedGraph_file.tmp
  	
  	# delete values that were assigned as -10000 to skip na of the original file
  	# to avoid problems if a file got a feature with a feature always set to NA I add this code (short files for examples)
  	cat bed_file.tmp | grep -v "\\-10000" > ${name_file}".no_na.bed"  
  	cat ${name_file}".no_na.bed" | grep -v "track name" > ${name_file}.no_tr.bed || echo -e "chr1\t0\t100\t.\t-10000\t+\t0\t100\t135,206,250" > ${name_file}".no_tr.bed.no_tr.bed"
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
  	println "Matlab file containing worm behavior processed: $file_worm"

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
map_bed_pergola.into { map_bed_pergola_loc; map_bed_pergola_turn}

/*
 * Filter is used to delete pairs that do not come from the same original mat file
 */
//bed_motion.subscribe { println ("=========" + it) }  
//bed_loc_no_track_line.subscribe { println ("********" + it) }

bed_loc_motion = bed_loc_no_track_line
	.spread (bed_motion)
	.filter { it[0] == it[4] }

//bed_loc_motion.subscribe { println ("=========" + it) }

process intersect_loc_motion {
	container 'cbcrg/pergola:latest'
	
	input:
	set val (mat_file_loc), val (pheno_feature), file ('bed_loc_no_tr'), val (exp_group),  val (mat_motion_file), file (motion_file), val (name_file_motion), val (direction) from bed_loc_motion
	file bed2pergola from map_bed_pergola_loc.first()
	
	output:
	set '*.mean.bed', pheno_feature, mat_file_loc, mat_motion_file, name_file_motion, exp_group into bed_mean_speed_motion	
	set '*.mean.bedGraph', pheno_feature, mat_file_loc, mat_motion_file, name_file_motion, exp_group into bedGr_mean_loc_motion
	set '*.intersect.bed', pheno_feature, mat_file_loc, mat_motion_file, name_file_motion, exp_group into bed_intersect_loc_motion, bed_intersect_loc_motion2p
	set '*.mean_file.bed', pheno_feature, mat_file_loc, mat_motion_file, name_file_motion, exp_group into mean_intersect_loc_motion
	
	"""
	celegans_feature_i_motion.py -p $bed_loc_no_tr -m $motion_file -b $bed2pergola
	"""
}

/*
 * Grouping (collect) bed files in order to plot the distribution by strain, motion direction and body part 
 */
//bed_intersect_loc_motion2p.subscribe { println ( "@@@@@@@@@" + it[3].split("_on_")[0] + "." + it[1] + "." +  it[4].tokenize(".")[1] ) }
bed_intersect_loc_motion_plot = bed_intersect_loc_motion2p.collectFile(newLine: false, sort:'none') { 
	def name = it[3].split("_on_")[0] + "." + it[1] + "." +  it[4].tokenize(".")[1]
	[ name, it[0].text ]	
}.map { 
	def strain =  it.name.split("\\.")[0]	
	def pheno_feature =  it.name.split("\\.")[1]	
	def direction =  it.name.split("\\.")[2]
 	[ it, strain, pheno_feature, direction, it.name ]
}

//bed_intersect_loc_motion_plot.subscribe { println ( it ) }
 
/*
 * Tagging files for plotting
 */
process tag_bed_files {
	input: 
	set file ('bed_file'), val (strain), val (pheno_feature), val (direction), val (strain_beh_dir) from bed_intersect_loc_motion_plot
	
	output:
	set '*.bed', strain, pheno_feature, direction into bed_tagged
	
	"""
	# Adds to the bed file a tag for being used inside the R dataframe
	awk '{ print \$0, \"\\t$pheno_feature\\t$direction\" }' ${bed_file} > ${strain_beh_dir}.bed  
	"""
}

/*
 * Plots the distribution of bed containing all intervals by strain, motion and body part
 */
process plot_distro {
	container 'joseespinosa/docker-r-ggplot2:v0.1'

  	input:
	set file (intersect_feature_motion), strain, pheno_feature, direction from bed_tagged
  
  	output:
  	set '*.png', strain, pheno_feature, direction into plots_pheno_feature
    
  	"""
  	#plot_pheno_feature_distribution_grid.R --bed_file=${intersect_feature_motion}  	
  	plot_pheno_feature_distribution.R --bed_file=${intersect_feature_motion}
  	"""
}

/*
 * Folder to keep plots
 */
result_dir_pheno_features = file("$baseDir/plots_pheno_features")
 
result_dir_pheno_features.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_pheno_features"
}

plots_pheno_feature.subscribe {		
	it[0].copyTo( result_dir_pheno_features.resolve ( it[1] + "." + it[2] + "." + it[3] + ".png" ) )	   
}

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

/*
 * Tagging files for plotting
 */
process tag_bed_mean_files {
	input: 
	set file ('bed_file'), val (strain), val (pheno_feature), val (direction), val (strain_beh_dir), val (exp_group) from mean_intersect_loc_motion_plot
	
	output:
	set '*.bed', strain, pheno_feature, direction, exp_group into bed_tagged_for_case, bed_tagged_for_ctrl
	
	"""
	# Adds to the bed file a tag for being used inside the R dataframe
	awk '{ print \$0, \"\\t$pheno_feature\\t$direction\\t$strain\" }' ${bed_file} > ${strain_beh_dir}.bed  
	"""
}

case_bed_tagged = bed_tagged_for_case.filter { it[4] == 'case_worms' }
ctrl_bed_tagged = bed_tagged_for_ctrl.filter { it[4] == 'ctrl_worms' }

//case_bed_tagged.subscribe { println "***** case **" + it }
//ctrl_bed_tagged.subscribe { println "***** ctrl **" + it }

/*
 * Matching the control group for each strain in the data set
 */
case_ctrl_bed = case_bed_tagged
	.spread (ctrl_bed_tagged)
	.filter { it[2] == it[7] && it[3] == it[8] }
	.map { [ it[0], it[1], it[2], it[3], it[5] ] }	
	
//case_ctrl_bed.subscribe { println ( it[1] + it[2] + it[3] + it[6]+ it[7]+ it[8] ) }				
//case_ctrl_bed.subscribe { println ( it ) }	

process plot_mean_distro {
	container 'joseespinosa/docker-r-ggplot2:v0.1'

  	input:
	set file (intersect_feature_motion), strain, pheno_feature, direction, file (intersect_feature_motion_ctrl) from case_ctrl_bed
  	
  	output:
  	set '*.png', strain, pheno_feature, direction into plots_pheno_feature_means
    
  	""" 	
  	plot_pheno_feature_mean_distro.R --bed_file=${intersect_feature_motion} --bed_file_ctrl=${intersect_feature_motion_ctrl}
  	"""
}

result_dir_means_pheno_features = file("$baseDir/plots_means_pheno_features")
 
result_dir_means_pheno_features.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_means_pheno_features"
}

plots_pheno_feature_means.subscribe {		
	it[0].copyTo( result_dir_means_pheno_features.resolve ( it[1] + "." + it[2] + "." + it[3] + ".png" ) )	   
}

/*
 * Creating folder to keep bed files to visualize data
 */
result_dir_GB = file("$baseDir/results_GB")

result_dir_GB.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_GB"
} 

out_fasta.subscribe {  
  fasta_file = it[0]
  fasta_file.copyTo( result_dir_GB.resolve ( it[2] + ".fa" ) )
}

result_dir_bed = file("$baseDir/results_bed")

result_dir_bed.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_bed"
} 

bed_loc_no_nas.subscribe {   
  bed_file = it[0]
  bed_file.copyTo ( result_dir_bed.resolve ( it[1] + "." + it[2] + ".GB.bed" ) )
}

result_dir_bedGraph = file("$baseDir/results_bedGraph")

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
  bed_file.copyTo ( result_dir_bed.resolve ( "intersect." + it[1] + "." + it[3] + "." + it[2] + ".GB.bed" ) )
}