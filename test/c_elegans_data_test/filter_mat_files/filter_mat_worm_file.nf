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
 */    


params.path_files = "$baseDir/mat_worm_data/"

log.info "C. elegans mat files filter  - N F  ~  version 0.1"
log.info "========================================="
log.info "c. elegans data    : ${params.path_files}"
log.info "\n"

mat_files_path = "${params.path_files}*.mat"
mat_files = Channel.fromPath(mat_files_path)
mat_files_path = "${params.path_files}*.mat"
mat_files = Channel.fromPath(mat_files_path)

/*
 * Files not reaching the filtering criteria
 */ 
process get_speed {
	//container 'ipython/scipyserver'
  
  	input:
  	set file ('file_worm') from mat_files

  	output:
    stdout result
    
  	"""
  	frames_by_file.py -i ${file_worm} > files_to_filter.txt
  	cat files_to_filter.txt
  	"""
}

/*
 * print the channel content
 */
result_dir = file( "$baseDir" )

//result.subscribe {  println it }

result
    .collectFile(name: "files_to_filter.txt")
    .subscribe { it.copyTo ( result_dir.resolve () ) } 
