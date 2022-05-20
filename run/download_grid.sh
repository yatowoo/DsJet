#!/bin/bash -

# Script to download files from the Grid

# Path: alien:///alice/sim/2020/LHC20f4a/$(run)/AOD235/$(subjob)

prodType=sim
prod=2020/LHC20f4a
runnumber=$1
filenames=(AliAOD.root AliAOD.VertexingHF.root)
alien_path=alien:///alice/$prodType/$prod/$runnumber/AOD235
for subjob in $(alien_ls $alien_path | grep -e "0.*/");
do
  subpath=$runnumber/$subjob
  echo "> Processing "$subpath;
  mkdir -p $subpath;
  for file in $filenames;
  do
    echo ">> Downloading "$subpath;
    alien_cp -a -retry 3 $alien_path/$subjob/$file file:$subpath/
  done
done