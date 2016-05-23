#!/usr/bin/env Rscript

#  Copyright (c) 2014-2016, Centre for Genomic Regulation (CRG).
#  Copyright (c) 2014-2016, Jose Espinosa-Carrasco and the respective authors.
#
#  This file is part of Pergola.
#
#  Pergola is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pergola is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Pergola.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################
### Jose Espinosa-Carrasco NPMMD/CB-CRG Group. May 2016                   ###
#############################################################################
### Mean values for each group of worms                                   ###
### Using bed files raw data intercepted with the motion                  ### 
#############################################################################

# To use this script in ant first export this:
# export R_LIBS="/software/R/packages"

##Getting HOME directory 
home <- Sys.getenv("HOME")

### Execution example
## Rscript plot_speed_motion_mean.R --bed_file="bed_file"

library(ggplot2)

# Loading params plot:
source("https://raw.githubusercontent.com/cbcrg/mwm/master/lib/R/plot_param_public.R")

#####################
### VARIABLES
#Reading arguments
args <- commandArgs (TRUE) #if not it doesn't start to count correctly

## Default setting when no arguments passed
if ( length(args) < 1) {
  args <- c("--help")
}

## Help section
if("--help" %in% args) {
  cat("
      plot_speed_motion_mean.R
      
      Arguments:
      --bed_file=concat_bed_file     - character      
      --help                         - print this text
      
      Example:
      ./plot_speed_motion_mean.R --bed_file=\"path_to_file\" \n")
  
  q (save="no")
}

# Use to parse arguments beginning by --
parseArgs <- function(x) 
{
  strsplit (sub ("^--", "", x), "=")
}

#Parsing arguments
argsDF <- as.data.frame (do.call("rbind", parseArgs(args)))
argsL <- as.list (as.character(argsDF$V2))
names (argsL) <- argsDF$V1

# All arguments are mandatory
{
  if (is.null (argsL$bed_file)) 
  {
    stop ("[FATAL]: bed_file arg is mandatory")
  }
  else
  {
    bed_file <- argsL$bed_file
  }
}

{
  if (is.null (argsL$bed_file_ctrl)) 
  {
    stop ("[FATAL]: bed_file_ctrl not provided", stderr())
  }
  else
  {
    bed_file_ctrl <- argsL$bed_file_ctrl
  }
}

read_bed <- function (bed_file) {
  info = file.info(bed_file)
  if (info$size == 0) { 
    df_bed <- data.frame (chr="chr1", start=0, end=0, dummy_value=0, mean_value=0, pheno_feature=0, motion=0, strain="")
  }
  else { df_bed <- read.csv(file=bed_file, header=F, sep="\t")        
         colnames (df_bed) <- c("chr", "start", "end", "dummy_value", "mean_value", "pheno_feature", "motion", "strain")          
  }
  
  ## We remove this fake rows they were included just to avoid last line of code above to crash
  df_bed <- df_bed [!(df_bed$start == 0 & df_bed$end == 0), ]
  
  ## Absolute value of the means
  df_bed$mean_value_abs <- abs(df_bed$mean_value)
  
  return (df_bed)
}

df_bed <- read_bed (bed_file)
df_ctrl <- read_bed (bed_file_ctrl)
df_bed <- rbind (df_bed, df_ctrl)
  
name_file <- basename(bed_file)
name_out <- paste(name_file, ".png", sep="")

name_split <- strsplit (name_file, "\\." )

# body_part <- name_split[[1]][2]
# motion <- name_split[[1]][3]
# motion <- gsub ("backward", "when reversing", motion)

pheno_feature <- strsplit (name_file,  "\\.")[[1]][2]
units <- switch (pheno_feature, foraging_speed="Degrees/seconds", tail_motion="Degrees/seconds", crawling="Degrees", 'no units')

title_strain_pheno_dir <- gsub("_", " ", gsub ("\\.", " - ", gsub ("\\.bed", "", name_file)))
title_strain_pheno_dir <- gsub ("backward", "when reversing", title_strain_pheno_dir)

## many files of gk298 strain are annotated as ok298
title_strain_pheno_dir <- gsub ("ok298", "gk298", title_strain_pheno_dir)

### Functions summary stats for plot
## Returns mean and standard deviation
mean_and_sd <- function(x) {
  m <- mean(x)
  sd_min <- m - sd(x)
  sd_max <- m + sd(x)
  return(c(y=m,ymin=sd_min,ymax=sd_max))
}

## Returns mean and standard error of the mean 
mean_and_se <- function(x) {
  m <- mean(x)
  se_min <- m - sd(x)/sqrt(length(x))
  se_max <- m + sd(x)/sqrt(length(x))
  return(c(y=m,ymin=se_min,ymax=se_max))
}

## Returns mean for crossbar
mean_for_cross <- function(x) {
  return(c(y=mean(x), ymin=mean(x), ymax=mean(x)))
}

## color blind friendly palette
cbb_palette <- c("#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7")
size_titles <- 20
size_axis <- 18
size_axis_ticks <- 18
size_axis_ticks_y <- 14

ggplot(df_bed, aes(x=strain, y=mean_value_abs)) +        
       ## standard deviation
       stat_summary(fun.data=mean_and_sd, geom="crossbar", width=0.3, fill=cbb_palette[3]) +
       ## standard error
#        stat_summary(fun.data="mean_se", geom="crossbar", width=0.3, fill=cbb_paletee[8]) +
       stat_summary(fun.data=mean_and_se, geom="crossbar", width=0.3,  col="gray30", fatten=3, fill=cbb_palette[8]) +
       # mean in orange
       stat_summary(fun.data=mean_for_cross, geom="crossbar", width=0.3, size=0.5, colour=cbb_palette[2]) +     
       ## plots means as dots  
       geom_point(position = position_jitter(w = 0.12, h = 0), size=0.25) +
       labs (title = paste(title_strain_pheno_dir, "\n", sep=" ")) +
       labs (y = paste(units, "\n", sep=""), x="") +
       theme (axis.text.x = element_text(size=size_axis_ticks)) +
       theme (plot.title = element_text(size=size_titles)) + 
       theme (axis.title.x = element_text(size=size_axis)) +
       theme (axis.title.y = element_text(size=size_axis)) +
       theme (axis.text.x = element_text(size=size_axis_ticks)) +  
       theme (axis.text.y = element_text(size=size_axis_ticks_y))

ggsave (file=name_out)