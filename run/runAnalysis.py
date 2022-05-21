#!/usr/bin/env python3

# AliPhysics run local analysis

import os, argparse
import ROOT
from ROOT import kTRUE, kFALSE
from ROOT import AliHFTreeHandler

# Configurations
parser = argparse.ArgumentParser(description='AliPhysics local debug')
parser.add_argument('--run', default='286350', help='Path with runnumber')
parser.add_argument('--all', help='Loop all subjobs under run path', default=False, action='store_true')
parser.add_argument('--debug', help='Print info. without starting analysis', default=False, action='store_true')
parser.add_argument('--sub', default='0001', help='Dir. name of sub-job, add comma to separate multiple jobs')
args = parser.parse_args()

ALICE_PHYSICS = os.environ['ALICE_PHYSICS']

# ALICE includes
ROOT.gInterpreter.ProcessLine(".include $ROOTSYS/include")
ROOT.gInterpreter.ProcessLine(".include $ALICE_ROOT/include")

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
taskMacro = 'PWGHF/treeHF/macros/AddTaskHFTreeCreator.C'
__R_ADDTASK__ = ROOT.gInterpreter.ExecuteMacro("$ALICE_PHYSICS/PWGHF/treeHF/macros/AddTaskHFTreeCreator.C(1, 0, \"HFTreeCreator_pp_kAny\", \"D0DsDplusDstarLcBplusBsLbCuts_pp_kAny.root\", 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 9, 1, 0, 0, 0, 0)")
__R_ADDTASK__ = mgr.GetTask("TreeCreatorTask")
__R_ADDTASK__.SelectCollisionCandidates(ROOT.AliVEvent.kINT7)
__R_ADDTASK__.SetFillJets(kTRUE)
__R_ADDTASK__.SetDoJetSubstructure(kTRUE)
__R_ADDTASK__.SetJetSubRadius(0.)
__R_ADDTASK__.SetSoftDropZCut(0.1)
__R_ADDTASK__.SetSoftDropBeta(0.)

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

if(args.debug):
  print('[-] DEBUG - STOP before mgr.InitAnalysis & StartAnalysis')
else:
  if(not mgr.InitAnalysis()):
    print('[X] ERROR - Fail to InitAnalysis')
    exit()
  mgr.PrintStatus()
  mgr.SetUseProgressBar(1, 25)
  mgr.StartAnalysis("local",aodChain)
  
# ISSUE: segmentation violation => ~AliAnalysisTaskSEHFTreeCreator