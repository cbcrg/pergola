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
### Mean values of each animal for each N2 group of worms by hour         ###
#############################################################################

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

info = file.info(bed_file)

{  
  if (info$size == 0) { 
    df_bed <- data.frame (chr="chr1", start=0, end=0, dummy_value=0, mean_value=0, hour="")
  }
  else { df_bed <- read.csv(file=bed_file, header=F, sep="\t")        
         colnames (df_bed) <- c("chr", "start", "end", "dummy_value", "mean_value", "hour")          
  }
}

# We remove this fake rows they were included just to avoid last line of code above to crash
df_bed <- df_bed [!(df_bed$start == 0 & df_bed$end == 0), ]

# Filtering any data that is record before 9 and after 16
df_bed <- df_bed [!(df_bed$hour < 9 | df_bed$hour > 16), ]

name_file <- basename(bed_file)
pheno_feature <-strsplit (name_file, "\\." )[[1]][3]
df_bed$hour_f <- as.factor (df_bed$hour)

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
size_axis_ticks_x <- 14
size_axis_ticks_y <- 14

pheno_feature_up <- paste (toupper(substr(pheno_feature, 1, 1)), substr(pheno_feature, 2, nchar(pheno_feature)), sep="")
units <- switch (pheno_feature, length="mm", foraging="degrees", range="mm", 'no units')
name_out <- paste (name_file, ".", "png", sep="")

ggplot(df_bed, aes(x=hour_f, y=mean_value)) +        
  ## standard deviation
  stat_summary(fun.data=mean_and_sd, geom="crossbar", width=0.25, fill=cbb_palette[3]) +
  ## standard error
  #        stat_summary(fun.data="mean_se", geom="crossbar", width=0.25, fill=cbb_paletee[8]) +
  stat_summary(fun.data=mean_and_se, geom="crossbar", width=0.25,  col="gray30", fatten=3, fill=cbb_palette[8]) +
  # mean in orange
  stat_summary(fun.data=mean_for_cross, geom="crossbar", width=0.25, size=1, colour=cbb_palette[2]) +     
  ## plots means as dots  
  geom_point(position = position_jitter(w = 0.05, h = 0), size=3) +
  labs (title = paste(pheno_feature_up, "\n", sep="")) +
  labs (y = paste(paste (pheno_feature_up, " (", units, ")", "\n", sep="")), x="\nHour") +  
  theme (plot.title = element_text(size=size_titles)) + 
  theme (axis.title.x = element_text(size=size_axis)) +
  theme (axis.title.y = element_text(size=size_axis)) +
  theme (axis.text.x = element_text(size=size_axis_ticks_x)) +  
  theme (axis.text.y = element_text(size=size_axis_ticks_y))

ggsave (file=name_out)