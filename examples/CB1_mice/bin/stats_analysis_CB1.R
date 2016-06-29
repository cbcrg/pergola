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
### Jose Espinosa-Carrasco NPMMD/CB-CRG Group. June 2016                  ###
#############################################################################
### Mean values for each group of mice                                    ###
### Using bed files with bouts intersected with day phases                ###
### (light and dark)                                                      ###
#############################################################################

##Getting HOME directory
# home <- Sys.getenv("HOME") #del

##Loading libraries
library ("ggplot2")
library ("plotrix") #std.error

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
      starting_regions_file_vs_24h
      
      Arguments:
      --tag=someValue        - character, stat to analyze (sum, mean, ...)
      --path2files=someValue - character, path to read files
      --path2plot=someValue  - character, path to dump plots
      --help                 - print this text
      
      Example:
      ./starting_regions_file_vs_24h.R --tag=\"sum\" --path2plot=\"/foo/plots\"\n")
  
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
print (paste(">>>>>>>>>>@@@@@@@@@",argsL))
print(paste(".....argsDF",argsDF$V1))
print(paste(">>>>>> length",length(names(argsL))))
names (argsL) <- argsDF$V1

# tag is mandatory
{
  if (is.null (argsL$tag)) 
  {
    stop ("[FATAL]: Tag parameter is mandatory")
  }
  else
  {
    tag <- argsL$tag
  }
}

# path to files
{
  if (is.null (argsL$path2files)) 
  {
    stop ("[FATAL]: Path to files is mandatory")
  }
  else
  {
    path2files <- argsL$path2files
  }
}

{
  if (is.null (argsL$path2plot)) 
  {
    print ("[Warning]: Plots will be dump in working directory as not path was provided")
    path2plot <- getwd()  
  }
  else
  {
    path2plot <- argsL$path2plot
  }
}


# Loading params plot:
source("https://raw.githubusercontent.com/cbcrg/mwm/master/lib/R/plot_param_public.R")
# path2files <- "/Users/jespinosa/git/pergola/examples/CB1_mice/results/"
# path2plot <- "/Users/jespinosa/git/pergola/examples/CB1_mice/"

write(paste("Path to files: ", path2files, sep=""), stderr())
setwd(path2files)

files <- list.files(pattern=paste("tr_.*.bed$", sep=""))
  
data.frame_bed <- NULL

for (bed_file in files) {
  
  info = file.info (bed_file)
  if (info$size == 0) { next }
    
  df <- read.csv(bed_file, header=F, sep="\t")
  
  phenotype <- gsub ("tr_", "", unlist(strsplit(bed_file, split=".",fixed=T))[1])
  mouse <- gsub ("tr_", "", unlist(strsplit(bed_file, split=".",fixed=T))[2])
  data_type <- gsub ("tr_", "", unlist(strsplit(bed_file, split=".",fixed=T))[3])
  phase <- gsub ("tr_", "", unlist(strsplit(bed_file, split=".",fixed=T))[4])
  df$phenotype <- phenotype
  df$mouse <- mouse
  df$data_type <- data_type
  df$phase <- phase
  df$group2plot <- paste (phase, data_type)
#   print (paste (phenotype, phase, data_type)) 
  data.frame_bed <- rbind(data.frame_bed, df)
}

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

# pheno_feature_up <- paste (toupper(substr(pheno_feature, 1, 1)), substr(pheno_feature, 2, nchar(pheno_feature)), sep="")
# units <- switch (pheno_feature, length="mm", foraging="degrees", range="mm", 'no units')
name_file <- "plot"
name_out <- paste (path2plot, name_file, ".", "png", sep="")

plot_title <- switch (tag, count="Feeding bouts", mean=paste("Mean intake per feeding bout", ''))
axis_title <- switch (tag, count="Number of bouts", mean='g', 'no units' )

ggplot(data.frame_bed, aes(x=group2plot, y=V5, colour=phase, fill=data_type)) +
  ## standard deviation
  stat_summary(fun.data=mean_and_sd, geom="crossbar", width=0.3, lwd=1) +
  scale_fill_manual(values = c(cbb_palette[2], cbb_palette[1])) +
  ## standard error
  stat_summary(fun.data=mean_and_se, geom="crossbar", width=0.3, col=cbb_palette[8], fatten=3, fill=cbb_palette[8]) +
