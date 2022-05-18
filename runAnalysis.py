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

# Task
taskMacro = 'PWGHF/treeHF/macros/AddTaskHFTreeCreator.C'
ROOT.gInterpreter.ProcessLine(f".L {os.environ['ALICE_PHYSICS']}/{taskMacro}")

# Analysis handler
mgr = ROOT.AliAnalysisManager("AnalysisMyTask")
aodH = ROOT.AliAODInputHandler()

task = ROOT.AddTaskHFTreeCreator(kTRUE, 0, "HFTreeCreator_pp_kAny", "D0DsDplusDstarLcBplusBsLbCuts_pp_kAny.root", 0, kTRUE, kTRUE, 1, 1, 0, 0, 0, 1, 0, 0, 0, AliHFTreeHandler.kNsigmaDetAndCombPID, AliHFTreeHandler.kRedSingleTrackVars, kFALSE, kFALSE, 0, kFALSE)

vtxChain = ROOT.TChain("aodTree")
vtxChain.Add("AliAOD.VertexingHF.root")
aodChain = ROOT.TChain("aodTree")
aodChain.Add("AliAOD.root")
aodChain.AddFriend(vtxChain)

mgr.InitAnalysis()
mgr.StartAnalysis("local",aodChain)
