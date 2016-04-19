#!/usr/bin/env nextflow

/*
#################################################################################
### Jose Espinosa-Carrasco. CB/CSN-CRG. April 2016                            ###
#################################################################################
### Code : 04.19                                                              ### 
### Worm DB distribution by strains                                           ###
#################################################################################
*/

params.path_files = "$HOME/git/pergola/test/c_elegans_data_test/"
mat_files_path = "${params.path_files}*.mat"
mat_files = Channel.fromPath(mat_files_path)

worm_strains = [ '575_JU440', 'N2', 'flp-19ok2460', 'flp-20ok2964', 'ins-15ok3444I', 'nlp-14tm1880X' ]
//worm_strains = [ '575_JU440', 'N2']
body_parts = [ 'head', 'headTip', 'midbody', 'tail', 'tailTip' ]
motion_directions = [ 'forward', 'backward', 'paused' ]

process plot_distro {
  input:
  val body_part from body_parts
  each worm_strain from worm_strains 
  each motion_direction from motion_directions
  
  output:
  set '*.png' into plot_file
    		
  """
  export R_LIBS="/software/R/packages"
  Rscript \$HOME/git/pergola/test/c_elegans_data_test/plot_speed_motion_mean.R --body_part=${body_part} --pattern_worm=${worm_strain} --motion=${motion_direction}		
  """
}
  
plot_file.subscribe {
  plot_file= it
  plot_file.copyTo ( it.name )
}