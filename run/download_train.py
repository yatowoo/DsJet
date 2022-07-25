#!/usr/bin/env python3

# Download output from LEGO train
# Refer: https://github.com/ginnocen/MachineLearningHEP/tree/master/cplusutilities
# Env: AliPhysics or any modules with JAliEn commands alien_cp/ls
# Preparation: alien-token-init [user]
# Parameters: train_id, top_save_dir, train_name=PWGHF/HF_TreeCreator

# AliEn path:
# - MC: /alice/sim/2020/LHC20f4c/264347/AOD235/PWGHF/HF_TreeCreator/706_20220720-1829_child_1/AOD/001/AnalysisResults.root
# - Data: /alice/data/2018/LHC18e/000286937/pass1/AOD264/PWGHF/HF_TreeCreator/705_20220720-1829_child_2/AOD/001/AnalysisResults.root
# Local path:
# - MC: D0DsLckINT7HighMultCalo_withJets/vAN-20220720_ROOT6-1/pp_sim/705_20220720-1829/unmerged/child_12/000293368/001/AnalysisResults.root
# - Data: D0DsLckINT7HighMultCalo_withJets/vAN-20220720_ROOT6-1/pp_data/705_20220720-1829/unmerged/child_12/000293368/001/AnalysisResults.root
# Search pattern: PWGHF/HF_TreeCreator/705_20220720-1829_child_2/AOD

import os, sys
import datetime
import subprocess
import multiprocessing as mp
import argparse
from pprint import pprint
from copy import deepcopy

