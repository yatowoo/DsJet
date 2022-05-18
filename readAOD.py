#!/bin/env python3

# AliPhysics read AOD event
import ROOT

vtxChain = ROOT.TChain("aodTree")
vtxChain.Add("AliAOD.VertexingHF.root")
aodChain = ROOT.TChain("aodTree")
aodChain.Add("AliAOD.root")
aodChain.AddFriend(vtxChain)

aod = ROOT.AliAODEvent()
aod.ReadFromTree(aodChain)

# 'mcparticles' - ROOT.AliAODMCParticle.StdBranchName()
mcBranch = ROOT.AliAODMCParticle.StdBranchName()
mcarray =  aod.GetList().FindObject(mcBranch)
mcHeader = ROOT.AliAODMCHeader.StdBranchName()
mcH = aod.GetList().FindObject(mcHeader)
candBranch = 'Charm3Prong'
candarray = aod.GetList().FindObject(candBranch)

pdgCand = 431 # Ds
for ev in aodChain:
  candFound = False
  for mcPar in mcarray:
    if(abs(mcPar.GetPdgCode()) != pdgCand): continue
    mcPar.Print()
    mcarray[mcPar.GetDaughterFirst()].Print()
    mcarray[mcPar.GetDaughterLast()].Print()
    candFound = True
    break
  if(candFound): break
