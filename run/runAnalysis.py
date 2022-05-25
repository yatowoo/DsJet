#!/usr/bin/env python3

# AliPhysics run local analysis

import os, time, datetime
import argparse, yaml
import subprocess

# Configurations
parser = argparse.ArgumentParser(description='AliPhysics local debug')
parser.add_argument('--run', default='286350', help='Path with runnumber')
parser.add_argument('--all', help='Loop all subjobs under run path', default=False, action='store_true')
parser.add_argument('--debug', help='Print info. without starting analysis', default=False, action='store_true')
parser.add_argument('--sub', default='0001', help='Dir. name of sub-job, add comma to separate multiple jobs')
parser.add_argument('--lib', default=None, help='User defined libraries')
parser.add_argument('--grid', help='Submit jobs to grid, input mode', default=None)
parser.add_argument('-o', '--output', help='Work dir in grid', default='test')
parser.add_argument('--prod', help='Select production', type=int,default=2018)
parser.add_argument('--job', help='Select job under output dir.', type=str,default='000')

args = parser.parse_args()

import ROOT
from ROOT import kTRUE, kFALSE
ALICE_PHYSICS = os.environ['ALICE_PHYSICS']

# ALICE includes
ROOT.gInterpreter.ProcessLine(".include $ROOTSYS/include")
ROOT.gInterpreter.ProcessLine(".include $ALICE_ROOT/include")

def SubmitMerge(stage:int =1):
  workdir=args.output
  outputdir='OutputAOD'
  jobdir=args.job
  mergedir=f'alien://{workdir}/{outputdir}/{jobdir}/'
  subprocess.call(['alien_find', f'{mergedir}/*root_archive.zip', '-x', f'{mergedir}/Stage_{stage}.xml'])
  # Submit
  subprocess.call(['alien_submit',f'{mergedir}/../DsJet_pp_merge.jdl', '{stage}'])
  return kTRUE

def SetupGridHandler(mode : str = 'local', isMC : bool = True, task_name : str = 'DsJet_pp', work_dir='test', prod=2018):
  alienHandler = ROOT.AliAnalysisAlien()
  # Include Path
  alienHandler.AddIncludePath("-I. -I$ROOTSYS/include -I$ALICE_ROOT -I$ALICE_ROOT/include -I$ALICE_PHYSICS/include")
  # User files - copy to alien
    # ISSUE: Fail to copy .so libs
  alienHandler.SetAdditionalLibs("runAnalysis.py libPWGHFtreeHF_FixMC.so libPWGHFtreeHF_FixMC.rootmap AliHFJetFinder.h AliHFJetFinder.cxx D0DsDplusDstarLcBplusBsLbCuts_pp_kAny.root")
  # Source file to compile - gROOT->ProcessLine(".L [.cxx]+g");
  #alienHandler.SetAnalysisSource("AliHFJetFinder.cxx")
  # Data path
  config = yaml.load(open('DsJet_pp13TeV.yml'),Loader=yaml.FullLoader)
  runList = config['RunList']['MCpp13TeV_MB_Pythia8_AOD235']
  alienHandler.AddRunNumber(' '.join([str(run) for run in runList[prod]]))
    # MC production
  if(isMC):
    i = runList['child'].index(prod)
    mcProd = runList['production'][i]
    alienHandler.SetGridDataDir(f"/alice/sim/2020/{mcProd}/")
    alienHandler.SetDataPattern("AOD235/*/*AOD.root")
    alienHandler.SetFriendChainName("AliAOD.VertexingHF.root")
    alienHandler.SetRunPrefix("")
    alienHandler.SetNrunsPerMaster(1000)
    alienHandler.SetOutputToRunNo(kFALSE)
    # Data
  else:
    alienHandler.SetGridDataDir("/alice/data/2018/LHC18l")
    alienHandler.SetDataPattern("*/pass1/AOD*/AliAOD*.root")
    alienHandler.SetRunPrefix("000")
    alienHandler.SetNrunsPerMaster(200)
    alienHandler.SetOutputToRunNo(kTRUE)
  # Package
  tagDate = datetime.date.today() - datetime.timedelta(days=2)
  alienHandler.SetAliPhysicsVersion(f'vAN-{tagDate.strftime("%Y%m%d")}_ROOT6-1')
  alienHandler.SetAPIVersion("V1.1x")
  # Configuration
  alienHandler.SetSplitMaxInputFileNumber(20)

  alienHandler.SetTTL(43200) # 12 hours
  if(mode != 'test'):
    alienHandler.SetGridWorkingDir(f'{task_name}-{work_dir}')
  else:
    alienHandler.SetGridWorkingDir(f'{task_name}-{work_dir}-{time.strftime("%Y%m%d%H%M%S")}')
  alienHandler.SetGridOutputDir("OutputAOD")

  alienHandler.SetAnalysisMacro(task_name + ".C")
  alienHandler.SetExecutable(task_name + ".sh")
  alienHandler.SetJDLName(task_name + ".jdl")
  alienHandler.SetKeepLogs(kTRUE)
  alienHandler.SetDropToShell(kFALSE)
  
  alienHandler.SetMaxMergeFiles(50)
  alienHandler.SetMergeAOD(kTRUE)
  alienHandler.SetMaxMergeStages(2)
  alienHandler.SetMergeViaJDL( (mode != 'final') )
  if(mode == 'test'):
    alienHandler.SetNtestFiles(1)
    alienHandler.SetRunMode("test")
  elif(mode == 'full'):
    alienHandler.SetRunMode("full")
  elif(mode == 'merge' or mode == 'final'):
    alienHandler.SetRunMode("terminate")
  else:
    print(f'[X] Error - Unknown mode : {mode}')
    exit()
  return alienHandler

