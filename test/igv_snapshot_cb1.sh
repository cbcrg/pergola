#!/usr/bin/env bash

# How to run the script
# cd /Users/jespinosa/git/pergola/test/
# sh igv_snapshot_cb1.sh |  telnet 127.0.0.1 60151
mkdir -p $HOME/phecomp/2016_nicotine_mice/tmp_igv/
# file_type=".png"
file_type=".svg"
# tag="_ctrl_bed_food_sc"${file_type}
# tag="_cb1_bed_food_sc"${file_type}
# tag="_ctrl_bed_food_fat"${file_type}
# tag="_cb1_bed_food_fat"${file_type}
# tag="_phases"${file_type}
# tag="_ctrl_cb1_bedGr_food_sc"${file_type}
# tag="_ctrl_cb1_bedGr_food_fat"${file_type}
# tag="_ctrl_cb1_bedGr_water"${file_type}
# tag="_ctrl_cb1_bedGr_saccharin"${file_type}
# tag="_ctrl_bedGr_food_sc_fat_food_alternate"${file_type}
# tag="_cb1_bedGr_food_sc_fat_food_alternate"${file_type}
# tag="_ctrl_bedGr_liquid_alternate"${file_type}
# tag="_cb1_bedGr_liquid_alternate"${file_type}
# tag="_header"${file_type}
# tag="_phases"${file_type}
# tag="_ctrl_cb1_HF_nicotineWithdrawal"${file_type}
# tag="_ctrl_cb1_SC_nicotineWithdrawal"${file_type}
tag="phaseTrack_withdrawal"${file_type}
sleep 2
echo "snapshotDirectory $HOME/phecomp/2016_nicotine_mice/tmp_igv/"
sleep 2
echo "goto chr1"
# sleep 2
# echo "snapshot all_exp${tag}"
sleep 2
# echo "goto chr1:1,560,381-2,070,991"
# echo "goto chr1:2,426,073-3,635,631"
echo "goto chr1:2,419,200-3,628,800"
sleep 2
echo "snapshot one_week${tag}"
sleep 2
#echo "goto chr1:432,000-604,800"
#sleep 2
#echo "snapshot day_6_7${tag}"
#sleep 2