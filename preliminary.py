#!/usr/bin/env python3

# Render ALICE preliminary figures

import argparse

parser = argparse.ArgumentParser(description='FF results')
parser.add_argument('-f','--file', default='/mnt/d/DsJet/systematics/merged_full0714/pp_data/unfolding_results.root', help='Unfolded data results')
parser.add_argument('-m','--model', default='/mnt/d/DsJet/fastsimu/', help='Model outputs')
parser.add_argument('--sys', default='/mnt/d/DsJet/systematics/merged_full0705/pp_data/systematics_results.root', help='Systematic uncertainties')
parser.add_argument('-i','--iter',type=int, default=4, help='N iterations for unfolding')
parser.add_argument('-o','--output',default='DsJet-results.root', help='Output file')
parser.add_argument('--extra',default=None, help='unfolding_results.root, Extra variation for comparison')
parser.add_argument('--dzero',default=False, action='store_true', help='Compare with D0 results from ALICE')

args = parser.parse_args()


import ROOT
from ROOT import TFile, TH1D, TCanvas, TLegend, TPaveText
from ROOT import kRed, kBlack, kBlue, kWhite, kGray
from array import array
import root_plot

FF_db = {
  'fd_fr':{
    'x':  [  0.5,  0.65,  0.75,  0.85,  0.95],
    'y':  [0.225, 0.150, 0.159, 0.124,0.0823],
    'exl':[  0.1,  0.05,  0.05,  0.05,  0.05],
    'exh':[  0.1,  0.05,  0.05,  0.05,  0.05],
    'eyl':[0.069, 0.045, 0.047, 0.036, 0.023],
    'eyh':[0.104, 0.069, 0.072, 0.056, 0.036],
    'stats':
          [0.0470, 0.0167, 0.0158, 0.0088, 0.00343],
  }
}

Z_BINNING = [0.4,0.6,0.7,0.8,0.9,1.0]
N_BINS = len(Z_BINNING)

def draw_cuts(range=None):
  ptxt = ROOT.TPaveText(0.15,0.68,0.60,0.90,"NDC")
  ptxt.SetTextAlign(13)
  ptxt.SetBorderSize(0)
  ptxt.SetTextSize(0.03)
  ptxt.SetFillColor(0)
  ptxt.SetTextFont(42)
  ptxt.AddText('D_{s}^{+}-tagged charged jets, anti-#it{k}_{T}, #it{R} = 0.4')
  ptxt.AddText('7 < #it{p}_{T}^{jet ch.} < 15 GeV/#it{c}, ' +'|#it{#eta}_{jet}| #leq 0.5')
  ptxt.AddText('3 < #it{p}_{T}^{D_{s}} < 15 GeV/#it{c}, ' +'|#it{y}_{D_{s}^{+}}| #leq 0.8')
  return ptxt

def draw_fd_fraction(path=None):
  c_fd_fr_sys = ROOT.TCanvas('c_fd_fr', 'canvas for preliminary', 1600,1200)
  tg_fd_fr_sys = ROOT.TGraphAsymmErrors(N_BINS,
    array('d', FF_db['fd_fr']['x']),
    array('d', FF_db['fd_fr']['y']),
    array('d', FF_db['fd_fr']['exl']),
    array('d', FF_db['fd_fr']['exh']),
    array('d', FF_db['fd_fr']['eyl']),
    array('d', FF_db['fd_fr']['eyh']))
  h_fd_fr_sys = ROOT.TGraphErrors(N_BINS,
    array('d', FF_db['fd_fr']['x']),
    array('d', FF_db['fd_fr']['y']),
    array('d', FF_db['fd_fr']['exl']),
    array('d', FF_db['fd_fr']['stats']))
  # Style
  c_fd_fr_sys.Draw()
  alice = root_plot.InitALICELabel(y1=-0.06, type='prel')
  color_i = 2 # Blue
  # sys.
  tg_fd_fr_sys.UseCurrentStyle()
  tg_fd_fr_sys.GetYaxis().SetTitle('Feed-down fraction')
  tg_fd_fr_sys.GetYaxis().SetRangeUser(0.02, 0.63)
  tg_fd_fr_sys.GetXaxis().SetTitle('#it{z}_{#parallel}^{ch}')
  tg_fd_fr_sys.GetXaxis().SetRangeUser(0.4, 1.0)
  tg_fd_fr_sys.SetMarkerStyle(root_plot.kRound)
  tg_fd_fr_sys.SetMarkerSize(0)
  tg_fd_fr_sys.SetMarkerColor(root_plot.COLOR_SET_ALICE[color_i])
  tg_fd_fr_sys.SetLineWidth(0)
  tg_fd_fr_sys.SetFillColor(root_plot.COLOR_SET_ALICE_FILL[color_i])
  tg_fd_fr_sys.SetFillStyle(3001)
  # val
  h_fd_fr_sys.SetMarkerStyle(root_plot.kRound)
  h_fd_fr_sys.SetLineColor(root_plot.COLOR_SET_ALICE[color_i])
  h_fd_fr_sys.SetLineWidth(2)
  h_fd_fr_sys.SetMarkerSize(2)
  h_fd_fr_sys.SetMarkerColor(root_plot.COLOR_SET_ALICE[color_i])
  #tg_fd_fr_sys.GetYaxis().SetTitleOffset(1.0)
  #tg_fd_fr_sys.GetYaxis().SetTitleSize(0.07)
  #tg_fd_fr_sys.GetYaxis().SetLabelSize(0.06)
  # Cuts
  pcuts = draw_cuts()
  # add legend
  ptxtR = ROOT.TPaveText(0.63,0.85,0.95,0.95,"NDC")
  ptxtR.SetTextSize(0.03)
  ptxtR.SetFillColor(0)
  ptxtR.SetBorderSize(0)
  ptxtR.AddText('pp #sqrt{#it{s}} = 13 TeV')
  ptxtR.AddText('POWHEG + PYTHIA 6 + EvtGen')
  # Legend
  lgd = ROOT.TLegend(0.63,0.63,0.95,0.80)
  lgd.SetTextSize(0.033)
  lgd.AddEntry(h_fd_fr_sys, 'POWHEG estimation')
  lgd.AddEntry(tg_fd_fr_sys, 'POWHEG uncertainty')
  # Render
  tg_fd_fr_sys.Draw('A2 P')
  alice.Draw('same')
  h_fd_fr_sys.Draw('P')
  lgd.Draw('same')
  pcuts.Draw('same')
  ptxtR.Draw('same')
  # Save
  tg_fd_fr_sys.Write()
  h_fd_fr_sys.Write()
  c_fd_fr_sys.Write()
  c_fd_fr_sys.SaveAs('c_fd_fr_sys.eps')
  c_fd_fr_sys.SaveAs('c_fd_fr_sys.pdf')
  c_fd_fr_sys.SaveAs('c_fd_fr_sys.root')
  # End - fd_fr
  input()

if __name__ == '__main__':
  root_plot.ALICEStyle()
  rootFile = ROOT.TFile.Open('preliminary.root','RECREATE')
  draw_fd_fraction()
  rootFile.Close()
