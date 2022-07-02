#!/usr/bin/env python3

import argparse

import multiprocessing as mp
import subprocess

GRID_DB = {
  'powheg_fd':{ # for sys. unc.
    'F1-R05': ('POWHEG_PYTHIA6_EVTGEN_BEAUTY_13TeV_F1-R05', 1656658784),
    'F05-R1': ('POWHEG_PYTHIA6_EVTGEN_BEAUTY_13TeV_F05-R1', 1656658790),
    'F2-R1': ('POWHEG_PYTHIA6_EVTGEN_BEAUTY_13TeV_F2-R1', 1656658795),
    'F1-R2': ('POWHEG_PYTHIA6_EVTGEN_BEAUTY_13TeV_F1-R2', 1656658800),
    'F2-R2': ('POWHEG_PYTHIA6_EVTGEN_BEAUTY_13TeV_F2-R2', 1656658805),
    'F05-R05': ('POWHEG_PYTHIA6_EVTGEN_BEAUTY_13TeV_F05-R05', 1656658811),
    'Mhi': ('POWHEG_PYTHIA6_EVTGEN_BEAUTY_13TeV_Mhi', 1656658816),
    'Mlo': ('POWHEG_PYTHIA6_EVTGEN_BEAUTY_13TeV_Mlo', 1656658821),
    'NoEvetGen': ('POWHEG_PYTHIA6_BEAUTY_13TeV_central', 1656675710),
  },
}

def convert():
  """
  """

def download():
  """
  """
def merge_process(args):
  """
  """
  config_name = args[0]
  config_file = args[1][0] + '.yaml'
  timestamp = args[1][1]
  with open(f'fastsimu/grid_merge_{config_name}.log','w+') as logfile:
    cmd = ['./submit_grid.py', config_file, '--merge', f'{timestamp}']
    print(f'[-] {config_name} - Processing merge job')
    print('>>> ' + ' '.join(cmd) + f'\n>>> log file : {logfile.name}')
    process = subprocess.run(cmd, stdout=logfile)
    print(f'[-] {config_name} - merge job submitted.')
def merge(batch_name):
  """
  """
  #pool = mp.Pool(processes=mp.cpu_count())
  #pool.map(merge_process, [[k,v] for k,v in GRID_DB[batch_name].items()])
  for k,v in GRID_DB[batch_name].items():
    merge_process([k, v])

def main(args):
  """
  """
  merge(args.batch)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Grid batch for fast simulation.')
  parser.add_argument('batch', metavar='NAME')
    
  args, unknown = parser.parse_known_args()
  if unknown:
    print('[+] Unknown arguments : ' + repr(unknown))

  main(args)
