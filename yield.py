#!/bin/env python3

from ROOT import TH1, TCanvas, TFile, TPad, gStyle, gPad
from ROOT import kBlack, kRed, kBlue

def readhist(fname,hname,hname_new,color,output, scale=1.0):
  f = TFile(fname)
  htmp = f.Get(hname)
  hout = htmp.Clone(hname_new)
  hout.SetDirectory(output)
  f.Close()
  hout.SetLineColor(color)
  hout.SetMarkerColor(color)
  hout.Scale(scale)
  return hout

sigmav0 = 57.8e-3
br = 2.24e-2 # Ds -> (phi->KK)pi
fout = TFile("yield/sum.root","RECREATE")
hincl = readhist("yield/finalcrossDsJetppMBvspt_ntrklmulttot.root",
  "histoSigmaCorr0", "hIncl", kBlack, fout,
  1/(sigmav0 * 1e12 * br))

hspd = readhist("yield/DsCorrectedYieldPerEvent_SPD_1999_19_1029_3059_6099.root",
  "histoSigmaCorr_0", "hSPD", kRed, fout)

hv0m = readhist("yield/DsCorrectedYieldPerEvent_V0M_0100_50100_30100_0130_001.root",
  "histoSigmaCorr_0", "hV0M", kBlue, fout)

gStyle.SetOptTitle(0)
c = TCanvas("cDraw","Ds corrected yield", 800, 1000)
c.SetMargin(0.1,0.02,0.1,0.02)
c.cd()
# split - 0.3/0.7
pYield = TPad("pYield","",0,0.3,1,1)
pYield.SetMargin(0.15, 0.02, 0, 0.02)
pYield.Draw()
pRatio = TPad("pRatio","",0,0,1,0.3)
pRatio.SetMargin(0.15, 0.02, 0.3, 0)
pRatio.Draw()
pYield.cd()
hincl.SetTitle("Incl.")
hincl.SetXTitle("")
hincl.SetYTitle("1/#it{N}_{evt} d^{2}#it{N}/(d#it{y}d#it{p}_{T}) (GeV^{-1}/#it{c})")
hincl.Draw()
hspd.SetTitle("SPD #it{N}_{trkl} #in [0, 9999]")
hspd.Draw("same")
hv0m.SetTitle("V0M 0-100")
hv0m.Draw("same")
pYield.SetLogy()
pYield.BuildLegend(0.6,0.7,0.95,0.86)
pYield.Update()

# Ratio plot, lower pad
rpSPD = hincl.Clone("rpSPD")
rpSPD.Divide(hspd)
rpSPD.SetLineColor(kRed)
rpSPD.SetMarkerColor(kRed)
rpV0M = hincl.Clone("rpV0M")
rpV0M.Divide(hv0m)
rpV0M.SetLineColor(kBlue)
rpV0M.SetMarkerColor(kBlue)
pRatio.cd()
rpSPD.SetXTitle("#it{p}_{T} (GeV/#it{c})")
rpSPD.GetXaxis().SetTitleSize(0.12)
rpSPD.GetXaxis().SetTitleOffset(0.9)
rpSPD.GetXaxis().SetLabelSize(0.1)
rpSPD.GetYaxis().SetTitleSize(0.12)
rpSPD.GetYaxis().SetTitleOffset(0.5)
rpSPD.GetYaxis().SetLabelSize(0.08)
rpSPD.SetYTitle("Ratio")
rpSPD.Draw()
rpV0M.Draw('same')

fout.cd()
c.Write()
c.SaveAs('yield/sum.pdf')
fout.Close()