#   # mean in orange
  stat_summary(fun.data=mean_for_cross, geom="crossbar", width=0.3, size=0.3, colour=cbb_palette[5]) +
  scale_colour_manual(values = c(cbb_palette[6], cbb_palette[3])) +
  ## plots means as dots  
  geom_point(position = position_jitter(w = 0.12, h = 0), size=0.25) +
  labs (title = paste(plot_title, "\n", sep="")) +
  labs (y = paste(paste (axis_title, "\n", sep="")), x="\nPhase") +  
  theme (plot.title = element_text(size=size_titles)) + 
  theme (axis.title.x = element_text(size=size_axis)) +
  theme (axis.title.y = element_text(size=size_axis)) +
  theme (axis.text.x = element_text(size=size_axis_ticks_x)) +  
  theme (axis.text.y = element_text(size=size_axis_ticks_y)) +
  theme (axis.text.x = element_text(angle=-90, vjust=0.4,hjust=1)) +
  facet_grid(.~phenotype) +
  theme(strip.background = element_rect(fill="white")) +
  theme(strip.text.x = element_text(size = size_axis_ticks_x))

ggsave (file=name_out)

tbl_stat_mean <- with (data.frame_bed, aggregate (cbind (V5), list (phenotype=phenotype, data_type=data_type, phase=phase), 
                                                  FUN=function (x) c (mean=mean(x), std.error=std.error(x))))

tbl_stat_mean$mean <- tbl_stat_mean$V5 [,1]
tbl_stat_mean$std.error <- tbl_stat_mean$V5 [,2]

name_out_bar <- paste (path2plot, name_file, "_bar", ".", "png", sep="")

ggplot(data=tbl_stat_mean, aes(x=phase, y=mean, fill=data_type)) + 
  geom_bar(stat="identity", position=position_dodge()) +
  scale_fill_manual(values = c(cbb_palette[2], cbb_palette[1])) +
  geom_errorbar(aes(ymin=mean-std.error, ymax=mean+std.error),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  facet_grid(.~phenotype) +
  theme(strip.background = element_rect(fill="white")) +
  theme(strip.text.x = element_text(size = size_axis_ticks_x)) +
  labs (title = paste(plot_title,  "\n", sep="")) +
  labs (y = paste(paste (axis_title, "\n", sep="")), x="\nPhase") +  
  theme (plot.title = element_text(size=size_titles)) + 
  theme (axis.title.x = element_text(size=size_axis)) +
  theme (axis.title.y = element_text(size=size_axis)) +
  theme (axis.text.x = element_text(size=size_axis_ticks_x)) +  
  theme (axis.text.y = element_text(size=size_axis_ticks_y)) 

ggsave (file=name_out_bar)

# ggplot(data.frame_bed, aes(x=phase, y=V5, colour=phase, fill=data_type)) +
#   ## standard deviation
#   stat_summary(fun.data=mean_and_sd, geom="crossbar", width=0.4, lwd=1, position=position_dodge()) +
#   scale_fill_manual(values = c(cbb_palette[2], cbb_palette[1])) +
#   stat_summary(fun.data=mean_and_se, geom="crossbar", width=0.4, fatten=3, #colour=cbb_palette[8], 
#                position=position_dodge()) +
#   scale_fill_manual(values = c(cbb_palette[8], cbb_palette[8])) +
#   facet_grid(.~phenotype)
#   #   # mean in orange
# #   stat_summary(fun.data=mean_for_cross, geom="crossbar", width=0.3, size=0.3, colour=cbb_palette[5]) +
# #   scale_colour_manual(values = c(cbb_palette[6], cbb_palette[3])) +
# #   ## plots means as dots  
# #   geom_point(position = position_jitter(w = 0.12, h = 0), size=0.25) +
# #   
# #     # mean in orange
# #     stat_summary(fun.data=mean_for_cross, geom="crossbar", width=0.3, size=0.3, colour=cbb_palette[5]) +
#     scale_colour_manual(values = c(cbb_palette[6], cbb_palette[3])) +
# #     ## plots means as dots  
# #     geom_point(position = position_jitter(w = 0.12, h = 0), size=0.25) +
# #     labs (title = paste("Plot title", "\n", sep="")) +
# #     labs (y = paste(paste ("Plot title", "\n", sep="")), x="\nGroup") +  
# #   theme (plot.title = element_text(size=size_titles)) + 
# #   theme (axis.title.x = element_text(size=size_axis)) +
# #   theme (axis.title.y = element_text(size=size_axis)) +
# #   theme (axis.text.x = element_text(size=size_axis_ticks_x)) +  
# #   theme (axis.text.y = element_text(size=size_axis_ticks_y)) +
# #   theme (axis.text.x = element_text(angle=-90, vjust=0.4,hjust=1)) +
#   facet_grid(.~phenotype) +
#   theme(strip.background = element_rect(fill="white")) +
#   theme(strip.text.x = element_text(size = size_axis_ticks_x))