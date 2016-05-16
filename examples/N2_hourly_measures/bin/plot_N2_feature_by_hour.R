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

# bed_file<-"/Users/jespinosa/git/pergola/examples/N2_hourly_measures/work/bd/9f3779b594abb816e88eafa7d790ab/N2.range"

info = file.info(bed_file)

{  
  if (info$size == 0) { 
    df_bed <- data.frame (chr="chr1", start=0, end=0, data_type=0, value=0, strand=0, s=0, e=0, color_code=0, hour=0)
  }
  else { df_bed <- read.csv(file=bed_file, header=F, sep="\t")
         colnames (df_bed) <- c("chr", "start", "end", "data_type", "value", "strand", "s", "e", "color_code", "hour")
  }  
}

# We remove this fake rows they were included just to avoid last line of code above to crash
df_bed <- df_bed [!(df_bed$start == 0 & df_bed$end == 0), ]

name_file <- basename(bed_file)
pheno_feature <-strsplit (name_file, "\\." )[[1]][2]

units <- switch(pheno_feature, length="mm", foraging="degrees", range="mm", 'no units')
name_out <- paste (name_file, ".", pheno_feature, ".png", sep="")

size_strips <- 12
size_titles <- 13
size_axis <- 12
size_axis_ticks <- 10
xmin <- -1000
xmax <- 1000

pheno_feature_up <- paste (toupper(substr(pheno_feature, 1, 1)), substr(pheno_feature, 2, nchar(pheno_feature)), sep="")

paste (pheno_feature_up, "\n", sep="")

ggplot(df_bed, aes (hour, value, fill = as.factor(hour))) + 
  geom_boxplot(show.legend = FALSE) +
  scale_x_continuous(breaks=c(9,10,11,12,13,14,15,16)) +
  scale_fill_manual(name = "Genotype", values=rep("lightblue",8)) +
  labs(title = paste (pheno_feature_up, "\n", sep="")) +
  xlab ("\nHour") + ylab(paste (pheno_feature_up, " (", units, ")", "\n", sep=""))

ggsave (file=name_out)