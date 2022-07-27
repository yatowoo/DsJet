#!/usr/bin/env python3

# Download output from LEGO train
# Refer: https://github.com/ginnocen/MachineLearningHEP/tree/master/cplusutilities
# Env: AliPhysics or any modules with JAliEn commands alien_cp/ls
# Preparation: alien-token-init [user]
# Parameters and basic usage: (see help)
#
# Example: ./download_trian.py 705_20220720-1829 -p /mnt/temp/TTree/D0DsLckINT7HighMultCalo_withJets -j 20
#
# AliEn path:
# - MC: /alice/sim/2020/LHC20f4c/264347/AOD235/PWGHF/HF_TreeCreator/706_20220720-1829_child_1/AOD/001/AnalysisResults.root
# - Data: /alice/data/2018/LHC18e/000286937/pass1/AOD264/PWGHF/HF_TreeCreator/705_20220720-1829_child_2/AOD/001/AnalysisResults.root
# Local path:
# - MC: D0DsLckINT7HighMultCalo_withJets/vAN-20220720_ROOT6-1/pp_sim/705_20220720-1829/unmerged/child_12/000293368/001/AnalysisResults.root
# - Data: D0DsLckINT7HighMultCalo_withJets/vAN-20220720_ROOT6-1/pp_data/705_20220720-1829/unmerged/child_12/000293368/001/AnalysisResults.root
# Search pattern: PWGHF/HF_TreeCreator/705_20220720-1829_child_2/AOD

import os, sys
import datetime
import time
import subprocess
import multiprocessing as mp
import argparse
from pprint import pprint
from copy import deepcopy
import defusedxml.ElementTree as xml

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

def repr_ratio(n_numerator : int, n_denominator : int):
  ratio = 1.0 * n_numerator / n_denominator
  return f'{n_numerator}/{n_denominator} ({ratio*100.:.1f}%)'

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

def find_alien(path_dir, pattern='', args=[], **subproc_args):
  """
  """
  cmd = ['alien_find', path_alien(path_dir), pattern] + args
  print_cmd(cmd)
  proc = subprocess.run(cmd, stdout=subprocess.PIPE, **subproc_args)
  return proc.stdout.decode('utf-8')

def find_local(path_dir, pattern_name='*.root',typefile='f',**find_args):
  """Find files with name pattern
  """
  cmd = ['find',path_dir, '-name',pattern_name]
  print_cmd(cmd)
  proc = subprocess.run(cmd, stdout=subprocess.PIPE)
  return proc.stdout.decode('utf-8')

def ls_alien(path_dir, pattern=''):
  """List files under Alien directory
  """
  cmd = ['alien_ls', path_alien(path_dir)]
  proc = subprocess.run(cmd, stdout=subprocess.PIPE)
  ret = proc.stdout.decode('utf-8')
  job_list = [job_dir for job_dir in ret.split() if job_dir.find(pattern) > -1]
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
  # Pipe
  ret = ' '.join(cmd) + '\n'
  stdout = subproc_args.get('stdout', None)
  stderr = subproc_args.get('stderr', None)
  if not stdout:
    print_cmd(cmd)
  elif stdout != subprocess.PIPE:
    stdout.write(ret)
  if debug:
    cmd = ['echo'] + cmd
  proc = subprocess.run(cmd, **subproc_args)
  if stdout == subprocess.PIPE:
    ret = ret + proc.stdout.decode('utf-8')
  if stderr == subprocess.PIPE:
    ret = ret + proc.stderr.decode('utf-8')
  return ret
  # exception