# Analysis handler
mgr = ROOT.AliAnalysisManager("AnalysisMyTask")
aodH = ROOT.AliAODInputHandler()
mgr.SetInputEventHandler(aodH)

# Wagons
  # Phys Selection
ROOT.gInterpreter.ExecuteMacro("$ALICE_PHYSICS/OADB/macros/AddTaskPhysicsSelection.C(1,1)")
  # PID pp TuneOnData
ROOT.gInterpreter.ExecuteMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskPIDResponse.C(1)")
  # Tree creator
if(args.lib is not None):
  for lib in args.lib.split(','):
    ROOT.gSystem.Load(lib)
taskMacro = 'PWGHF/treeHF/macros/AddTaskHFTreeCreator.C'
cutFile = "D0DsDplusDstarLcBplusBsLbCuts_pp_kAny.root"
__R_ADDTASK__ = ROOT.gInterpreter.ExecuteMacro(f"$ALICE_PHYSICS/PWGHF/treeHF/macros/AddTaskHFTreeCreator.C(1, 0, \"HFTreeCreator_pp_kAny\", \"{cutFile}\", 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 9, 1, 0, 0, 0, 0)")

__R_ADDTASK__ = mgr.GetTask("TreeCreatorTask")
__R_ADDTASK__.SelectCollisionCandidates(ROOT.AliVEvent.kINT7)
__R_ADDTASK__.SetFillJets(kTRUE)
__R_ADDTASK__.SetDoJetSubstructure(kTRUE)
__R_ADDTASK__.SetJetSubRadius(0.)
__R_ADDTASK__.SetSoftDropZCut(0.1)
__R_ADDTASK__.SetSoftDropBeta(0.)

if(not mgr.InitAnalysis()):
  print('[X] ERROR - Fail to InitAnalysis')
  exit()

# Running analysis
if(args.grid is not None):
  # Grid mode
  alienHandler = SetupGridHandler(mode=args.grid, work_dir=args.output, prod=args.prod)
  mgr.SetGridHandler(alienHandler)
  alienHandler.CreateJDL()
  jdl = alienHandler.GetGridJDL()
  jdl.AddToInputSandbox("LF:/alice/cern.ch/user/y/yitao/DsJet_pp/libPWGHFtreeHF_FixMC.so")
  alienHandler.WriteJDL(kTRUE)
  if(args.debug):
    print('[-] DEBUG - STOP before StartAnalysis')
  else:
    mgr.StartAnalysis("grid")
else:
  # Local mode
  aodChain = ROOT.TChain("aodTree")
  vtxChain = ROOT.TChain("aodTree")
  runpath = args.run
  subdirList = sorted(os.listdir(runpath)) if args.all else args.sub.split(',')

  print('[-] Path to run number : ' + runpath)
  print('>>> Sub-dir list : ' + ', '.join(subdirList))

  for subdir in subdirList:
    filepath=runpath + '/' + subdir
    aodChain.Add(filepath + "/AliAOD.root")
    vtxChain.Add(filepath + "/AliAOD.VertexingHF.root")
  aodChain.AddFriend(vtxChain)
  mgr.PrintStatus()
  mgr.SetUseProgressBar(1, 25)
  if(args.debug):
    print('[-] DEBUG - STOP before StartAnalysis')
  else:
    mgr.StartAnalysis("local",aodChain)
  
# ISSUE: segmentation violation => ~AliAnalysisTaskSEHFTreeCreator
