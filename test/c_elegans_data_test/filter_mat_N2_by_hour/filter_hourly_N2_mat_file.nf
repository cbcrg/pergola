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
 * Jose Espinosa-Carrasco. CB/CSN-CRG. May 2016
 *
 * Wormbehavior DB (http://wormbehavior.mrc-lmb.cam.ac.uk/) 
 * Process mat files downloaded from the DB filtering of files that include less
 * than 20 fps or less than 14 minutes of recording
 * Also printing time of recording
 */    


params.path_files = "$baseDir/mat_worm_data/"
params.strain_tag = "no_strain"
log.info "C. elegans mat files filter  - N F  ~  version 0.1"
log.info "========================================="
log.info "c. elegans data    : ${params.path_files}"
log.info "c. elegans data    : ${params.strain_tag}"
log.info "\n"

mat_files_path = "${params.path_files}*.mat"
mat_files = Channel.fromPath(mat_files_path)
tag_file_out = "${params.strain_tag}"

/*
 * Creates a channel with file content and name of input file without spaces
 */ 
mat_files_name = mat_files.flatten().map { mat_files_file ->      
	def content = mat_files_file	
	def name = mat_files_file.name
    [ content, name ]
}

/*
 * Files not reaching the filtering criteria
 */ 
process check_file {
	container 'ipython/scipyserver'
  
  	input:
  	set file ('file_worm'), val (name_file) from mat_files_name

  	output:
    stdout result
    
  	"""
  	mat_hourly_by_file.py -i ${file_worm} -n \'${name_file}\' > files_to_filter.txt
  	cat files_to_filter.txt
  	"""
}

/*
 * print the channel content
 */
result_dir = file( "$baseDir" )

//result.subscribe {  println it }

result
    .collectFile(name: "files_to_filter")
    .subscribe {  
    	it.copyTo ( result_dir.resolve (  tag_file_out + "." + it.name + ".txt" ) ) 
    } 
