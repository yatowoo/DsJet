#!/bin/env python3

import string
import ROOT
from machine_learning_hep.fitting.fitters import FitAliHF

f = ROOT.TFile("../DsJet-pre/pp_data/masshisto.root")

# pt_cand: [3,4,6,8, 12, 24]
# jet_pt : [5, 7, 15, 35]
# xgboost: [0.96, 0.98, 0.94, 0.97, 0.96]

pt_jet_l = [5, 7, 15]
pt_jet_u = [7, 15, 35]
pt_cand_l = [3,4,6,8, 12]
pt_cand_u = [4,6,8, 12, 24]
prob = [0.98, 0.98, 0.94, 0.97, 0.96]

c = ROOT.TCanvas("c1","Fitting",2400,800)
c.Divide(3,1)
c.Draw()

# Check fitters
  # Parameters
fit_pars = {'bkg_func_name': 2,
		 'fit_range_low': 1.75,
		 'fit_range_up': 2.15,
		 'fix_mean': False,
		 'fix_sec_mean': False,
		 'fix_sec_sigma': False,
		 'fix_sigma': False,
		 'include_sec_peak': True,
		 'likelihood': False,
		 'mean': 1.969,
		 'n_sigma_sideband': 4,
		 'rebin': 6,
		 'rel_sigma_bound': 0.5,
		 'sec_mean': 1.869,
		 'sec_sigma': 0.91,
		 'sig_func_name': 0,
		 'sigma': 0.011,
 'use_sec_peak_rel_sigma': True}

# hmass_[i]                                # pt_cand bin
# hmasspt_cand12_24_0.96pt_jet_7.00_15.00  # TH1, inv. mass
# hzvsmasspt_cand12_24_0.96pt_jet_15.00_35.00   # TH2, z vs inv. mass
# hmasspt_cand3_4_0.98pt_jet_5.00_7.00
# hmasspt_cand4_6_0.98pt_jet_5.00_7.00
def histname(prefix, ptCandL, ptCandU, ptJetL, ptJetU, probVal):
  return f'{prefix}pt_cand{ptCandL:.0f}_{ptCandU:.0f}_{probVal:.2f}pt_jet_{ptJetL:.2f}_{ptJetU:.2f}'

def add_text(pave : ROOT.TPaveText, str : string, color=None, size=0.024, align=11):
  text = pave.AddText(str)
  text.SetTextAlign(align)
  text.SetTextSize(size)
  text.SetTextFont(42)
  if(color):
    text.SetTextColor(color)
  return text

# Fit results
def DrawRegion(histo, name, left, right, color, style = 3004):
  binMin = histo.FindBin(left)
  binMax = histo.FindBin(right)
  xLeft = histo.GetBinCenter(binMin) - 0.5 * histo.GetBinWidth(binMin)
  xRight = histo.GetBinCenter(binMax) + 0.5 * histo.GetBinWidth(binMax)
  hRegion = ROOT.TH1F(name,'',binMax-binMin+1, xLeft, xRight)
  for i in range(binMin, binMax+1):
    hRegion.Fill(histo.GetBinCenter(i), histo.GetBinContent(i))
  hRegion.SetDirectory(0)
  hRegion.SetFillColor(color)
  hRegion.SetFillStyle(style)
  hRegion.Draw('same hist')
  return hRegion

fitters = []
for i in range(len(pt_jet_l)):
  fitters.append({"root_obj":[]})
  fitters[i]["pt_jet_l"] = pt_jet_l[i]
  fitters[i]["pt_jet_u"] = pt_jet_u[i]
  fitters[i]["hmass"] = None
  for j in range(len(pt_cand_l)):
    hname = histname('hmass', pt_cand_l[j], pt_cand_u[j], pt_jet_l[i], pt_jet_u[i], prob[j])
    if(not fitters[i]["hmass"]):
      try:
        fitters[i]["hmass"] = f.Get(hname).Clone(f'hmass_jet_{pt_jet_l[i]:.0f}_{pt_jet_u[i]:.0f}')
      except Exception:
        print(hname)
        exit()
    else:
      fitters[i]["hmass"].Add(f.Get(hname))
  fitters[i]["core"] = FitAliHF(fit_pars, histo=fitters[i]["hmass"])
  fitters[i]["core"].fit()
  c.cd(i+1)
  fitters[i]["core"].draw(ROOT.gPad)
  # PaveText
    # Jet pt bin
  fitters[i]["root_obj"].append(fitters[i]["core"].add_pave_helper_(0.3, 0.9, 0.7, 0.99, "NDC"))
  add_text(fitters[i]["root_obj"][-1],
    f"{pt_jet_l[i]:.1f} < #it{{p}}_{{T,jet}} < {pt_jet_u[i]:.1f} (GeV/#it{{c}})",
    size=0.05, align=22)
  fitters[i]["root_obj"][-1].Draw()
    # Ds cand. pt bin
  fitters[i]["root_obj"].append(fitters[i]["core"].add_pave_helper_(0.15, 0.55, 0.4, 0.7, "NDC"))
  add_text(fitters[i]["root_obj"][-1],
    f"{pt_cand_l[0]:.1f} < #it{{p}}_{{T,cand}} < {min(pt_jet_u[i], pt_cand_u[-1]):.1f} (GeV/#it{{c}})",
    size=0.03)
  fitters[i]["root_obj"][-1].Draw()    
  # Values
  result = fitters[i]["core"].kernel
  mu = result.GetMean()
  sigma = result.GetSigma()
  mu_sec = result.GetSecondPeakFunc().GetParameter(1)
  sigma_sec = result.GetSecondPeakFunc().GetParameter(2)
  # Sideband
  n_sigma_signal = 3
  n_sigma_sideband = 5
  sideband_left = 1.75
  n_sigma_sideband_min = 5
  n_sigma_sideband_max = 10
  fitters[i]["signal_l"] = mu - n_sigma_signal * sigma
  fitters[i]["signal_u"] = mu + n_sigma_signal * sigma
  fitters[i]["sideband_left_l"] = mu_sec - n_sigma_sideband * (sigma + sigma_sec)
  fitters[i]["sideband_left_u"] = mu_sec - n_sigma_sideband * sigma_sec
  fitters[i]["sideband_right_l"] = mu + n_sigma_sideband_min * sigma
  fitters[i]["sideband_right_u"] = mu + n_sigma_sideband_max * sigma
    # Signal region
  fitters[i]["hSignal"] = DrawRegion(fitters[i]["core"].histo, f'hSignal_{i}',
    fitters[i]["signal_l"], fitters[i]["signal_u"],
    ROOT.kBlue, 3444)
  fitters[i]["hSBleft"] = DrawRegion(fitters[i]["core"].histo, f'hSBleft_{i}',
    fitters[i]["sideband_left_l"], fitters[i]["sideband_left_u"],
    ROOT.kRed, 3354)
  fitters[i]["hSBright"] = DrawRegion(fitters[i]["core"].histo, f'hSBright_{i}',
    fitters[i]["sideband_right_l"], fitters[i]["sideband_right_u"],
    ROOT.kRed, 3354)

c.SaveAs("test.pdf")

f.Close()