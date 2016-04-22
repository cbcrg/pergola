#############################################################################
### Jose A Espinosa. NPMMD/CB-CRG Group. Apr 2015                         ###
#############################################################################
### Mean values for each group of worms                                   ###
### Using bed files raw data intercepted with the motion                  ### 
#############################################################################

# To use this script in ant first export this:
# export R_LIBS="/software/R/packages"

##Getting HOME directory 
home <- Sys.getenv("HOME")

### Execution example
## Rscript plot_speed_motion_mean.R --body_part="midbody" --pattern_worm="575_ju440" --motion="backward"
## Rscript plot_speed_motion_mean.R --body_part="midbody" --pattern_worm="N2" --motion="forward"

# ggplot2 package loaded locally, cluster version is older and is causing problems
library(ggplot2, lib.loc="/users/cn/jespinosa/R/library")

# Loading params plot:
source (paste (home, "/git/mwm/lib/R/plot_param_public.R", sep=""))

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

# bed_file<-"/Users/jespinosa/git/pergola/test/c_elegans_data_test/work/tmp/2a/44c5b934c39a3af6a8318fd61127f8/headTip_575_JU440_backward"

df_bed <- read.csv(file=bed_file, header=F, sep="\t")

name_file <- basename(bed_file)
name_out <- paste(name_file, ".png", sep="")

name_split <- strsplit (name_file, "_" )

body_part <- name_split[[1]][1]
motion <- name_split[[1]][length(name_split[[1]])]

{
  if (length(name_split[[1]]) > 3) {
    pattern_worm <- paste(name_split[[1]][2], name_split[[1]][3], sep="_")
  }
  else {
    pattern_worm <- name_split[[1]][2]
  }
}

ggplot(df_bed, aes(x=V5)) + geom_density() + xlim (c(-1000, 1000)) +
  # c(min(tbl_bed$V5)-200, max(tbl_bed$V5)+200)
  labs (title = paste(pattern_worm, motion, body_part, "\n", sep=" "))

ggsave(file=name_out)
