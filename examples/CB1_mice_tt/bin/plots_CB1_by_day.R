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
library('extrafont')
library ('gtools') 
library(dplyr)

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
      --stat=someValue        - character, stat to analyze (sum, mean, ...)
      --path2files=someValue - character, path to read files
      --path2plot=someValue  - character, path to dump plots
      --help                 - print this text
      
      Example:
      ./starting_regions_file_vs_24h.R --stat=\"sum\" --path2plot=\"/foo/plots\"\n")
  
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

# stat is mandatory
{
  if (is.null (argsL$stat)) 
  {
    stop ("[FATAL]: Stat parameter is mandatory")
  }
  else
  {
    stat <- argsL$stat
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
# source("https://raw.githubusercontent.com/cbcrg/mwm/master/lib/R/plot_param_public.R")

write(paste("Path to files: ", path2files, sep=""), stderr())
# path2files <- "/Users/jespinosa/git/pergola/examples/CB1_mice_tt/results_by_day/feeding_by_phases/sum/"

# stat <- 'sum'
setwd(path2files)

files <- list.files(pattern=paste("tr_.*.bed$", sep=""))

data.frame_bed <- NULL

for (bed_file in files) {
  
  info = file.info (bed_file)
  if (info$size == 0) { next }
  df <- read.csv(bed_file, header=F, sep="\t")
#   df <- read.csv("tr_KO_cb1_nicotine.12.food_fat.dark.Basal.bed", header=F, sep="\t")
  phenotype <- gsub ("tr_", "", unlist(strsplit(bed_file, split=".",fixed=T))[1])
#   treatment <- gsub ("tr_", "", unlist(strsplit(bed_file, split=".",fixed=T))[2])
  genotype <- unlist(strsplit(phenotype, split="_",fixed=T))[1]
  mouse <- gsub ("tr_", "", unlist(strsplit(bed_file, split=".",fixed=T))[2])
  data_type <- gsub ("tr_", "", unlist(strsplit(bed_file, split=".",fixed=T))[3])
  data_type <- gsub ("food_fat", "HF", data_type)
  data_type <- gsub ("food_sc", "SC", data_type)
  phase <- gsub ("tr_", "", unlist(strsplit(bed_file, split=".",fixed=T))[4])
  exp_phase <- gsub ("tr_", "", unlist(strsplit(bed_file, split=".",fixed=T))[5])
  df$phenotype <- phenotype
  df$phenotype <- factor(df$phenotype, levels=c("wt_saline", "wt_nicotine", "KO_cb1_saline", "KO_cb1_nicotine"), 
                         labels=c("wt_saline", "wt_nicotine", "KO_cb1_saline", "KO_cb1_nicotine"))
  df$mouse <- mouse
  df$genotype <- genotype
  df$genotype <- factor(df$genotype, levels=c("wt", "KO"), 
                       labels=c("wt", "KO"))
#   df$treatment <- treatment 
  df$mouse <- mouse
  df$data_type <- data_type
  df$phase <- phase
  df$exp_phase <- gsub("_", " ", exp_phase)
  df$group2plot <- paste (phase, data_type)
  data.frame_bed <- rbind(data.frame_bed, df)
}
subset(data.frame_bed, V4=='no_hits')

## el animal 29 no tiene datos para el nicotine treatment
## 3799 chr1  0  1 no_hits  0  0     wt_saline    29        SC   day  Nicotine treatment     day SC
to_replace <- subset(data.frame_bed, mouse=='1' & exp_phase=="Nicotine treatment" & data_type=="SC")
to_replace$V6 <- 0
data.frame_bed <- rbind(to_replace, data.frame_bed)

#######
# In the analysis of the original paper they substitute empty values for an animal
# for the medians, but not only for these days but for the whole experimental    
# period during which the empty values was occurring
# This part of the code will be use to preprocess the data and use the same approach
# in order to reproduce the plots they published
#######
# Ojo I am working with counts right now
subset (data.frame_bed, exp_phase=="Basal")
subset (data.frame_bed, exp_phase=="Basal" & phenotype=="KO_cb1_nicotine" & V6==0 & V4=="day_4")

nzmean <- function(x) {
  zvals <- x==0
  if (all(zvals)) 0 else mean(x[!zvals])
}

means_no_zeros <- with (data.frame_bed, aggregate (cbind (V6), list (genotype=genotype, data_type=data_type,
                                                     exp_phase=exp_phase, day=V4 ), 
                                   FUN=function (x) c (mean=nzmean(x))))

# means_zeros <- with (data.frame_bed, aggregate (cbind (V6), list (genotype=genotype, data_type=data_type,
#                                                                    exp_phase=exp_phase, day=V4 ), 
#                                                  FUN=function (x) c (mean=mean(x))))


for (i in c(1:length (data.frame_bed$exp_phase))) {
  if (data.frame_bed [i,"V6"] == 0) {
    # si ya he cambiado un dia el resto ya no son 0
    # tengo que cambiar por el valor medio del resto en ese dia
#     print (data.frame_bed [i,])
    data.frame_bed [i,"V6"] <- subset(means_no_zeros, genotype==data.frame_bed [i,"genotype"] &                                       
                                      exp_phase==data.frame_bed [i,"exp_phase"] & 
                                      data_type==data.frame_bed [i,"data_type"] & 
                                      day==data.frame_bed [i,"V4"], select=c("V6"))
  }
} 

## delete the first 4 days of the nicotine tt -> injection
data.frame_bed <- subset (data.frame_bed, V4!="day_15" & V4!="day_16" & V4!="day_17" & V4!="day_18")



########################
  
  


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
{
  if ('HF' %in% data.frame_bed$data_type & 'SC' %in% data.frame_bed$data_type) {
    cbb_palette <- c("#E69F00", "#000000", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7")
    bouts_title <- "Feeding bouts"
    units <- 'g'
    filter_pref <- 'HF'
  }
  else if ('water' %in% data.frame_bed$data_type & 'saccharin' %in% data.frame_bed$data_type) {
    cbb_palette <- c("#0072B2", "#D55E00", "#E69F00", "#000000", "#56B4E9", "#009E73", "#F0E442", "#CC79A7")
    bouts_title <- "Drinking bouts"
    units <- 'mL'
    filter_pref <- 'saccharin'
  }
  else {
    cbb_palette <- c("#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7")
    bouts_title <- "Number of bouts"
    units <- 'no units'
  }
}
size_titles <- 20
size_axis <- 18
size_axis_ticks_x <- 14
size_axis_ticks_y <- 14
size_strip_txt <- 14
plot_width <- 12
plot_height <- 10 
font <- "Arial"

name_file <- "plot"
name_out <- paste (path2plot, stat, "_", name_file, ".", "png", sep="")

plot_title <- switch (stat, count=bouts_title, mean="Mean intake per feeding bout", median='Median intake per feeding bout', sum='Accumulated intake', 
                      max='Maximun intake', '')
axis_title <- switch (stat, count="Number of bouts", mean=units, median=units, sum=units, max=units, 'no units' )

ggplot(data.frame_bed, aes(x=group2plot, y=V6, colour=phase, fill=data_type)) +
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
  theme (plot.title = element_text(family=font, size=size_titles)) + 
  theme (axis.title.x = element_text(family=font, size=size_axis)) +
  theme (axis.title.y = element_text(family=font, size=size_axis)) +
  theme (axis.text.x = element_text(family=font, size=size_axis_ticks_x, angle=-90)) +  
  theme (axis.text.y = element_text(family=font, size=size_axis_ticks_y)) +
  theme (axis.text.x = element_text(family=font, angle=-90, vjust=0.4,hjust=1)) +
  facet_grid(phenotype~exp_phase) +
  theme(strip.background = element_rect(fill="white"), strip.text = element_text(family=font, size = size_strip_txt)) +
  theme(legend.title=element_blank())

ggsave (file=name_out, width = plot_width, height=plot_height)

tbl_stat_mean <- with (data.frame_bed, aggregate (cbind (V6), list (phenotype=phenotype, data_type=data_type, phase=phase,
                                                                    exp_phase=exp_phase), 
                                                  FUN=function (x) c (mean=mean(x), std.error=std.error(x))))

tbl_stat_mean$mean <- tbl_stat_mean$V6 [,1]
tbl_stat_mean$std.error <- tbl_stat_mean$V6 [,2]

## Combined phases as in the original paper
tbl_stat_mean_comb_ph <- with (data.frame_bed, aggregate (cbind (V6), list (phenotype=phenotype, data_type=data_type,
                                                                    exp_phase=exp_phase), 
                                                  FUN=function (x) c (mean=mean(x), std.error=std.error(x))))

tbl_stat_mean_comb_ph$mean <- tbl_stat_mean_comb_ph$V6 [,1]
tbl_stat_mean_comb_ph$std.error <- tbl_stat_mean_comb_ph$V6 [,2]
# 22.48/(22.48+3.39) 86 vs 90
name_out_bar <- paste (path2plot, stat, "_", name_file, "_bar", ".", "png", sep="")

ggplot(data=tbl_stat_mean, aes(x=phase, y=mean, fill=data_type)) + 
  geom_bar(stat="identity", position=position_dodge()) +
  scale_fill_manual(values = c(cbb_palette[2], cbb_palette[1])) +
  geom_errorbar(aes(ymin=mean-std.error, ymax=mean+std.error),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  facet_grid(phenotype~exp_phase) +
  theme(strip.background = element_rect(fill="white"), strip.text = element_text(family=font, size = size_strip_txt)) +
  labs (title = paste(plot_title,  "\n", sep="")) +
  labs (y = paste(paste (axis_title, "\n", sep="")), x="\nPhase") +  
  theme (plot.title = element_text(family=font, size=size_titles)) + 
  theme (axis.title.x = element_text(family=font, size=size_axis)) +
  theme (axis.title.y = element_text(family=font, size=size_axis)) +
  theme (axis.text.x = element_text(family=font, size=size_axis_ticks_x, angle=-90)) +  
  theme (axis.text.y = element_text(family=font, size=size_axis_ticks_y)) +
  theme(legend.title=element_blank())

ggsave (file=name_out_bar, width=plot_width, height=plot_height, dpi=300)

name_out_bar_comb_phases <- paste (path2plot, stat, "_", name_file, "_bar_comb_phases", ".", "png", sep="")
ggplot(data=tbl_stat_mean_comb_ph, aes(x=phenotype, y=mean, fill=data_type)) + 
  geom_bar(stat="identity", position=position_dodge()) +
  scale_fill_manual(values = c(cbb_palette[2], cbb_palette[1])) +
  geom_errorbar(aes(ymin=mean-std.error, ymax=mean+std.error),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  facet_grid(.~exp_phase) +
  theme(strip.background = element_rect(fill="white"), strip.text = element_text(family=font, size = size_strip_txt)) +
  labs (title = paste(plot_title,  "\n", sep="")) +
  labs (y = paste(paste (axis_title, "\n", sep="")), x="\nPhenotype") +  
  theme (plot.title = element_text(family=font, size=size_titles)) + 
  theme (axis.title.x = element_text(family=font, size=size_axis)) +
  theme (axis.title.y = element_text(family=font, size=size_axis)) +
  theme (axis.text.x = element_text(family=font, size=size_axis_ticks_x, angle=-90)) +  
  theme (axis.text.y = element_text(family=font, size=size_axis_ticks_y)) +
  theme(legend.title=element_blank())

ggsave (file=name_out_bar_comb_phases, width=plot_width, height=plot_height, dpi=300)

# detach("package:plyr")
####################
## relative frequencies of counts
{
  if (stat == 'count' | stat == 'sum'){
    data.frame_bed$value <- data.frame_bed$V6
    # getting relative frequencies
    rel_freq <- data.frame_bed %>%
      group_by(phenotype, exp_phase, phase, data_type) %>%
      summarise(mean=mean(value)) %>%
      mutate(freq=mean/sum(mean), pos = (cumsum(mean/sum(mean)) - 0.5 * mean/sum(mean)))
    
    rel_freq <- as.data.frame(rel_freq)
    rel_freq_dark <- subset(rel_freq, phase=="dark")
    rel_freq_light <- subset(rel_freq, phase=="light") 
    
    tbl_fold_change <- NULL
    tbl_fold_change <- rel_freq_light
    tbl_fold_change$freq_dark <- rel_freq_dark$freq
    tbl_fold_change$mean_dark <- rel_freq_dark$mean
    tbl_fold_change$ratio <- rel_freq_light$freq / rel_freq_dark$freq
    tbl_fold_change$fold_change <- foldchange(rel_freq_light$freq, rel_freq_dark$freq)
    tbl_fold_change$log_ratio2 <- log2(tbl_fold_change$ratio)

    name_out_rel_freq <- paste (path2plot, stat, "_", name_file, "_rel_freq", ".", "png", sep="") 
    
    ggplot(data=tbl_stat_mean, aes(x=phase, y=mean, fill=data_type)) + 
      geom_bar(stat="identity", position="fill") +
      scale_fill_manual(values = c(cbb_palette[2], cbb_palette[1])) +
      geom_text(data = tbl_fold_change, aes(x=phase, y = pos, label = round(log_ratio2,2)), size = 4, colour = 'white') +
      facet_grid(phenotype~exp_phase) +
      theme(strip.background = element_rect(fill="white"), strip.text = element_text(family=font, size = size_strip_txt)) +
      labs (title = paste(plot_title,  "\n", sep="")) +
      labs (y = "Relative frequency\n", x="\nPhase") +
      theme (plot.title = element_text(family=font, size=size_titles)) + 
      theme (axis.title.x = element_text(family=font, size=size_axis)) +
      theme (axis.title.y = element_text(family=font, size=size_axis)) +
      theme (axis.text.x = element_text(family=font, size=size_axis_ticks_x, angle=-90)) +  
      theme (axis.text.y = element_text(family=font, size=size_axis_ticks_y)) +
      theme(legend.title=element_blank())
    
    ggsave (file=name_out_rel_freq, width=plot_width, height=plot_height, dpi=300)
    
    name_out_rel_freq_comb <- paste (path2plot, stat, "_", name_file, "_rel_freq_comb_phases", ".", "png", sep="")       
    
    ggplot(data=tbl_stat_mean_comb_ph, aes(x=phenotype, y=mean, fill=data_type)) + 
      geom_bar(stat="identity", position="fill") +
      scale_fill_manual(values = c(cbb_palette[2], cbb_palette[1])) +
      geom_text(data = tbl_fold_change, aes(x=phase, y = pos, label = round(log_ratio2,2)), size = 4, colour = 'white') +
      facet_grid(.~exp_phase) +
      theme(strip.background = element_rect(fill="white"), strip.text = element_text(family=font, size = size_strip_txt)) +
      labs (title = paste(plot_title,  "\n", sep="")) +
      labs (y = "Relative frequency\n", x="\nPhenotype") +
      theme (plot.title = element_text(family=font, size=size_titles)) + 
      theme (axis.title.x = element_text(family=font, size=size_axis)) +
      theme (axis.title.y = element_text(family=font, size=size_axis)) +
      theme (axis.text.x = element_text(family=font, size=size_axis_ticks_x, angle=-90)) +  
      theme (axis.text.y = element_text(family=font, size=size_axis_ticks_y)) +
      theme(legend.title=element_blank())
    
    ggsave (file=name_out_rel_freq_comb, width=plot_width, height=plot_height, dpi=300)    
  }
}

## In this case I do not compare relative frequencies but directly mean values of 
## the same data_type during dark and light phase
# adding pseudo-accounts
# data.frame_bed$value <- data.frame_bed$V6 + 1

# I calculate the mean of the counts and the other factors
# dark <- with (subset(data.frame_bed, phase=="dark"), aggregate (cbind (value), list (phenotype=phenotype, data_type=data_type,
#                                                                           exp_phase=exp_phase),
#                                                         FUN=function (x) c (mean=mean(x))))
# light <- with (subset(data.frame_bed, phase=="light"), aggregate (cbind (value), list (phenotype=phenotype, data_type=data_type,
#                                                                           exp_phase=exp_phase),
#                                                         FUN=function (x) c (mean=mean(x))))

# tbl_fold_change <- NULL
# tbl_fold_change <- dark
# tbl_fold_change$value_light <- light$value
# tbl_fold_change$fold_change <- foldchange (tbl_fold_change$value, tbl_fold_change$value_light)
# tbl_fold_change$log_ratio2 <- foldchange2logratio(tbl_fold_change$fold_change,2)


######################
# preference by animal
#preference <- mean_intake HF  / (mean_intake SC + mean_intake HF) They do animal by animal and file by file
{
  if (stat == 'count' | stat == 'sum'){
    
    data.frame_bed$value <- data.frame_bed$V6
    preference <- data.frame_bed %>%
      # lo hace en funcion del ultimo (data type)
      group_by(mouse, phenotype, exp_phase, phase,  V2, V3, data_type) %>%
      summarise(mean=mean(value)) %>%
      mutate(pref=mean/sum(mean)*100)
    preference <- as.data.frame(preference)
    preference <- preference[!is.na(preference$pref),]
    
    preference_mean_comb_ph <- with (preference, aggregate (cbind (pref), list (phenotype=phenotype, data_type=data_type,
                                                                                exp_phase=exp_phase), 
                                                              FUN=function (x) c (mean=mean(x), std.error=std.error(x))))
    
    preference_mean_comb_ph$mean <- preference_mean_comb_ph$pref [,1]
    preference_mean_comb_ph$std.error <- preference_mean_comb_ph$pref [,2]
    
    name_out_bar_preference <- paste (path2plot, stat, "_", name_file, "preference_bars_stderr", ".", "png", sep="")
    
    preference_mean_comb_ph_HF <- subset (preference_mean_comb_ph, data_type==filter_pref)
    ggplot(data=preference_mean_comb_ph_HF, aes(x=phenotype, y=mean, fill=data_type)) + 
      geom_bar(stat="identity", position=position_dodge()) +
      scale_fill_manual(values = c(cbb_palette[2], cbb_palette[1])) +
      scale_y_continuous (breaks=seq(0, 100,20), limits=c(0, 100)) +
      geom_errorbar(aes(ymin=mean-std.error, ymax=mean+std.error),
                    width=.2,                    # Width of the error bars
                    position=position_dodge(.9)) +
      labs (title = paste(plot_title, "\n", sep="")) +
      labs (y = paste(paste ("Percentage", "\n", sep="")), x="\n") +  
      theme (plot.title = element_text(family=font, size=size_titles)) + 
      theme (axis.title.x = element_text(family=font, size=size_axis)) +
      theme (axis.title.y = element_text(family=font, size=size_axis)) +
      theme (axis.text.x = element_text(family=font, size=size_axis_ticks_x, angle=-90)) +  
      theme (axis.text.y = element_text(family=font, size=size_axis_ticks_y)) +
      theme (axis.text.x = element_text(family=font, angle=-90, vjust=0.4,hjust=1)) +
      guides(fill=FALSE) +
      facet_grid(.~exp_phase) 
    ggsave (file=name_out_bar_preference, width=plot_width, height=plot_height, dpi=300)   
    
    name_out_rel_freq_preference <- paste (path2plot, stat, "_", name_file, "_preference_relFreq", ".", "png", sep="")
    
    ggplot(data=preference_mean_comb_ph, aes(x=phenotype, y=mean, fill=data_type)) + 
      geom_bar(stat="identity", position="fill") +
      scale_fill_manual(values = c(cbb_palette[2], cbb_palette[1])) +
      scale_y_continuous (breaks=seq(0, 1,0.2)) +
      labs (title = paste(plot_title, "\n", sep="")) +
      labs (y = paste(paste ("Percentage", "\n", sep="")), x="\n") +  
      theme (plot.title = element_text(family=font, size=size_titles)) + 
      theme (axis.title.x = element_text(family=font, size=size_axis)) +
      theme (axis.title.y = element_text(family=font, size=size_axis)) +
      theme (axis.text.x = element_text(family=font, size=size_axis_ticks_x, angle=-90)) +  
      theme (axis.text.y = element_text(family=font, size=size_axis_ticks_y)) +
      theme (axis.text.x = element_text(family=font, angle=-90, vjust=0.4,hjust=1)) +
      facet_grid(.~exp_phase)
    
    ggsave (file=name_out_rel_freq_preference, width=plot_width, height=plot_height, dpi=300)
  }
}


# same thing but only with basal
data.frame_bed_basal <- subset (data.frame_bed, exp_phase=="Basal")
# data.frame_bed_basal <-  gsub(data.frame_bed_basal$)

head(data.frame_bed)
{
  if (stat == 'count' | stat == 'sum'){
    
    data.frame_bed_basal$value <- data.frame_bed_basal$V6
    preference <- data.frame_bed_basal %>%
      # lo hace en funcion del ultimo (data type)
      group_by(mouse, genotype, exp_phase, phase,  V2, V3, data_type) %>%
      summarise(mean=mean(value)) %>%
      mutate(pref=mean/sum(mean)*100)
    preference <- as.data.frame(preference)
    preference <- preference[!is.na(preference$pref),]
    
    preference_mean_comb_ph <- with (preference, aggregate (cbind (pref), list (genotype=genotype, data_type=data_type,
                                                                                exp_phase=exp_phase), 
                                                            FUN=function (x) c (mean=mean(x), std.error=std.error(x))))
    
    preference_mean_comb_ph$mean <- preference_mean_comb_ph$pref [,1]
    preference_mean_comb_ph$std.error <- preference_mean_comb_ph$pref [,2]
    
    name_out_bar_preference <- paste (path2plot, stat, "_", name_file, "preference_bars_stderr_basal", ".", "png", sep="")
    
    preference_mean_comb_ph_HF <- subset (preference_mean_comb_ph, data_type==filter_pref)
    ggplot(data=preference_mean_comb_ph_HF, aes(x=phenotype, y=mean, fill=data_type)) + 
      geom_bar(stat="identity", position=position_dodge()) +
      scale_fill_manual(values = c(cbb_palette[2], cbb_palette[1])) +
      scale_y_continuous (breaks=seq(0, 100,20), limits=c(0, 100)) +
      geom_errorbar(aes(ymin=mean-std.error, ymax=mean+std.error),
                    width=.2,                    # Width of the error bars
                    position=position_dodge(.9)) +
      labs (title = paste(plot_title, "\n", sep="")) +
      labs (y = paste(paste ("Percentage", "\n", sep="")), x="\n") +  
      theme (plot.title = element_text(family=font, size=size_titles)) + 
      theme (axis.title.x = element_text(family=font, size=size_axis)) +
      theme (axis.title.y = element_text(family=font, size=size_axis)) +
      theme (axis.text.x = element_text(family=font, size=size_axis_ticks_x, angle=-90)) +  
      theme (axis.text.y = element_text(family=font, size=size_axis_ticks_y)) +
      theme (axis.text.x = element_text(family=font, angle=-90, vjust=0.4,hjust=1)) +
      guides(fill=FALSE) +
      facet_grid(.~exp_phase) 
    ggsave (file=name_out_bar_preference, width=plot_width, height=plot_height, dpi=300)   
    
    name_out_rel_freq_preference <- paste (path2plot, stat, "_", name_file, "_preference_relFreq_basal", ".", "png", sep="")
    
    ggplot(data=preference_mean_comb_ph, aes(x=genotype, y=mean, fill=data_type)) + 
      geom_bar(stat="identity", position="fill") +
      scale_fill_manual(values = c(cbb_palette[2], cbb_palette[1])) +
      scale_y_continuous (breaks=seq(0, 1,0.2)) +
      labs (title = paste(plot_title, "\n", sep="")) +
      labs (y = paste(paste ("Percentage", "\n", sep="")), x="\n") +  
      theme (plot.title = element_text(family=font, size=size_titles)) + 
      theme (axis.title.x = element_text(family=font, size=size_axis)) +
      theme (axis.title.y = element_text(family=font, size=size_axis)) +
      theme (axis.text.x = element_text(family=font, size=size_axis_ticks_x, angle=-90)) +  
      theme (axis.text.y = element_text(family=font, size=size_axis_ticks_y)) +
      theme (axis.text.x = element_text(family=font, angle=-90, vjust=0.4,hjust=1)) +
      facet_grid(.~exp_phase)
    
    ggsave (file=name_out_rel_freq_preference, width=plot_width, height=plot_height, dpi=300)
  }
}
