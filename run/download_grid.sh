#!/bin/bash -

# Script to download files from the Grid

# Path: alien:///alice/sim/2020/LHC20f4a/$(run)/AOD235/$(subjob)

filenames=(AnalysisResults.root)
alien_path=alien://$1
outputdir=$2
echo "[-] Copy $alien_path to $outputdir"
for subjob in $(alien_ls $alien_path | grep -e "0.*/");
do
  subpath=$outputdir/$subjob
  echo "> Processing "$subpath;
  mkdir -p $subpath;
  for file in ${filenames[@]};
  do
    echo ">> Downloading "$subpath/$file;
    alien_cp -f -retry 3 $alien_path/$subjob/$file file:$subpath/
  done
done
