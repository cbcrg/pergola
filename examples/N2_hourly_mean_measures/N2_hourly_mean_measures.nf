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
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
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
 * Get the time of the day (hour in the naming of the file) and group them in order to reproduce the figure 3 of
 * supplementary materials.
 * las medidas como el numero, igual se podria utilizar pergola y bedtools
 * pero en este caso seria interesante ver si la visualizacion directa hace que se vea a ojo
 * TODO  explain what pergola does
 */    

params.path_files = "$baseDir/data/"

log.info "C. elegans N2 hourly phenotypes - N F  ~  version 0.1"
log.info "========================================="
log.info "c. elegans data    : ${params.path_files}"
log.info "\n"

mat_files_path = "${params.path_files}*.mat"
mat_files = Channel.fromPath(mat_files_path)

/*
 * Creates a channel with file content and name of input file without spaces
 */ 
mat_files_name = mat_files.flatten().map { mat_files_file ->      
	def content = mat_files_file
	def name = mat_files_file.name.replaceAll(/ /,'_')
    [ content, name ]
}

mat_files_name.into { mat_files_pheno; mat_files_motion }

/*
 * Get c. elegans phenotypes from mat files
 */ 
process get_pheno_measure {
	container 'ipython/scipyserver'
  
  	input:
  	set file ('file_worm'), val (name_file_worm) from mat_files_pheno
  
  	output:  
  	set '*.pheno.csv', name_file_worm into pheno_measure_files, pheno_measure_files_wr
     
  	script:
  	println "Matlab file containing worm behavior processed: $name_file_worm"

  	"""
  	extract_N2_features.py -i $file_worm  	
  	"""
}

/*
 * Folder to save csv phenotypic features files 
 */
result_dir_pheno_features = file("$baseDir/results_N2_features")

result_dir_pheno_features.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_pheno_features"
}

//pheno_measure_files_wr.subscribe { println (it) }

pheno_measure_files_hour = pheno_measure_files.map { 
	def content = it[0]
	def name = it[0].name.split("\\.")[0] + "." + it[1]
	def hour = it[0].name.split("\\.")[0] 
    [ content, name, hour ]
}

//pheno_measure_files_hour.subscribe { println (it) }

pheno_measure_files_wr.subscribe { 
  it[0].copyTo( result_dir_pheno_features.resolve ( it[0].name.split("\\.")[0] + "." + it[1] ))
}

/*
 * Transform phenotypic features files into bed format files
 */ 
map_features_path = "$baseDir/data/N2_features_map.txt" 

map_features = file(map_features_path)

// Phenotypic features extracted
phenotypic_features =  ['length', 'foraging', 'range']

process pheno_features_to_pergola {
	container 'cbcrg/pergola:latest'
  
  	input:
  	set file ('pheno_file'), val (name_file), val (hour) from pheno_measure_files_hour
  	file map_features2p from map_features
  	each pheno_feature from phenotypic_features
  
  	output: 
  	set '*.no_na.bed', pheno_feature, name_file into bed_measure_no_nas
  	set '*.no_na.bedGraph', pheno_feature, name_file into bedGraph_measure_no_nas
  	
  	set name_file, pheno_feature, '*.no_tr.bed', hour into bed_measure_no_track_line, bed_measure_no_track_line_cp, bed_measure_no_track_line_turns
  	set name_file, pheno_feature, '*.no_tr.bedGraph', hour into bedGraph_measure_no_track_line
  	
  	set '*.fa', pheno_feature, name_file into out_fasta
  
  	"""  
  	cat $map_features2p | sed 's/behavioural_file:$pheno_feature > pergola:dummy/behavioural_file:$pheno_feature > pergola:data_value/g' > feat_map_file
  	pergola_rules.py -i $pheno_file -m feat_map_file
  	pergola_rules.py -i $pheno_file -m feat_map_file -f bedGraph -w 1 
  	
  	# This is done just because is easy to see in the display of the genome browsers
  	cat tr*.bed | sed 's/track name=\"1_a\"/track name=\"${pheno_feature}\"/g' > bed_file.tmp
  	
  	cat tr*.bedGraph | sed 's/track name=\"1_a\"/track name=\"${pheno_feature}\"/g' > bedGraph_file.tmp
  	
  	# delete values that were assigned as -10000 to skip na of the original file
  	# to avoid problems if a file got a feature with a feature always set to NA I add this code (short files for examples)
  	cat bed_file.tmp | grep -v "\\-10000" > ${name_file}".no_na.bed"  
  	cat ${name_file}".no_na.bed" | grep -v "track name" > ${name_file}".no_tr.bed" || echo -e "chr1\t0\t100\t.\t-10000\t+\t0\t100\t135,206,250" > ${name_file}".no_tr.bed"    	
  	rm bed_file.tmp
  	
  	cat bedGraph_file.tmp | grep -v "\\-10000" > ${name_file}".no_na.bedGraph"  
  	cat ${name_file}".no_na.bedGraph" | grep -v "track name" > ${name_file}".no_tr.bedGraph" || echo -e echo -e "chr1\t0\t100\t1" > ${name_file}".no_tr.bedGraph"
  	rm bedGraph_file.tmp 
  	"""
}

