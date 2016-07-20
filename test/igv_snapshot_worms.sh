#!/usr/bin/env bash

# How to run the script
# cd /Users/jespinosa/git/pergola/test/
# sh igv_snapshot_worms.sh |  telnet 127.0.0.1 60151
mkdir -p $HOME/2016_worm_DB/tmp
file_type=".png"
# tag=""${file_type}
tag="_noNamePanel"${file_type}
# tag="_noNamePanel_noHeader"${file_type}
# name_f="N2_"
name_f="heatMap_unc16_"
sleep 2
echo "snapshotDirectory $HOME/2016_worm_DB/tmp"
sleep 2
echo "goto chr1"
sleep 2
echo "snapshot ${name_f}all_period${tag}"
sleep 2
echo "goto chr1:1-2,000"
sleep 2
echo "snapshot ${name_f}region1${tag}"
sleep 2
echo "goto chr1:12,000-14,000"
sleep 2
echo "snapshot ${name_f}region2${tag}"
sleep 2
# file_type=".svg"
# tag=""${file_type}
tag="_noNamePanel"${file_type}
# tag="_noNamePanel_noHeader"${file_type}
# name_f="N2_"
name_f="heatMap_unc16_"
sleep 2
echo "snapshotDirectory $HOME/2016_worm_DB/tmp"
sleep 2
echo "goto chr1"
sleep 2
# echo "snapshot ${name_f}all_period${tag}"
sleep 2
echo "goto chr1:1-2,000"
sleep 2
# echo "snapshot ${name_f}region1${tag}"
sleep 2
echo "goto chr1:12,000-14,000"
sleep 2
# echo "snapshot ${name_f}region2${tag}"
sleep 2


#  name_f="heatMap_unc16_"
# echo "goto chr1:1-23,000"
# sleep 2
# echo "snapshot ${name_f}region1${tag}"
# sleep 10
# echo "goto chr1:10,000-12,000"
# sleep 2
# echo "snapshot ${name_f}region2${tag}"
# sleep 10
