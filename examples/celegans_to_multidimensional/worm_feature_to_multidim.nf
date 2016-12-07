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
 * Process mat files downloaded from the DB to extract several variables of celegans motion 
 * to used them in a PCA like approach
 */    


params.path_files = "$baseDir/data/"

log.info "C. elegans features  - N F  ~  version 0.1"
log.info "========================================="
log.info "c. elegans data    : ${params.path_files}"
log.info "c. elegans tag     : ${params.tag_results}"
log.info "Output directory   : ${params.output_dir}"
log.info "\n"

mat_files_path = "${params.path_files}*.mat"
mat_files = Channel.fromPath(mat_files_path)
params.tag_results = ""
itag_res = "${params.tag_results}"
result_dir_csv="${params.output_dir}"

if (result_dir_csv == null) {
	result_dir_csv=baseDir
	println "Results directory set to: ${result_dir_csv}"
}

output_file="var_to_multidim_${params.tag_results}.csv"

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
process get_variables {
	container 'ipython/scipyserver'
  
  	input:
  	set file ('file_worm'), val (name_file_worm) from mat_files_speed
  
  	output:
  	//set '*.multivar.csv', name_file_worm into multivar_files, multivar_files_wr
    set '*.multivar.csv' into multivar_files
  	
  	script:
  	println "Matlab file containing worm behavior processed: $name_file_worm"

  	"""
  	extract_features_mean.py -i $file_worm
  	"""
}

result_dir = file("${result_dir_csv}")
outFile = file(output_file)
outFile.text = 'strain\tunix_time\tframe_start\tframe_end\tlength\trange\teccentricity\twave_length_primary\tkinks\ttrack_length\n'
 
multivar_files
	.collectFile (name: output_file)
	.subscribe {
		outFile << it.text
		outFile.copyTo( result_dir.resolve ( it.name  ) )
	}
