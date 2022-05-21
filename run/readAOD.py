#!/usr/bin/env python3

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

pdgCand = [431, 4122] # Ds, Lc
idxCand = []

def MCParticleName(mcpart):
  if(mcpart is None):
    return '[IP]'
  try:
    return ROOT.TDatabasePDG.Instance().GetParticle(mcpart.GetPdgCode()).GetName()
  except ReferenceError:
    return str(mcpart.GetPdgCode())

def FindMCdaughters(array, mcpart, daughter_vec):
  for i in range(mcpart.GetNDaughters()):
    daughterLabel = mcpart.GetDaughterLabel(i)
    if(daughterLabel == -1): continue
    daughter = array.At(daughterLabel)
    if(daughter is None): continue
    daughter_vec.append(daughterLabel)
    if(not daughter.IsPhysicalPrimary()):
      FindMCdaughters(array, daughter, daughter_vec)

for i, ev in enumerate(aodChain):
  candFound = False
  for j, mcPar in enumerate(mcarray):
    if(abs(mcPar.GetPdgCode()) not in pdgCand): continue
    mother = None if mcPar.GetMother() == -1 else mcarray[mcPar.GetMother()]
    daughter_vec = []
    FindMCdaughters(mcarray, mcPar, daughter_vec)
    print(f'{i:06d}\t{MCParticleName(mother)} -> {MCParticleName(mcPar)} -> ', end='')
    print(', '.join([MCParticleName(mcarray[id]) for id in daughter_vec]))
  if(candFound): break
