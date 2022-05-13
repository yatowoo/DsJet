#!/bin/env python3

# Processing resphisto.root

from ROOT import gStyle, gPad
from ROOT import TFile, TH1D, TCanvas, TLegend, TPaveText
from ROOT import kRed, kBlack, kBlue, kWhite

gStyle.SetOptStat(False)
gStyle.SetOptTitle(False)
gStyle.SetLegendBorderSize(0)
gStyle.SetLegendFillColor(kWhite)
gStyle.SetLegendFont(42)

colorset = [kBlack, kRed, kBlue]
markerstyle = [24, 25, 26]

file_input = '/mnt/d/DsJet/ana-reldiff/reldiff-resphisto.root'
file_out = 'response_draw.root'
fInput = TFile.Open(file_input)
fOutput = TFile.Open(file_out,'RECREATE')
HFcand = 'Ds'

vars = ['jetpt', 'ptcand', 'jeteta', 'jetphi']
labels = ['#it{p}_{T,jet}', '#it{p}_{T,cand}', '#it{#eta}_{jet}', '#it{#phi}_{jet}']

candtype = ['prompt', 'nonprompt']

suffix = ['5.00_7.00', '7.00_15.00', '15.00_35.00']

c = TCanvas('c1','Gen_reco rel. diff.', 3200, 1600)
c.Divide(4,2)
c.SetLogy(True)
padIndex = 0
root_obj = []
for candt in candtype:
  for j, varName in enumerate(vars):
    padIndex += 1
    c.cd(padIndex)
    gPad.SetLogy(True)
    gPad.SetMargin(0.15, 0.02, 0.15, 0.1)
    root_obj.append(TLegend(0.18,0.6,0.4,0.88))
    lgd = root_obj[-1]
    for i, suf in enumerate(suffix):
      histname = f'h{varName}_fracdiff_{candt}pt_jet_' + suf
      print(histname)
      htmp = fInput.Get(histname)
      htmp.SetLineColor(colorset[i])
      htmp.SetMarkerColor(colorset[i])
      htmp.SetMarkerStyle(markerstyle[i])
      htmp.GetXaxis().SetTitleSize(0.07)
      htmp.SetXTitle("#Delta_{rel}" + labels[j])
      htmp.SetYTitle("Entries (self normalised)")
      lgd.AddEntry(htmp, suf)
      if(i == 0):
        htmp.Draw()
      else:
        htmp.Draw("same")
    lgd.Draw("same")

c.SaveAs("reldiff.pdf")

fInput.Close()
fOutput.Close()
