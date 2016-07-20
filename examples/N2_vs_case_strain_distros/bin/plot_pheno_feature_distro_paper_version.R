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
## Rscript plot_speed_motion_mean.R --bed_file="bed_file" --bed_file_ctrl="bed_file_ctrl"
library(ggplot2)
library('extrafont')

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
         df_bed <- data.frame (chr="chr1", start=0, end=0, data_type=0, value=0, strand=0, s=0, e=0, color_code=0, body_part="", motion=0, strain="")
  }
  else { df_bed <- read.csv(file=bed_file, header=F, sep="\t")        
         colnames (df_bed) <- c("chr", "start", "end", "data_type", "value", "strand", "s", "e", "color_code",  "body_part", "motion", "strain")
  }
  
  ## We remove this fake rows they were included just to avoid last line of code above to crash
  df_bed <- df_bed [!(df_bed$start == 0 & df_bed$end == 0), ]
    
  return (df_bed)
}

df_bed <- read_bed (bed_file)
df_ctrl <- read_bed (bed_file_ctrl)
df_bed <- rbind (df_bed, df_ctrl)
df_bed <- read_bed ("/Users/jespinosa/git/pergola/examples/N2_vs_case_strain_distros/work/a0/5828f6e64bc99999df7cb54da1340f/N2.midbody.forward.bed")
name_file <- basename(bed_file)

name_split <- strsplit (name_file, "\\." )

# body_part <- name_split[[1]][2]
# motion <- name_split[[1]][3]
# motion <- gsub ("backward", "when reversing", motion)

pheno_feature <- strsplit (name_file,  "\\.")[[1]][2]
#units <- switch (pheno_feature, foraging_speed="Degrees/seconds", tail_motion="Degrees/seconds", crawling="Degrees", 'no units')
units <-"Microns/seconds"

title_strain_pheno_dir <- gsub("_", " ", gsub ("\\.", " - ", gsub ("\\.bed", "", name_file)))
# title_strain_pheno_dir <- gsub ("backward", "\nwhen reversing", title_strain_pheno_dir)

## color blind friendly palette
cbb_palette <- c("#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7")
size_titles <- 5
size_axis <- 5
size_axis_ticks <- 4
size_axis_ticks_y <- 4

# aes and fonts for publications plot
plot_width <- 12
plot_height <- 12 
font <- "Arial"
dpi <- 300
# file_format <- ".png"
file_format <- ".pdf"

name_out <- paste(name_file, file_format, sep="")

# From the maximun and minimun value I add a shift to set axes limits
shift_axes <- 100
tick_interval <- 400
xmin <- round(min (df_bed$value) - shift_axes, digits = -2)
xmax <- round(max (df_bed$value) + shift_axes, digits = -2)
# xmin <- -100
# xmax <- 600
breaks_v <- c(-rev(seq(0,abs(xmin), by=tick_interval)[0:-1]), seq (0, xmax, by=tick_interval))

labs_plot <- as.vector(levels(df_bed$strain))

labs_plot [!labs_plot %in% "N2"] <- "Exp"
labs_plot [labs_plot %in% "N2"] <- "Ctrl"

ggplot(df_bed, aes(x=value, fill=strain)) + geom_density(alpha=0.25) +
       scale_x_continuous (breaks=breaks_v, limits=c(xmin, xmax)) +
       scale_y_continuous(breaks=NULL) +
       labs (title = paste(title_strain_pheno_dir, "\n", sep=" ")) +
       labs (x = paste("\n", units, sep=""), 
             y = expression(paste("Probability (", Sigma, "P(x) = 1)", "\n", sep=""))) +       
       theme (axis.text.x = element_text(family=font, size=size_axis_ticks)) +
       theme (plot.title = element_text(family=font, size=size_titles)) + 
       theme (axis.title.x = element_text(family=font, size=size_axis)) +
       theme (axis.title.y = element_text(family=font, size=size_axis)) +
       theme (axis.text.x = element_text(family=font, size=size_axis_ticks)) +  
       theme (axis.text.y = element_text(family=font, size=size_axis_ticks_y)) +       
       scale_fill_manual(name='', labels = labs_plot, values = cbb_palette) +
       theme (legend.text = element_text(family=font))
#        scale_fill_manual( name='', values = cbb_palette) 

ggsave (file=name_out, width = plot_width, height=plot_height))
