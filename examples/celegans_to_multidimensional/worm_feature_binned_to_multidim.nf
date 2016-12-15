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
 * Jose Espinosa-Carrasco. CB/CSN-CRG. November 2016
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
    set '*.multivar.csv', name_file_worm into frame_files
  	
  	script:
  	println "Matlab file containing worm behavior processed: $name_file_worm"

  	"""
  	extract_features_trajectory.py -i $file_worm
  	"""
}

/*
 * Transform variables files by pergola creating mapping file
 */ 
map_var_path = "$baseDir/data/worms_vari_to_p.txt" 

map_var=file(map_var_path)

variables = ['length','range','eccentricity','wave_length_primary',
			 'kinks','track_length','velocity_head_direction','velocity_head_speed',
			 'velocity_headTip_direction','velocity_headTip_speed','velocity_midbody_direction','velocity_midbody_speed',
			 'velocity_tail_direction','velocity_tail_speed','velocity_tailTip_direction',
			 'velocity_tailTip_speed','bends_foraging_amplitude','bends_foraging_angleSpeed',
			 'bends_head_amplitude','bends_head_frequency','bends_midbody_amplitude',
			 'bends_midbody_frequency','bends_tail_amplitude','bends_tail_frequency']
			 
process speed_to_pergola {
	container 'joseespinosa/pergola:celegans'
  
  	input:
  	set file ('var_file'), val (name_file) from frame_files
  	file worms_var_to_p from map_var
  	each var from variables
  
  	output:   	
  	set 'tr*.bedGraph', var, name_file into multivar_files
  	
  	"""  
  	cat $worms_var_to_p | sed 's/behavioural_file:$var > pergola:dummy/behavioural_file:$var > pergola:data_value/g' > mod_map_file     	
  	pergola_rules.py -i $var_file -m mod_map_file -f bedGraph -w 30 -wm
  	"""
}

result_dir = file("${result_dir_csv}")

multivar_files.subscribe { 
	file_var = it[0]
 	file_var.copyTo( result_dir.resolve ( it[2] + "." + it[1] + ".bedGraph"  ) )
}

/*
    }
    
result_dir = file("${result_dir_csv}")
outFile = file(output_file)

multivar_files
.collectFile (name: output_file)
.subscribe {
	outFile.copyTo( result_dir.resolve ( it.name + ".bin"  ) )
}
*/