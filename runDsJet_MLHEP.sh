#!/bin/bash - 

workdir=$HOME/work/DsJet-test
output_dir=$HOME/work/Results
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
log_file=~/log/runDsJet-$config_name-$(date +%Y%m%d%H%M).log

exec &> >(tee "$log_file")
echo $SCRIPT $*
set -x
# Empty work dir
if [ -e "$workdir_data" ];then
  echo "[+] WARNING Work dir not empty : "$workdir_data
fi

# Run analysis
cd $rundir
nice python do_entire_analysis.py -r $submission -d $database -a $analysis

cd $output_dir
cp $log_file $workdir/
# Clean dir by year
if [ -d "$workdir/pp_2016_data" ];then
  rm -rf $workdir/pp_20*
fi
if [ -d "$workdir_data" ];then
  archive_dir=$output_dir/ana-$config_name
  rm -rf $archive_dir
  cp -a $workdir $archive_dir
  tar czf $output_dir/ana-$config_name.tar.gz ana-$config_name/
  rm $workdir/*.log
  echo "[+] Results saved to "$output_dir/ana-$config_name".tar.gz"
fi
set +x
echo "[-] Log file : "$log_file
