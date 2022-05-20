#!/bin/env python3

# AliPhysics run local analysis

import os, sys
import ROOT
from ROOT import kTRUE, kFALSE
from ROOT import AliHFTreeHandler

# Configurations
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
runpath='286350'
for subdir in os.listdir(runpath):
  filepath=runpath + '/' + subdir
  aodChain.Add(filepath + "/AliAOD.root")
  vtxChain.Add(filepath + "/AliAOD.VertexingHF.root")
aodChain.AddFriend(vtxChain)

mgr.InitAnalysis()
mgr.StartAnalysis("local",aodChain)
