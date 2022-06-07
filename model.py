#!/usr/bin/env python3

# Ds/D0 comparison

import ROOT
from ROOT import TFile, TH1D, TCanvas, TLegend, TPaveText
from ROOT import kRed, kBlack, kBlue, kWhite
from array import array
import root_plot

fDs = TFile.Open('beauty_fastsimu_Ds.root')
fD0 = TFile.Open('beauty_fastsimu_D0.root')

root_plot.ALICEStyle()

PT_JET_BINNING = [5, 7, 15, 35]
N_JETBINS = 3

c = TCanvas('c1','draw',1200,1200)

root_objs = []
def newObj(obj):
  global root_objs
  root_objs.append(obj)
  return root_objs[-1]

pMain, pRatio = newObj(root_plot.NewRatioPads(c, f'padz', f'padratio', gap=0.0))
lgd = newObj( TLegend(0.15,0.5,0.45,0.85) )

for iptjet in range(N_JETBINS):
  pt_jet_l = PT_JET_BINNING[iptjet]
  pt_jet_u = PT_JET_BINNING[iptjet+1]
  root_objs.append(fDs.Get(f'hz_ptjet_{pt_jet_l:.0f}_{pt_jet_u:.0f}').Clone(f'hzDs_ptjet_{pt_jet_l:.0f}_{pt_jet_u:.0f}'))
  hDs = root_objs[-1]
  root_objs.append(fD0.Get(f'hz_ptjet_{pt_jet_l:.0f}_{pt_jet_u:.0f}').Clone(f'hzD0_ptjet_{pt_jet_l:.0f}_{pt_jet_u:.0f}'))
  hD0 = root_objs[-1]
  hD0.SetLineStyle(3)
  pMain.cd()
  if(iptjet == 0):
    hDs.Draw("E0")
    hDs.GetXaxis().SetLabelSize(0.0)
    hDs.GetYaxis().SetRangeUser(0.01, 6.0)
  else:
    hDs.Draw("E0 same")
  hD0.Draw("E0 same")
  lgd.AddEntry(hDs, f'D_{{s}} - {pt_jet_l} < #it{{p}}_{{T,jet}} < {pt_jet_u} GeV/#it{{c}}')
  lgd.AddEntry(hD0, f'D^{{0}} - {pt_jet_l} < #it{{p}}_{{T,jet}} < {pt_jet_u} GeV/#it{{c}}')  
  ratio = newObj(hDs.Clone(f'ratioDsD0_ptjet_{pt_jet_l:.0f}_{pt_jet_u:.0f}'))
  ratio.Divide(hD0)
  ratio.SetYTitle('D_{s}/D^{0}')
  # Ratio pad
  pRatio.cd()
  root_plot.SetRatioPlot(ratio, 0.3, 1.8)
  if(iptjet == 0):
    ratio.Draw('E0')
  else:
    ratio.Draw('E0 same')

pMain.cd()
lgd.Draw("same")

pave = newObj(TPaveText(0.6,0.72,0.85,0.85,"NDC"))
pave.SetFillColor(kWhite)
root_plot.add_text(pave, f'#it{{p}}_{{T,D}} > 3 GeV/#it{{c}}')
root_plot.add_text(pave, "|#it{#eta}_{jet}| < 0.5")
pave.Draw("same")

cmd = input('<exit>')