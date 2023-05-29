#!/bin/bash

# $1 num of trajectories
# $2 working directory

cd $2/traj/

rm -rf *

for i in $(seq 0 $1); do
  tmpi=$(printf "%02d" $i)
  mkdir -p "$tmpi"
  cp -r /home/project/11002298/long/testsg/em_real/* ./$tmpi/

  # for j in $(seq 0 $2); do
  #   tmpj=$(printf "%02d" $j)
  #   mkdir -p "$tmpi/$tmpj"
  # done
done