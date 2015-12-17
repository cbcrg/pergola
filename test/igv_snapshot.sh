#!/usr/bin/env bash

# How to run the script
# cd /Users/jespinosa/git/pergola/test/
# sh igv_snapshot.sh |  telnet 127.0.0.1 60151
mkdir -p $HOME/tmp/igv
sleep 2
echo "snapshotDirectory $HOME/tmp/igv"
sleep 2
#echo "goto chr1:1-1,780,869"
echo "goto chr1"
sleep 2
echo "snapshot region.svg"
sleep 2
echo "goto chr1:919,000-982,000"
sleep 2
echo "snapshot region_two.svg"
sleep 2
echo "goto chr1:875,146-880,644"
sleep 2
echo "snapshot region_three.svg"
sleep 2
echo "goto chr1:820,802-950,400"
sleep 2
echo "snapshot region_four.svg"
sleep 2
# First two light phases of development
echo "goto chr1:563,700-691,200"
sleep 2
echo "snapshot dev_ini.svg"
sleep 2
# Development phase
echo "goto chr1:563,646-1,780,869"
sleep 2
echo "snapshot dev.svg"
sleep 2