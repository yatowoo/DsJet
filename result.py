#!/usr/bin/env python3

# Present FF results and model comparison

import argparse

parser = argparse.ArgumentParser(description='FF results')
parser.add_argument('-f','--file', default='/mnt/d/DsJet/ana-testFixMC/pp_data/unfolding_results.root', help='Unfolding results')
parser.add_argument('-m','--model', default='charm_fastsimu_Ds.root', help='Model outputs')
parser.add_argument('-i','--iter',type=int, default=4, help='N iterations for unfolding')
args = parser.parse_args()

# result: unfolded_z_[Niter]_pt_jet_15.00_35.00
# model: hz_ptjet_7_15

import ROOT
from ROOT import TFile, TH1D, TCanvas, TLegend, TPaveText
from ROOT import kRed, kBlack, kBlue, kWhite
from array import array

ROOT.gStyle.SetOptTitle(False)
ROOT.gStyle.SetOptStat(False)
ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gStyle.SetLegendFillColor(kWhite)
ROOT.gStyle.SetLegendFont(42)
ROOT.gStyle.SetLineWidth(2)
ROOT.gStyle.SetPadTopMargin(0.02)
ROOT.gStyle.SetPadBottomMargin(0.12)
ROOT.gStyle.SetPadLeftMargin(0.14)
ROOT.gStyle.SetPadRightMargin(0.02)

Z_BINNING = [0.4,0.6,0.7,0.8,0.9,1.0]

fResult = TFile.Open(args.file)
fModel = TFile.Open(args.model)
c = TCanvas('c1','draw',2400,600)
c.Divide(3,1)

def add_text(pave : TPaveText, s : str, color=None, size=0.04, align=11):
  text = pave.AddText(s)
  text.SetTextAlign(align)
  text.SetTextSize(size)
  text.SetTextFont(42)
  if(color):
    text.SetTextColor(color)
  return text

root_objs = []
PT_JET_BINNING = [5, 7, 15, 35]
for iptjet in range(3):
  pt_jet_l = PT_JET_BINNING[iptjet]
  pt_jet_u = PT_JET_BINNING[iptjet+1]
  hResult = fResult.Get(f'unfolded_z_{args.iter}_pt_jet_{pt_jet_l:.2f}_{pt_jet_u:.2f}')
  hModelRaw = fModel.Get(f'hz_ptjet_{pt_jet_l:.0f}_{pt_jet_u:.0f}')

  hModel = hModelRaw.Rebin(len(Z_BINNING)-1,f'hz_model_ptjet_{pt_jet_l:.0f}_{pt_jet_u:.0f}', array('d', Z_BINNING))
  isolatedCandJet = hModelRaw.GetBinContent(hModelRaw.FindBin(1.001)) + hModel.GetBinContent(hModel.FindBin(0.99))
  hModel.SetBinContent(hModel.FindBin(0.99), isolatedCandJet)
  hModel.Scale(1./hModel.Integral(),'width')

  hResult.SetMarkerStyle(20)
  hResult.SetMarkerSize(1.5)
  hResult.SetLineColor(kBlack)
  hResult.SetMarkerColor(kBlack)
  hResult.SetXTitle('z_{#parallel}^{ch}')
  hResult.GetYaxis().SetRangeUser(0, 2* hResult.GetMaximum())
  hResult.SetYTitle("1/#it{N}_{jets} d#it{N}/d#it{z_{#parallel}^{ch}} (self normalised)")
  hModel.SetLineColor(kRed+1)
  hModel.SetMarkerColor(kRed+1)
  #hModel.SetFillColor(kRed-10)
  hModel.SetDrawOption('E0')
  # Legend
  root_objs.append(TLegend(0.15,0.7,0.45,0.85))
  lgd = root_objs[-1]
  lgd.AddEntry(hResult,'data (unfolded)')
  lgd.AddEntry(hModel,'POWHEG + PYTHIA6')
  # Description
  root_objs.append(TPaveText(0.6,0.7,0.88,0.92,"NDC"))
  pave = root_objs[-1]
  pave.SetFillColor(kWhite)
  add_text(pave, f'3 < #it{{p}}_{{T,D_{{s}}}} < {pt_jet_u} GeV/#it{{c}}')
  add_text(pave, f'{pt_jet_l} < #it{{p}}_{{T,jet}} < {pt_jet_u} GeV/#it{{c}}')
  add_text(pave, "|#it{#eta}_{jet}| < 0.5")
  c.cd(iptjet+1)
  hResult.Draw('E0')
  hModel.Draw('same')
  lgd.Draw('same')
  pave.Draw("same")

cmd = input('<exit>')
