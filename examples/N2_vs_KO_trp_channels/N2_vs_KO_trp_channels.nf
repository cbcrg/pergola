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

mat_files_name.into { mat_files_loc; mat_files_motion; mat_files_turns}

/*
 * Get speed from mat files
 */ 
process get_locomotion {
	container 'ipython/scipyserver'
  
  	input:
  	set file ('file_worm'), val (name_file_worm) from mat_files_loc
  
  	output:  
  	set '*_loc.csv', name_file_worm into locomotions_files, locomotion_files_wr
     
  	script:
  	println "Matlab file containing worm behavior processed: $name_file_worm"

  	"""
  	extract_trp_features.py -i $file_worm  	
  	"""
}

/*
 * Transform speed files into bed format files
 */ 

map_features_path = "$baseDir/data/trp_features_map.txt" 

map_features = file(map_features_path)

// Hacer de esto un parametro asi puedo escoger la strain y la feature y no repetir
// todo el codigo
// de momento lo dejo asi por el tiempo
phenotypic_features =  ['foraging_speed', 'tail_motion', 'crawling']

process locomotion_to_pergola {
	container 'cbcrg/pergola:latest'
  
  	input:
  	set file ('loc_file'), val (name_file) from locomotions_files
  	file map_features2p from map_features
  	each pheno_feature from phenotypic_features
  
  	output: 
  	set 'tr*.bed', pheno_feature, name_file into bed_speed
  	set 'tr*.bedGraph', pheno_feature, name_file into bedGraph_speed
  	set '*.fa', pheno_feature, name_file into out_fasta
  
  	"""  
  	cat $map_features2p | sed 's/behavioural_file:$pheno_feature > pergola:dummy/behavioural_file:$pheno_feature > pergola:data_value/g' > feat_map_file
  	pergola_rules.py -i $loc_file -m feat_map_file
  	pergola_rules.py -i $loc_file -m feat_map_file -f bedGraph -w 1 
  	"""
}
