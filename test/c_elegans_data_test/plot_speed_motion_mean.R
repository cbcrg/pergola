#############################################################################
### Jose A Espinosa. NPMMD/CB-CRG Group. Apr 2015                         ###
#############################################################################
### Mean values for each group of worms                                   ###
### Using bed files raw data intercepted with the motion                  ### 
#############################################################################

# To use this script in ant first export this:
# export R_LIBS="/software/R/packages"

### Execution example
## Rscript plot_speed_motion_mean.R --body_part="midbody" --pattern_worm="575_ju440" --motion="backward"
## Rscript plot_speed_motion_mean.R --body_part="midbody" --pattern_worm="N2" --motion="forward"
library (ggplot2)

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
      --body_part=someValue          - character
      --pattern_worm=someValue       - character
      --motion=someValue     - character
      --help                         - print this text
      
      Example:
      ./plot_speed_motion_mean.R --body_part=\"midbody\" --pattern_worm=\"575_JU440\" --motion=\"forward\" \n")
  
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
  if (is.null (argsL$body_part)) 
  {
    stop ("[FATAL]: body_part arg is mandatory")
  }
  else
  {
    body_part <- argsL$body_part
  }
}

{
  if (is.null (argsL$pattern_worm)) 
  {
    stop ("[FATAL]: pattern_worm arg is mandatory")
  }
  else
  {    
    pattern_worm <- argsL$pattern_worm
  }
}

{
  if (is.null (argsL$motion)) 
  {
    stop ("[FATAL]:  motion arg is mandatory")
    #     path2files <- "/Users/jespinosa/20150515_PCA_old_frotiersPaper/data/Ts65Dn_OLD_ACQ1_ACQ5_SUBCONJ.sav"
  }
  else
  {
    motion <- argsL$motion
  }
}

# 575_JU440*_worm_forward.csv.motion.bed
#listFiles <- list.files (path ="./results_motion_GB/" , pattern = pattern_files) #deb #del
# 
# motion -->backward
wd <- getwd()
path2files <- "/users/cn/jespinosa/git/pergola/test/c_elegans_data_test/results_intersect/"
# path2files <- "/Users/jespinosa/git/pergola/test/c_elegans_data_test/results_intersect/"
setwd(path2files)

# values2print <- paste ("INFO: Prints to stderr:", pattern_worm, body_part, motion, sep="==")
# write (values2print, stderr())

pattern_files = paste(body_part, ".", pattern_worm, ".*.", motion, "\\.csv\\.intersect\\.bed$", sep="")
list_files <- list.files (path = ".", pattern = pattern_files, ignore.case=TRUE)

tbl_bed <- do.call ("rbind", lapply(list_files, function(fn) 
                                                data.frame(Filename=fn, read.csv(fn, header=F, sep="\t"))
                                                ))

setwd(wd)

ggplot(tbl_bed, aes(x=V5)) + geom_density() + xlim (c(min(tbl_bed$V5)-50, max(tbl_bed$V5)+50))
ggsave(file=paste(pattern_worm, body_part, motion, "plot.png", sep="_"))