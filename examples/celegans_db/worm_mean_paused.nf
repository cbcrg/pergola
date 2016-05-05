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
#################################################################################
### Jose Espinosa-Carrasco. CB/CSN-CRG. April 2016                            ###
#################################################################################
### Code : 04.29                                                              ### 
### Worm DB processed by pergola for paper                                    ###
###                                                                           ###
### run local: nextflow run worm_mean_paused.nf -profile standard -resume     ###
### run cluster: nextflow run worm_mean_paused.nf -profile cluster -resume    ###
#################################################################################
*/

//params.path_files = "$HOME/git/pergola/test/c_elegans_data_test/results_motion_GB/"

params.path_files = "$HOME/git/pergola/test/c_elegans_data_test/"

mat_files_path = "${params.path_files}*.mat"
mat_files = Channel.fromPath(mat_files_path)


// Name of input file and file 
mat_files_name = mat_files.flatten().map { mat_files_file ->      
   def content = mat_files_file
   def name = mat_files_file.name.replaceAll(/ /,'_')
   [ content, name ]
}

process get_motion {
  //container 'scivm/scientific-python-2.7'
  container 'ipython/scipyserver'	  

  input:  
  set file ('file_worm'), val (name_file_worm) from mat_files_name
  
  output: 
  set name_file_worm, '*.csv' into motion_csv, motion_csv_wr
  
  script:
  println "Matlab file containing worm behavior processed: $file_worm"

  //$HOME/git/pergola/test/c_elegans_data_test/extract_worm_motion_joined.py -i \"$file_worm\"	
  
  """  
  extract_worm_motion_joined.py -i \"$file_worm\"  
  """
}

//forward_backward_csv.subscribe {println it}
map_motion_path = "$HOME/git/pergola/test/c_elegans_data_test/worms_motion_joined2p.txt"
map_motion_file = Channel.fromPath(map_motion_path)
map_motion_file.into { map_file_f; map_file_b; map_file_p }

// Combines forward and backward and gets the complement
process motion_to_bed {
	container 'joseespinosa/pergola:celegans'
	
	input:			
	set val(name_mat_file), file ('motion_file') from motion_csv
	
	file map_csv_motion from map_file_f.first()
	
	output:
	set  name_mat_file, 'tr_1_dt_forward.bed', 'tr_1_dt_backward.bed', 'tr_1_dt_paused.bed', 'chrom.sizes' into motion_bed
	
	"""
	pergola_rules.py -i $motion_file -m $map_csv_motion -nt  	
	"""	
}


map_bed_path = "$HOME/git/pergola/test/c_elegans_data_test/bed2pergola.txt"
map_bed_file = file (map_bed_path)

process join_and_complement {
	//container 'scivm/scientific-python-2.7'
        //container 'ipython/scipyserver'
	container 'joseespinosa/pergola:celegans'
	input:
	set val (name_mat_file), file ('forward_bed'), file ('backward_bed'), file ('paused_bed'), file ('chrom_sizes') from motion_bed
	file map_bed from map_bed_file
	
	output:
  	set name_mat_file, 'time_bw_motion.bed'   into time_bw_motion, time_bw_motion_wr    
  	set name_mat_file, 'time_bw_for_for.bed' into time_for_for, time_for_for_wr
  	set name_mat_file, 'time_bw_back_back.bed' into time_back_back, time_back_back_wr
  	set name_mat_file, 'time_bw_for_back.bed' into time_for_back, time_for_back_wr
  	set name_mat_file, 'time_bw_back_for.bed' into time_back_for, time_back_for_wr
  	
  	//$HOME/git/pergola/test/c_elegans_data_test/time_bw_motion_for_back.py -f $forward_bed -b $backward_bed -m $map_bed -c $chrom_sizes  	
  	
  	"""  	
  	time_bw_motion_for_back.py -f $forward_bed -b $backward_bed -m $map_bed -c $chrom_sizes  	
  	"""
  
	}

time_bw_motion_plot = time_bw_motion.collectFile(newLine: false, sort:'none') { 	
	def name = it[0].split("_on_")[0]
	[ name, it[1].text ] 
	}