def query_yes_no(question, default="yes"):
  valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
  if default is None:
    prompt = " [y/n] "
  elif default == "yes":
    prompt = " [Y/n] "
  elif default == "no":
    prompt = " [y/N] "
  else:
    raise ValueError("invalid default answer: '%s'" % default)

  while True:
    print(question + prompt)
    choice = input().lower()
    if default is not None and choice == "":
      return valid[default]
    elif choice in valid:
      return valid[choice]
    else:
      print("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

def print_cmd(cmd : list):
  print(' '.join(cmd))

def check_alien_file(path_raw):
  """
  """

def check_local_file(path_raw, overwrite=False):
  if not os.path.exists(path_raw):
    return False
  elif not overwrite:
    return True
  elif query_yes_no(f'{path_raw} existed. Overwrite? '):
    return False
  else:
    return True

def path_local(path_raw):
  return path_raw if path_raw.startswith('file:') else f'file:{path_raw}'
def path_alien(path_raw):
  return path_raw if path_raw.startswith('alien://') else f'alien://{path_raw}'

def find_alien(path_dir, pattern='', args='', **subproc_args):
  """
  """
  cmd = ['alien_find', path_alien(path_dir), pattern, args]
  print_cmd(cmd)
  proc = subprocess.run(cmd, stdout=subprocess.PIPE, **subproc_args)
  ret = proc.stdout.decode('utf-8')
  return ret.split('\n')

def ls_alien(path_dir, pattern=''):
  """List files under Alien directory
  """
  cmd = ['alien_ls', path_alien(path_dir)]
  proc = subprocess.run(cmd, stdout=subprocess.PIPE)
  ret = proc.stdout.decode('utf-8')
  job_list = [job_dir for job_dir in ret.split('\n') if job_dir.find(pattern) > -1]
  return job_list

def download_alien(source : str, target : str, args='-f', debug=False, **subproc_args):
  """Copy file to local from alien
  """
  if not source.startswith('alien://'):
    source = f'alien://{source}'
  if not target.startswith('file:'):
    target = f'file:{target}'
  # mkdir?
  cmd = ['alien_cp', args, source, target]
  print_cmd(cmd)
  if debug:
    cmd = ['echo'] + cmd
  subprocess.run(cmd, **subproc_args)
  # exception

def process_download_single(dl_args : dict):
  """ for MP pool
  """
  job_id = dl_args.get('job_id', 0)
  job_n = dl_args.get('job_n', 0)
  print(f'{job_id}/{job_n} - ',end='')
  flag_debug = dl_args.get('debug', False)
  # Pipe
  if dl_args.get('stdout') is None:
    logfile = subprocess.STDOUT
  else:
    logfile = open(dl_args.get('stdout'), 'a')
  if dl_args.get('stderr') is None:
    errfile = subprocess.STDOUT
  else:
    errfile = open(dl_args.get('stderr'), 'a')
  download_alien(dl_args["source"], dl_args["target"], dl_args["args"], debug=flag_debug, stdout=logfile, stderr=errfile)
  #cmd = ['echo', f'{job_id} alien_cp {dl_args["args"]} alien://{dl_args["source"]} file:{dl_args["target"]}']
  #proc = subprocess.run(cmd, stdout=logfile, stderr=errfile)

class GridDownloaderManager:
  """
  """
  def __init__(self, train_name, train_id, path_local, file_list, **gdm_args) -> None:
    self.train_name = train_name
    self.train_id = train_id
    self.train_no = train_id.split('_')[0]
    self.path_local = path_local
    self.file_list = file_list
    self.train_config = {}
    self.flag_debug = gdm_args.get('debug',False)
    self.flag_overwrite = gdm_args.get('overwrite',False)
    self.mp_jobs = gdm_args.get('mp_jobs', -1)
    self.child_list = gdm_args.get('child_list', None)
    if self.child_list is not None:
      self.child_list = [ f'child_{i}' for i in self.child_list]
  def read_env(self, path_envfile=None) -> dict:
    """
    """
    if not path_envfile:
      path_envfile = self.env_local
    with open(path_envfile,'r') as env_file:
      for var_string in env_file.readlines():
        keyval = var_string.replace('export','').strip().split('=')
        self.train_config[keyval[0]] = keyval[1].strip("'")
    # Parse configuration
    self.child_n = int(self.train_config['CHILD_DATASETS'])
    self.train_aliphys = self.train_config['ALIROOT_VERSION'].replace('VO_ALICE@AliPhysics::','') # 'ALIROOT_VERSION': 'VO_ALICE@AliPhysics::vAN-20220720_ROOT6-1'
    self.train_datasets = self.train_config['PERIOD_NAME']
    self.child_conf = {}
    for child_id in range(1,self.child_n+1):
      child_id = f'child_{child_id}'
      cfg = {}
      cfg['collision'] = self.train_config[f'ALIEN_JDL_{child_id}_LPMINTERACTIONTYPE']
      cfg['production'] = self.train_config[f'ALIEN_JDL_{child_id}_LPMPRODUCTIONTYPE']
      cfg['output_dir'] = self.train_config[f'ALIEN_JDL_{child_id}_OUTPUTDIR']
      alien_path_args = cfg['output_dir'].split('/')
      if cfg['production'] == 'MC':
        cfg['period'] = self.train_config[f'ALIEN_JDL_{child_id}_LPMPRODUCTIONTAG']
        cfg['prod_type'] = cfg['collision'] + '_sim'
      else:
        cfg['reco'] = self.train_config[f'ALIEN_JDL_{child_id}_LPMRAWPASS']
        cfg['period'] = self.train_config[f'ALIEN_JDL_{child_id}_LPMANCHORPRODUCTION']
        cfg['prod_type'] = cfg['collision'] + '_data'
      # MC -   /alice/sim/2020/LHC20f4a/285064/AOD235
      # Data - /alice/data/2018/LHC18k/000289177/pass1/AOD264'
      cfg['path_alien'] = '/'.join(alien_path_args[0:5])
      cfg['file_pattern'] = '/'.join(alien_path_args[6:]) + f'/{self.train_name}/{self.train_id}_{child_id}/AOD/*/'
      # Local dir
      cfg['path_local'] = f'{self.path_local}/{self.train_aliphys}/{cfg["prod_type"]}/{self.train_id}/unmerged/{child_id}'
      self.child_conf[child_id] = deepcopy(cfg)
    # Return
    return self.train_config
  def get_env(self) -> dict:
    """Train configuration
      AlienPath: /alice/cern.ch/user/a/alitrain/[PWGHF/HF_TreeCreator]/[train_id]<_child_N>/env.sh
    """
    self.env_file = f'TreeCreator_env_{self.train_no}.sh'
    self.env_local = f'{self.path_local}/{self.env_file}'
    if check_local_file(self.env_local, self.flag_overwrite):
      print(f'[-] Environment variables existed - {self.env_local}')
      return self.read_env()
    self.train_alien = f'/alice/cern.ch/user/a/alitrain/{self.train_name}'
    self.child_jobs = ls_alien(self.train_alien, self.train_id)
    if not self.child_jobs: # [] empty
      print(f'[X] Train ID - {self.train_id} - not found in {self.train_alien}')
      return None
    self.env_alien = f'{self.train_alien}/{self.child_jobs[0]}/env.sh'
    download_alien(self.env_alien, self.env_local)
    return self.read_env()
  def generate_path(self) ->  None:
    for child_id,cfg in self.child_conf.items():
      print(f'[+] Generating file list for {child_id} : ')
      #mkdir
      os.system('mkdir -p ' + cfg['path_local'])
      # existed filelist in file
      # generate if not
      child_filelist = cfg['path_local'] + '/alien_filelist_local.txt'
      self.child_conf[child_id]['filelist'] = child_filelist
      if check_local_file(child_filelist, self.flag_overwrite):
        print(f'>>> File list found - {child_filelist}')
        continue
      n_files = 0
      with open(child_filelist,'w') as fout:
        for file_name in self.file_list:
          ret = find_alien(cfg['path_alien'], cfg['file_pattern'] + file_name)
          n_files += len(ret)
          for fname in ret:
            if not fname: continue
            fname_args = fname.split('/')
            run = fname_args[5]
            subjob = fname_args[-2]
            local_file_path = cfg['path_local'] + f'/{run}/{subjob}'
            os.system('mkdir -p ' + local_file_path)
            fout.write(f'{fname} {local_file_path}/{file_name}\n')
      print(f' > N files found = {n_files} ({repr(self.file_list)})')
      print(f' > Example : {fname} {local_file_path}')
  def process_child(self, child_id) -> bool:
    """
    """
    cfg = self.child_conf[child_id]
    filelist = open(cfg['filelist'],'r').readlines()
    print(f'[-] Processing {child_id} - {len(filelist)} files')
    print(f'>>> Local path - {cfg["path_local"]}')
    # Arguments for each job
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    logfile = f'{cfg["path_local"]}/download_train_stdout_{child_id}_{timestamp}.log'
    errfile = f'{cfg["path_local"]}/download_train_stderr_{child_id}_{timestamp}.log'
    job_arguments = []
    for file_id, file_single in enumerate(filelist):
      file_alien = file_single.split()[0]
      file_local = file_single.split()[1]
      job_arguments.append({'source':file_alien, 'target':file_local,'args':'-f -retry 3', 'job_id':file_id, 'job_n':len(filelist), 'stdout': logfile, 'stderr':errfile, 'debug':self.flag_debug})
    # Multiprocessing
    print(f'>>> Downloading...\n>>> Log : {logfile}\n>>> Err : {errfile}')
    if self.mp_jobs < 1:
      self.mp_jobs = os.cpu_count()
    with mp.Pool(processes=self.mp_jobs) as mpPool:
      mpPool.map(process_download_single, job_arguments)
  def start(self):
    self.get_env()
    self.generate_path()
    # Select children
    if self.child_list is None:
      self.child_list = self.child_conf.keys() # all
    for child_id in self.child_list:
      self.process_child(child_id)

if __name__ == '__main__':
  parser = argparse.ArgumentParser('AliEn grid downloader for LEGO train')
  parser.add_argument('id',type=str, help='ID of LEGO train, <ID>_DATE-TIME e.g. 706_20220720-1829')
  parser.add_argument('-p','--local',dest='path_local', default='/data/Tree')
  parser.add_argument('--train', default='PWGHF/HF_TreeCreator',type=str, help='Train name in alitrain')
  parser.add_argument('--files', default='AnalysisResults.root')
  parser.add_argument('-i', '--overwrite', default=False, help='Ask prompt if overwrite', action='store_true')
  parser.add_argument('-v', '--verbose', default=False, help='Print more outputs', action='store_true')
  parser.add_argument('-j', '--jobs', default=-1, type=int, help='N jobs for multiprocessing')
  parser.add_argument('-c', '--children', nargs='+', help='Specify children list to download')
  # Save dir.: <path_local>[/<AliPhysics_tag>/<data_or_mc_production>/<train_name>/unmerged/child_<ID>]
  # Job dir.: [RunNumber]/[JobID]
  args, unknown =  parser.parse_known_args()
  if unknown:
    print(f'[+] Unknown arguments : {unknown}')
  adm = GridDownloaderManager(args.train, args.id, args.path_local, args.files.split(','), overwrite=args.overwrite, debug=args.verbose, mp_jobs=args.jobs, child_list=args.children) # Alien Download Manager
  # Debug
  #print(args)
  adm.start()
