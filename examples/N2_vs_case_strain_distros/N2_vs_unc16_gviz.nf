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
 * Process mat files downloaded from the DB to extract locomotion phenotypes characterized 
 * as significantly different between a given strain and its N2 control subset
 * TODO  explain what pergola does
 */    

log.info "C. elegans locomotion phenotypes comparison - N F  ~  version 0.1"
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

data_path = "$baseDir/data"

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

map_speed_path = "$data_path/worms_speed2p.txt" 

map_speed=file(map_speed_path)
//body_parts =  ['head', 'headTip', 'midbody', 'tail', 'tailTip']
body_parts =  ['head', 'headTip', 'midbody', 'tail', 'tailTip', 'foraging_speed', 'tail_motion', 'crawling']

locomotions_files.into { locomotions_files_ori; locomotions_files_gviz }

process feature_to_pergola {
	container 'joseespinosa/pergola:unc16_gviz'
  
  	input:
  	set file ('speed_file'), val (name_file), val (exp_group) from locomotions_files_ori 
  	file worms_speed2p from map_speed
  	each body_part from body_parts
  
  	output: 
  	set '*.no_na.bed', body_part, name_file into bed_loc_no_nas
  	//set '*.no_na.bedGraph', body_part, name_file into bedGraph_loc_no_nas
  	set '*.no_tr.bedGraph', body_part, name_file  into bedGraph_loc_no_nas
  	
  	set name_file, body_part, '*.no_tr.bed', exp_group into bed_loc_no_track_line, bed_loc_no_track_line_cp
  	//set name_file, body_part, '*.no_tr.bedGraph', exp_group into bedGraph_loc_no_track_line
  	
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
  	
  	# cat bedGraph_file.tmp | grep -v "\\-10000" > ${name_file}".no_na.bedGraph"
  	cat bedGraph_file.tmp > ${name_file}".no_na.bedGraph"  
  	cat ${name_file}".no_na.bedGraph" | grep -v "track name" > ${name_file}".no_tr.bedGraph" || echo -e echo -e "chr1\t0\t100\t1" > ${name_file}".no_tr.bedGraph"
  	rm bedGraph_file.tmp 
  	"""
}

/*
 * Transform locomotion files into bedGraph format files for Gviz representation
 */ 
process feature_to_bedGraph {
	container 'joseespinosa/pergola:unc16_gviz'
  
  	input:
  	set file ('speed_file'), val (name_file), val (exp_group) from locomotions_files_gviz 
  	file worms_speed2p from map_speed
  	each body_part from body_parts
  
  	output: 
  	set '*.no_tr.bedGraph', body_part, name_file into bedGraph_GvizWin_no_track_line
  	
  	"""  
  	## The frame rate was set to 20–30 frames per second	
  	cat $worms_speed2p | sed 's/behavioural_file:$body_part > pergola:dummy/behavioural_file:$body_part > pergola:data_value/g' > mod_map_file
  	pergola_rules.py -i $speed_file -m mod_map_file -f bedGraph -w 30
  	
  	# This is done just because is easy to see in the display of the genome browsers
  	cat tr*.bedGraph | sed 's/track name=\"1_a\"/track name=\"${body_part}\"/g' > bedGraph_file.tmp
  	
  	# delete values that were assigned as -10000 to skip na of the original file
  	# to avoid problems if a file got a feature with a feature always set to NA I add this code (short files for examples)
  	# cat bedGraph_file.tmp | grep -v "\\-10000" > ${name_file}".no_na.bedGraph"
  	cat bedGraph_file.tmp > ${name_file}".no_na.bedGraph"  
  	cat ${name_file}".no_na.bedGraph" | grep -v "track name" > ${name_file}".no_tr.bedGraph" || echo -e echo -e "chr1\t0\t100\t1" > ${name_file}".no_tr.bedGraph"
  	rm bedGraph_file.tmp 
  	"""
}


/*
 * Creating folder to keep bed files to visualize data
 */
/*
result_dir_fasta = file("results_fasta_$tag_res")

result_dir_fasta.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_fasta"
} 

out_fasta.subscribe {  
  fasta_file = it[0]
  fasta_file.copyTo( result_dir_fasta.resolve ( it[2] + ".fa" ) )
}

result_dir_bed = file("results_bed_$tag_res")

result_dir_bed.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_bed"
} 

bed_loc_no_nas.subscribe {   
  bed_file = it[0]
  bed_file.copyTo ( result_dir_bed.resolve ( it[1] + "." + it[2] + ".bed" ) )
}
*/
result_dir_bedGraph = file("results_bedGraph_$tag_res")

result_dir_bedGraph.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_bedGraph"
} 

bedGraph_loc_no_nas.subscribe {   
  bedGraph_file = it[0]
  bedGraph_file.copyTo (result_dir_bedGraph.resolve ( it[1] + "." + it[2] + ".bedGraph" ) )
}

bedGraph_GvizWin_no_track_line.subscribe {   
  bedGraph_file = it[0]
  bedGraph_file.copyTo (result_dir_bedGraph.resolve ( it[1] + "." + it[2] + ".gviz.bedGraph" ) )
}
/*
bed_motion_wr.subscribe {
  bed_file = it[1]
  bed_file.copyTo ( result_dir_bed.resolve ( it[0] + it[2] + ".bed" ) )
}

result_dir_bed_intersect = file("$result_dir_bed/motion_intersected")

result_dir_bed_intersect.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_bed_intersect"
} 

bed_intersect_loc_motion.subscribe {   
  bed_file = it[0]
  bed_file.copyTo ( result_dir_bed_intersect.resolve ( "intersect." + it[1] + "." + it[3] + "." + it[4] + ".bed" ) )
}

result_dir_bedGraph_intersect = file("$result_dir_bedGraph/motion_intersected")

result_dir_bedGraph_intersect.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_bedGraph_intersect"
} 

bedGraph_intersect_loc_motion.subscribe {
  bedGraph_file = it[0]
  bedGraph_file.copyTo ( result_dir_bedGraph_intersect.resolve ( "intersect." + it[1] + "." + it[3] + "." + it[4] + ".bedGraph" ) )
}
*/



/s
