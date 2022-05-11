#!/bin/bash - 

workdir=/home/yitao/work/DsJet-test
workdir_data=$workdir/pp_data

rundir=/home/yitao/MachineLearningHEP/machine_learning_hep

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
database=database_ml_parameters_DsJet_test.yml
submission=submission_DsJet.yml
analysis=jet_FF
config_name=$1
log_name=~/log/runDsJet-$config_name-$(date +%Y%m%d%H%M).log

# Empty work dir
if [ -z $workdir_data ];then
  echo "[X] Work dir not empty : "$workdir_data
  exit
fi

# Run analysis
cd $rundir
nice python do_entire_analysis.py -r $SCRIPTPATH/$submission -d $SCRIPTPATH/$database -a $analysis 2>&1 | tee $log_name

# Clean dir by year
rm -rf $workdir/pp_20*
cp -a $workdir ~/work/ana-$config_name
rm -rf $workdir/*
tar cvf ~/work/ana-$config_name.tar.gz ~/work/ana-$config_name/ 
