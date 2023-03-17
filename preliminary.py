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
  }
}

def draw_label(label='ALICE Preliminary'):
  pass

def draw_cuts(range):
  pass

def draw():
  pass

if __name__ == '__main__':
  root_plot.ALICEStyle()
  draw()