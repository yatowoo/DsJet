#!/bin/env python3

# Code from analyzerdhadrons_mult.py::fit()

from array import array
import os, itertools
from root_numpy import hist2array, array2hist
from ROOT import TFile, TH1F, TH2F, TCanvas, TPad, TF1, TH1D
from ROOT import gStyle, TLegend, TLine, TText, TPaveText, TArrow
from ROOT import gROOT, TDirectory, TPaveLabel
from ROOT import TStyle, kBlue, kGreen, kBlack, kRed, kOrange
from ROOT import TLatex
from ROOT import gInterpreter, gPad
# HF specific imports
from machine_learning_hep.fitting.helpers import MLFitter
from machine_learning_hep.logger import get_logger
from machine_learning_hep.io import dump_yaml_from_dict
from machine_learning_hep.utilities import folding, get_bins, make_latex_table, parallelizer
from machine_learning_hep.root import save_root_object
from machine_learning_hep.utilities_plot import plot_histograms
from machine_learning_hep.analysis.analyzer import Analyzer

import pickle, lz4.frame, yaml

# Database parameters
configFile = '/home/yitao/DsJet/database_ml_parameters_DsJet_test.yml'

datap = yaml.safe_load(open(configFile, 'r'))
massData = '/home/yitao/output/DsMultJet-test/pp_data/masshisto.root'
massMC = '/home/yitao/output/DsMultJet-test/pp_sim_D2H/masshisto.root'
case = 'DsJetpp'
typeana = 'MBvspt_ntrkl'
dirOut = '/home/yitao/output/DsMultJet-test/ana/'
fileOut = 'yield_test.root'

gROOT.SetBatch(True)

fitter = MLFitter(case, datap[case], typeana, massData, massMC)
fitter.perform_pre_fits()
fitter.perform_central_fits()

fout = TFile(dirOut + fileOut, 'RECREATE')
fitter.draw_fits(dirOut, fout)

# Fit results
def DrawRegion(histo, name, left, right, color, style = 3004):
  binMin = histo.FindBin(left)
  binMax = histo.FindBin(right)
  xLeft = histo.GetBinCenter(binMin) - 0.5 * histo.GetBinWidth(binMin)
  xRight = histo.GetBinCenter(binMax) + 0.5 * histo.GetBinWidth(binMax)
  hRegion = TH1F(name,'',binMax-binMin+1, xLeft, xRight)
  for i in range(binMin, binMax+1):
    hRegion.Fill(histo.GetBinCenter(i), histo.GetBinContent(i))
  hRegion.SetFillColor(color)
  hRegion.SetFillStyle(style)
  hRegion.Draw('same hist')
  return hRegion

confAna = datap[case]['analysis'][typeana]
n_sigma_signal = 3
n_sigma_sideband = 5
sideband_left = 1.75
n_sigma_sideband_min = 5
n_sigma_sideband_max = 10
canvas = TCanvas('cFit','Fit Ds pt bins',2100,1400)
canvas.Divide(3,2)
for iPtBin in confAna['binning_matching']:
  ptMin = confAna['sel_an_binmin'][iPtBin]
  ptMax = confAna['sel_an_binmax'][iPtBin]
  sideband_left = confAna['massmin'][iPtBin] + 0.02
  fit = fitter.get_central_fit(iPtBin, 0) # Var2 0 = Mult. 0-9999
  mean = fit.kernel.GetMean()
  sigma = fit.kernel.GetSigma()
  nSignal = fit.kernel.GetRawYield()
  fit2 = fit.kernel.GetSecondPeakFunc()
  mean2 = fit2.GetParameter(1)
  sigma2 = fit2.GetParameter(2)
  #nBkg = Double()
  #errBkg = Double()
  #self.kernel.Background(n_sigma_signal, nBkg, errBkg)
  # Draw signal
  canvas.cd(iPtBin+1)
  fout.cd()
  fit.draw(canvas.cd(iPtBin+1),title=f'{ptMin:.1f}' + '< #it{p}_{T,cand} <' + f'{ptMax:.1f}')
  hSignal = DrawRegion(fit.histo, f'hSig{iPtBin}', mean - n_sigma_signal * sigma, mean + n_sigma_signal * sigma, kBlue, 3444)
  hSignal.Write()
  # Draw sideband
  hSBleft = DrawRegion(fit.histo, f'hSBleft{iPtBin}', mean2 - n_sigma_sideband * (sigma + sigma2), mean2 - n_sigma_sideband * sigma2, kRed, 3354)
  hSBleft.Write()
  hSBright = DrawRegion(fit.histo, f'hSBright{iPtBin}', mean + n_sigma_sideband_min * sigma, mean + n_sigma_sideband_max * sigma, kRed, 3345)
  hSBright.Write()

fout.cd()
canvas.SaveAs(dirOut + '/yield_invmass_fit.pdf')
canvas.Write()
fout.Close()