def process_download_single(dl_args : dict):
  """ for MP pool
  """
  job_id = dl_args.get('job_id', 0)
  job_n = dl_args.get('job_n', 0)
  job_label = '/'.join([dl_args["source"].split('/')[i] for i in [4, 5, -2]])
  flag_debug = dl_args.get('debug', False)
  # Pipe
  log_mq = dl_args.get('log_mq', None)
  logfile = dl_args.get('stdout', None)
  msg = f'{job_id}/{job_n} - {job_label}'
  if log_mq:
    log_mq.put(msg)
  elif logfile is None:
    logfile = sys.stdout
    logfile.write(msg + '\n')
  else:
    logfile = open(logfile, 'a')
    logfile.write(msg + '\n')
  ret = download_alien(dl_args["source"], dl_args["target"], dl_args["args"], debug=flag_debug, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  status_ok = None
  if not check_local_file(dl_args["target"]) and not flag_debug:
    ret = ret + f'[X] Fail to download {job_label} - {dl_args["target"]}\n'
    status_ok = False
  else:
    ret = ret + f'[-] OK - {job_label}\n'
    status_ok = True
  if log_mq:
    log_mq.put(ret)
  else:
    logfile.write(ret)
  return status_ok

def listener_mp_log(q, logfile, n_job = 100, n_step=1, n_seconds=10):
  """Receive messages from mp.Pool, write to log file
  """
  n_done, n_ok, n_fail = 0, 0, 0
  flag_progress = False
  print(f'>>> Listener MQ - started\n>>> to report per {n_step} jobs or {n_seconds} seconds')
  time_start = int(time.time())
  time_report = time_start
  with open(logfile, 'w') as f:
    while True:
      m = q.get()
      if m.lower() == 'kill':
        f.write('[-] Listener killed - MP job\n')
        break
      elif m.lower().find('[-] ok') > -1:
        n_ok += 1
        n_done += 1
        flag_progress = True
      elif m.lower().find('fail') > -1:
        n_fail += 1
        n_done += 1
        flag_progress = True
      f.write(str(m) + '\n')
      f.flush()
      # Progress report
      flag_progress &= (n_done % n_step == 0)
      dt = int(time.time()) - time_start
      if flag_progress or (dt - time_report > n_seconds):
        time_report = dt
        print(f'>>> Progress : {n_done}/{n_job} - OK = {repr_ratio(n_ok,n_job)}, FAIL = {n_fail} - Time elapsed : {dt}s')
        flag_progress = False
  print(f'[-] Listener MQ - {n_done}/{n_ok}/{n_fail} (Done/OK/FAIL)')

class GridDownloaderManager:
  """Download outputs files from AliEn grid (by LEGO train)
  
  Parameters:
  - train_id (required, e.g. 708_20220723-0034)
  - train_name (str, Default: PWGHF/HF_TreeCreator)
  - path_local (str, Default: . )
  - file_list (list, Default: ['AnalysisResults.root'])
  
  Options: (**gdm_args)
  - child_list: [int], selected child id (Default: <all>)
  - debug: print verbose info (echo alien_cp command)
  - overwrite: bool, generate new env.sh and filelist (Default: false)
  - mp_jobs: int, number of multiple processes (Default: n_cpu)
  - mp_report_step: int, monitor report progress per N jobs (Default: 20) 
  - mp_report_dt: int, monitor report progress per N seconds (Default: 30)
  """
  def __init__(self, train_name, train_id, path_local, file_list, **gdm_args) -> None:
    self.train_name = train_name # PWGHF/HF_TreeCreator
    self.train_pwg, self.train_subname = self.train_name.split('/')
    self.train_id = train_id
    self.train_no = train_id.split('_')[0]
    self.path_local = path_local
    self.file_list = file_list
    self.train_config = {}
    self.flag_debug = gdm_args.get('debug',False)
    self.flag_overwrite = gdm_args.get('overwrite',False)
    self.mp_jobs = gdm_args.get('mp_jobs', -1)
    self.mp_report_step = gdm_args.get('mp_report_step', 20)
    self.mp_report_dt = gdm_args.get('mp_report_dt', 30) # per second
    self.child_list = gdm_args.get('child_list', None)
    if self.child_list is not None:
      self.child_list = [ f'child_{i}' for i in self.child_list]
    self.enable_xml = gdm_args.get('enable_xml', False)
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
  def generate_path_xml(self):
    """
    """
    for child_id,cfg in self.child_conf.items():
      print(f'[+] Generating file list for {child_id} : ')
      # Filelist Path
      os.system('mkdir -p ' + cfg['path_local'])
      child_filelist_suffix = f'{self.train_subname}-{self.train_id}-{child_id}.xml'
      child_filelist_alien = f'TMP/{child_filelist_suffix}'
      os.system('alien_mkdir TMP/') # ? CWD
      child_filelist = f'{cfg["path_local"]}/{child_filelist_suffix}'
      self.child_conf[child_id]['filelist'] = child_filelist
      if check_local_file(child_filelist, self.flag_overwrite):
        print(f'>>> File list found - {child_filelist}')
        continue
      # Generate
      xml_filelist = None
      file_size_total = 0
      n_files = 0
      for file_name in self.file_list:
        xml_node = xml.fromstring(find_alien(cfg['path_alien'],
          cfg['file_pattern'] + file_name,
          args=['-x', '-']))
        # alien-collection-[event-file]
        result = xml_node.find('collection').findall('event')
        n_files += len(result)
        for entry in result:
          entry = entry.find('file').attrib # entry[0]
          filename_alien = entry['lfn']
          file_size_total += int(entry['size']) # Bytes
          fname_args = filename_alien.split('/')
          entry['path_alien'] = filename_alien
          entry['run'] = fname_args[5]
          entry['subjob'] = fname_args[-2]
          entry['path_local'] = os.path.realpath(cfg['path_local'] + f'/{entry["run"]}/{entry["subjob"]}/{file_name}')
          os.system('mkdir -p ' + entry['path_local'])
        # Append
        if xml_filelist:
          xml_filelist.append(deepcopy(result))
        else:
          xml_filelist = deepcopy(xml_node)
      # Save
      print(f' > N files found = {n_files} ({repr(self.file_list)}) - Total size : {file_size_total/(1024**3):.3f} GB')
      print(f' > Example : {entry["path_alien"]} {entry["path_local"]}')
      with open(child_filelist, 'w') as f:
        f.write(xml.tostring(xml_filelist).decode('utf-8'))
  def generate_path_txt(self) ->  None:
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
          ret = find_alien(cfg['path_alien'], cfg['file_pattern'] + file_name).split()
          n_files += len(ret)
          for fname in ret:
            if not fname: continue
            fname_args = fname.split('/')
            run = fname_args[5]
            subjob = fname_args[-2]
            local_file_path = cfg['path_local'] + f'/{run}/{subjob}'
            os.system('mkdir -p ' + local_file_path)
            fout.write(f'{fname} {local_file_path}/{file_name}\n')
      self.child_conf[child_id]['filelist_n'] = n_files
      print(f' > N files found = {n_files} ({repr(self.file_list)})')
      print(f' > Example : {fname} {local_file_path}')
  def validate_child(self, child_id) -> int:
    """
    """
    cfg = self.child_conf[child_id]
    files_local = find_local(cfg['path_local'],pattern_name='*.root').split()
    nfiles_local = len(files_local)
    return nfiles_local
  def read_filelist(self, child_id):
    """
    """
    filelist_name = self.child_conf[child_id]['filelist']
    filelist = []
    f_filelist = open(filelist_name,'r')
    if not self.enable_xml:
      for entry in f_filelist.readlines():
        if not entry: continue
        filelist.append({})
        filelist[-1]['path_alien'], filelist[-1]['path_local'] = entry.split()
      f_filelist.close()
      return filelist
    # XML processing
    et = xml.parse(open(filelist_name,'r'))
    for coll in et.findall('collection'):
      for ev in coll.findall('event'):
        filelist.append(deepcopy(ev[0].attrib))
    return filelist
  def process_child(self, child_id) -> bool:
    """
    """
    cfg = self.child_conf[child_id]
    filelist =self.read_filelist(child_id)
    nfiles_alien = len(filelist)
    nfiles_local = self.validate_child(child_id)
    print(f'[-] Processing {child_id} - {nfiles_alien} files')
    print(f'>>> Local - {repr_ratio(nfiles_local, nfiles_alien)} files found - {cfg["path_local"]}')
    # Multiprocessing
    mgr = mp.Manager()
    log_mq = mgr.Queue()
    # Arguments for each job
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    logfile = f'{cfg["path_local"]}/download_train_stdout_{child_id}_{timestamp}.log'
    errfile = f'{cfg["path_local"]}/download_train_stderr_{child_id}_{timestamp}.log'
    job_arguments = []
    for file_id, file_single in enumerate(filelist):
      job_arguments.append({'source':file_single['path_alien'], 'target':file_single['path_local'],'args':'-f -retry 3', 'job_id':file_id, 'job_n':nfiles_alien, 'debug':self.flag_debug, 'log_mq':log_mq})
    # Start multithreading
    print(f'>>> Downloading...\n>>> Log : {logfile}\n>>> Err : {errfile}')
    if self.mp_jobs < 1:
      self.mp_jobs = os.cpu_count()
    with mp.Pool(processes=self.mp_jobs) as mpPool:
      listener = mpPool.apply_async(listener_mp_log, (log_mq, logfile, nfiles_alien, self.mp_report_step, self.mp_report_dt,))
      jobs = mpPool.map(process_download_single, job_arguments)
      log_mq.put('kill')
      listener.get() # clear MQ
    # Validation
      # TODO: integrity by size / cksum / md5
    files_local = find_local(cfg['path_local'],pattern_name='*.root').split()
    nfiles_local = len(files_local)
    files_fail = [] # grep / readlines by open
    with open(logfile,'r') as f_log:
      for l in f_log.readlines():
        if l.upper().find('FAIL') > -1:
          files_fail.append(l)
    nfiles_fail = len(files_fail)
    print(f'>>> Validation : OK - {repr_ratio(nfiles_local, nfiles_alien)}, FAIL - {nfiles_fail}, Done - {repr_ratio(nfiles_local+nfiles_fail, nfiles_alien)}')
    return True
  def start(self):
    self.get_env()
    if self.enable_xml:
      self.generate_path_xml()
    else:
      self.generate_path_txt()
    # Select children
    if self.child_list is None:
      self.child_list = self.child_conf.keys() # all
    for child_id in self.child_list:
      self.process_child(child_id)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='AliEn grid downloader for LEGO train', epilog='Train configuration: /alice/cern.ch/user/a/alitrain/<train_name>/<train_id>[_child_N]/env.sh --- Save path: <PATH_LOCAL>/<ALIPHYSICS_TAG>/pp_[data|sim]/<TRAIN_ID>/unmerged/child_<n>/<run_number>/<subjob>/AnalysisResults.root',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('train_id',type=str, help='ID of LEGO train, <ID>_DATE-TIME e.g. 706_20220720-1829')
  parser.add_argument('-p','--local',dest='path_local', default='.', help='Target path in local disk')
  parser.add_argument('--train', default='PWGHF/HF_TreeCreator',type=str, help='Train name in alitrain')
  parser.add_argument('--files', default='AnalysisResults.root', help='Specify output filename(s) to download, split by comma <,>')
  parser.add_argument('-i', '--overwrite', default=False, help='Ask prompt if overwrite', action='store_true')
  parser.add_argument('-v', '--verbose', default=False, help='Print more outputs', action='store_true')
  parser.add_argument('-j', '--jobs', default=1, type=int, help='N jobs for multiprocessing')
  parser.add_argument('-c', '--children', nargs='+', help='Specify children list to download, None is ALL.')
  parser.add_argument('--step', type=int, default=20, help='Specify progress report per N jobs')
  parser.add_argument('--dt', type=int, default=30, help='Specify progress report per N seconds')
  parser.add_argument('--xml', default=False, action='store_true', help='Generate filelist in XML format (required by intergrity check)')
  # Save dir.: <path_local>[/<AliPhysics_tag>/<data_or_mc_production>/<train_name>/unmerged/child_<ID>]
  # Job dir.: [RunNumber]/[JobID]
  args, unknown =  parser.parse_known_args()
  if unknown:
    print(f'[+] Unknown arguments : {unknown}')
  adm = GridDownloaderManager(args.train, args.train_id, args.path_local, args.files.split(','), overwrite=args.overwrite, debug=args.verbose, mp_jobs=args.jobs, child_list=args.children, mp_report_step=args.step, mp_report_dt=args.dt, enable_xml=args.xml) # Alien Download Manager
  # Debug
  #print(args)
  adm.start()