//bed_measure_no_track_line

//process pheno_features_to_pergola {
//	container 'cbcrg/pergola:latest'

map_bed_path = "$baseDir/data/bed2pergola.txt"
map_bed_pergola = Channel.fromPath(map_bed_path)
//map_bed_pergola.into { map_bed_pergola_loc; map_bed_pergola_turn}


process bed_mean {
	container 'ipython/scipyserver'
	
	input:
	set name_file, pheno_feature, bed_file, hour from bed_measure_no_track_line	
	file bed2pergola from map_bed_pergola.first()
	
	output:
	//set '*.mean_file.bed', pheno_feature, name_file, hour into mean_feature
	set 'tag.mean_file.bed', pheno_feature, name_file, hour into mean_feature
	
	"""
	celegans_feature_mean.py -p $bed_file -m $bed2pergola
	#awk '{ print \$0, \"\\t$hour\" }' ${name_file}".no_tr.bed.tmp" > ${name_file}".no_tr.bed" 
	cat *.mean_file.bed | awk '{ print \$0, \"\\t$hour\" }' > tag.mean_file.bed
	"""
}

/*
 * Grouping files by hour and phenotypic feature for plotting
 */ 
mean_feature_plot_col = mean_feature.collectFile (newLine: false, sort:'none') {
	def name = "N2." + it[3] + "." + it[1]
	[ name, it[0].text ] 
}

/*
 * Plots the distribution of bed containing all intervals by hour of the day
 */
process plot_distro {
	container 'joseespinosa/docker-r-ggplot2:v0.1'

  	input:
  	file N2_measure_by_h from mean_feature_plot_col
  
  	output:
  	set '*.png' into plots_measure_by_hour
    
  	script:
  	println ">>>>>>>>>>>>>>>: $N2_measure_by_h"
  	
  	"""
  	plot_N2_mean_feature_by_hour.R --bed_file=${N2_measure_by_h}
  	"""
}

//bed_measure_no_track_line_cp.subscribe { println it }

/*
 * Dumping bed and bedgraph files for its visualization
 */ 

// bed files
result_dir_bed = file("$baseDir/results_bed")
 
result_dir_bed.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_bed"
}

bed_measure_no_nas.subscribe {   
  bed_file = it[0]  
  bed_file.copyTo ( result_dir_bed.resolve ( it[1] + "." + it[2] + ".GB.bed" ) )
}

// bedGraph files
result_dir_bedGraph = file("$baseDir/results_bedGraph")
 
result_dir_bedGraph.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_bedGraph"
}

bedGraph_measure_no_nas.subscribe {   
  bedGraph_file = it[0]  
  bedGraph_file.copyTo (result_dir_bedGraph.resolve ( it[1] + "." + it[2] + ".GB.bedGraph" ) )
}

// fasta files
result_dir_fasta = file("$baseDir/results_fasta")
 
result_dir_fasta.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_fasta"
}

out_fasta.subscribe {   
  fasta_file = it[0]  
  fasta_file.copyTo( result_dir_fasta.resolve ( it[2] + ".fa" ) )
}

//bed_measure_no_track_line.subscribe { println ("======" + it) }

/*
 * Folder to keep plots
 */
result_dir_plots = file("$baseDir/plots_N2_means_by_h")
 
result_dir_plots.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_plots"
}

plots_measure_by_hour.subscribe {   
  it.copyTo( result_dir_plots.resolve ( it.name ) )
}