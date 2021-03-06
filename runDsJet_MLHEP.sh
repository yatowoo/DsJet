#!/bin/bash - 

workdir=$HOME/work/DsJet-test
workdir_data=$workdir/pp_data

rundir=$HOME/MachineLearningHEP/machine_learning_hep

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

if [ -f "$2" ];then
  submission=`realpath $2`
else
  submission=$SCRIPTPATH/db/submission_DsJet.yml
fi

if [ -f "$3" ];then
  database=`realpath $3`
else
  database=$SCRIPTPATH/db/database_ml_parameters_DsJet_test.yml
fi

analysis=jet_FF
config_name=$1
log_name=~/log/runDsJet-$config_name-$(date +%Y%m%d%H%M).log

echo $* > $log_name
set -x
# Empty work dir
if [ -e "$workdir_data" ];then
  echo "[+] WARNING Work dir not empty : "$workdir_data
fi

# Run analysis
cd $rundir
nice python do_entire_analysis.py -r $submission -d $database -a $analysis 2>&1 | tee -a $log_name

# Clean dir by year
exec >> $log_name
exec 2>&1

cd $workdir/../
cp $log_name $workdir/
if [ -d "$workdir/pp_2016_data" ];then
  rm -rf $workdir/pp_20*
fi
if [ -d "$workdir_data" ];then
  cp -a $workdir ~/work/ana-$config_name
  tar czf ana-$config_name.tar.gz ana-$config_name/
  rm $workdir/*.log
  echo "[+] Results saved to "$workdir/$ana-$config_name"[.tar.gz]"
fi
set +x
