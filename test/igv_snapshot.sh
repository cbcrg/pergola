#!/usr/bin/env bash

# How to run the script
# sh igv_snapshot.sh |  telnet 127.0.0.1 60151
mkdir -p $HOME/tmp/igv
sleep 2
echo "snapshotDirectory $HOME/tmp/igv"
sleep 2
echo "goto chr1:1-1,780,869"
sleep 2
echo "snapshot"
sleep 2
echo "goto chr1:919,000-982,000"
sleep 2
echo "snapshot"
sleep 2
