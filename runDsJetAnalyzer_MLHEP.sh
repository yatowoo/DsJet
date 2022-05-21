#!/bin/bash - 

workdir=$HOME/work/DsJet-test
workdir_data=$workdir/pp_data

rundir=$HOME/MachineLearningHEP/machine_learning_hep

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
database=db/database_ml_parameters_DsJet_test.yml
submission=db/submission_DsJetAnalyzer.yml
analysis=jet_FF
config_name=$1
log_name=~/log/runDsJet-$config_name-$(date +%Y%m%d%H%M).log

# Run analysis
cd $rundir
nice python do_entire_analysis.py -r $SCRIPTPATH/$submission -d $SCRIPTPATH/$database -a $analysis 2>&1 | tee $log_name

# Clean dir by year
cd $workdir/../
cp -a $workdir ana-$config_name
tar cvf ana-$config_name.tar.gz ana-$config_name/
cd $rundir