time_for_for_plot = time_for_for.collectFile(newLine: false, sort:'none') { 	
	def name = it[0].split("_on_")[0]
	[ name, it[1].text ] 
	}	
time_back_back_plot = time_back_back.collectFile(newLine: false, sort:'none') { 	
	def name = it[0].split("_on_")[0]
	[ name, it[1].text ] 
	}
time_for_back_plot = time_for_back.collectFile(newLine: false, sort:'none') { 	
	def name = it[0].split("_on_")[0]
	[ name, it[1].text ] 
	}
time_back_for_plot = time_back_for.collectFile(newLine: false, sort:'none') { 	
	def name = it[0].split("_on_")[0]
	[ name, it[1].text ] 
	}

all_trans = time_bw_motion_plot
	.spread(time_for_for_plot)
	.filter { it[0].name == it[1].name}
	.spread(time_back_back_plot)
	.filter { it[0].name == it[2].name}
	.spread(time_for_back_plot)
	.filter { it[0].name == it[3].name}
	.spread(time_back_for_plot)
	.filter { it[0].name == it[4].name}
	.map { [it[0], it[1], it[2], it[3], it[4], it[0].name ] }
	
//all_trans.subscribe{ println it }


process plot_distro_time {
	container 'joseespinosa/docker-r-ggplot2:v0.1'
	
	input:
		set file ('time_bw_motion'), file ('time_for_for'), file ('time_back_back'), file ('time_for_back'), file ('time_back_for'), strain from all_trans
	output:
		set '*.png' into plots_time_bw_motion
	
	//Rscript \$HOME/git/pergola/test/c_elegans_data_test/plot_time_bw_distro.R --bed_file=${time_bw_motion} --transition=\'All motion transitions\'  
  	
  	//export R_LIBS="/software/R/packages"
	//Rscript \$HOME/git/pergola/test/c_elegans_data_test/plot_time_bw_distro_grid_transitions.R
	
	"""
	plot_time_bw_distro_grid_transitions.R --bed_file_all_tr=${time_bw_motion} \
	--bed_file_for_for=${time_for_for} --bed_file_back_back=${time_back_back} --bed_file_for_back=${time_for_back} \
	--bed_file_back_for=${time_back_for} --strain=${strain}
  	"""
} 

// Creating motion results folder
result_dir_plots_time_bw_motion = file("$baseDir/plots_time_bw_motion")

result_dir_plots_time_bw_motion.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_plots_time_bw_motion"
}

plots_time_bw_motion.subscribe {   
  it.copyTo( result_dir_plots_time_bw_motion.resolve ( it.name ) )
}

// Saving csv files into a folder
result_dir_csv_motion = file("$baseDir/csv_motion")

result_dir_csv_motion.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_csv_motion"
}

motion_csv_wr.subscribe { 
	csv_file = it[1]
	csv_file.copyTo( result_dir_csv_motion.resolve ( it[0] + ".motion.csv" ) )
}  

//Saving bed files into a folder
result_dir_bw_motion = file("$baseDir/bed_files_bw_motion")

result_dir_plots_time_bw_motion.with {
     if( !empty() ) { deleteDir() }
     mkdirs()
     println "Created: $result_dir_bw_motion"
}

time_bw_motion_wr.subscribe { 
	bed_file = it[1]
	bed_file.copyTo( result_dir_bw_motion.resolve ( "bw_motion_" + it[0] + ".bed" ) )
}  

time_for_for_wr.subscribe { 
	bed_file = it[1]
	bed_file.copyTo( result_dir_bw_motion.resolve ( "for_for_" + it[0] + ".bed" ) )
}  

time_back_back_wr.subscribe { 
	bed_file = it[1]
	bed_file.copyTo( result_dir_bw_motion.resolve ( "back_back_" + it[0] + ".bed" ) )
}  

time_for_back_wr.subscribe { 
	bed_file = it[1]
	bed_file.copyTo( result_dir_bw_motion.resolve ( "for_back_" + it[0] + ".bed" ) )
}  

time_back_for_wr.subscribe { 
	bed_file = it[1]
	bed_file.copyTo( result_dir_bw_motion.resolve ( "back_for_" + it[0] + ".bed" ) )
}  
