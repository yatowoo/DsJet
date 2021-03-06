#!/bin/env python3

# Analyzer script for Ds jet analysis
#
# Dependencies: ROOT, machine_learning_hep
#
# Input
# - masshisto.root: Inv. mass - TH1, Inv. mass vs z - TH2 (for each pT bin)
# - effhisto.root: Yield/counts of hadron - TH1 (generated/selected, prompt/feeddown, for each jet pT bin)
# 
# Output:
# - fitting result: signal, background, sideband and stats
# - raw z shape: signal+background, sideband, subtracted
# - efficiency: prompt & non-prompt
# - z corrected: scale by efficiency

import string

from matplotlib.pyplot import title
import ROOT
from machine_learning_hep.fitting.fitters import FitAliHF
from copy import deepcopy
from ctypes import c_double

from painter import Painter

ROOT.gStyle.SetOptStat(False)
ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gStyle.SetLegendFillColor(ROOT.kWhite)
ROOT.gStyle.SetLegendFont(42)

f = ROOT.TFile("../DsJet-pre/pp_data/masshisto.root")
fEff = ROOT.TFile("../DsJet-pre/pp_mc_prodD2H/effhisto.root")
fOut = ROOT.TFile("DsJet-ff.root","RECREATE")

# pt_cand: [3,4,6,8, 12, 24]
# jet_pt : [5, 7, 15, 35]
# xgboost: [0.96, 0.98, 0.94, 0.97, 0.96]

pt_jet_l = [5, 7, 15]
pt_jet_u = [7, 15, 35]
pt_cand_l = [3,4,6,8, 12]
pt_cand_u = [4,6,8, 12, 24]
prob = [0.98, 0.98, 0.94, 0.97, 0.96]

c = ROOT.TCanvas("c1","Fitting",2400,1600)
c.Divide(3,2)
c.Draw()

cnew = ROOT.TCanvas("c2","Fitting",2400,3200)
cnew.Divide(3,4)
cnew.Draw()

# Check fitters
  # Parameters
fit_pars = {'bkg_func_name': 2, # Pol2, change to 1=Pol1 if failed
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

# Drawing - TODO
def DrawLegend(fitter, objs, labels, xlow, ylow, xup, yup):
  fitter["root_obj"].append(ROOT.TLegend(xlow, ylow, xup, yup))
  ltmp = fitter["root_obj"][-1]
  for obj, label in zip(objs, labels):
    ltmp.AddEntry(obj, label)
  ltmp.Draw("same")
def SetTextFF(hz : ROOT.TH1, xtitle='', ytitle=''):
  hz
def DrawRawFF(p : Painter, fitter):
  p.NextPad()
  fitter["hz_signal"].SetLineColor(ROOT.kBlue)
  fitter["hz_signal"].SetMarkerColor(ROOT.kBlue)
  fitter["hz_sideband"].SetLineColor(ROOT.kRed)
  fitter["hz_sideband"].SetMarkerColor(ROOT.kRed)
  fitter["hz_signal"].GetYaxis().SetRangeUser(0, 2 * fitter["hz_signal"].GetMaximum())
  fitter["hz_signal"].SetTitle("Raw z-distribution, bkg. subtraction using sideband")
  fitter["hz_signal"].Draw()
  fitter["hz_sideband"].Draw('same')
    # Substracted
  fitter["hz_sub"].SetLineColor(ROOT.kBlack)
  fitter["hz_sub"].SetMarkerColor(ROOT.kBlack)
  fitter["hz_sub"].SetLineWidth(2)
  fitter["hz_sub"].Draw("same")
  # Legend
  DrawLegend(fitter, [fitter["hz_signal"], fitter["hz_sideband"], fitter["hz_sub"]], ['Signal', 'Sideband', 'Substracted'],
    0.7, 0.7, 0.9, 0.85)
  # pT range
  fitter["root_obj"].append(fitter["core"].add_pave_helper_(0.2, 0.75, 0.45, 0.9, "NDC"))
  add_text(fitter["root_obj"][-1], fitter["draw_ptcand"], size=0.03)
  add_text(fitter["root_obj"][-1], fitter["draw_ptjet"], size=0.03)
  fitter["root_obj"][-1].Draw()
  return fitter
def AnalyzerJet(p : Painter, fitter):
  # Get histo inv. mass
  nameSuffix = f'cand{fitter["pt_cand_l"]:.0f}-{fitter["pt_cand_u"]:.0f}_jet{fitter["pt_jet_l"]:.0f}-{fitter["pt_jet_u"]:.0f}'
  fitter["root_obj"] = []
  # Fitting
  fitter["core"] = FitAliHF(fit_pars, histo=fitter["hmass"])
  fitter["core"].fit()
  # Attempt: pol1 for bkg.
  if(not fitter["core"].success):
    fit_pars_opt = deepcopy(fit_pars)
    fit_pars_opt["bkg_func_name"] = 1
    fitter["core"] = FitAliHF(fit_pars_opt, histo=fitter["hmass"])
    fitter["core"].fit()
  # Attempt: rebin to 12 MeV/c
  if(not fitter["core"].success):
    fitter["hmass"] = fitter["hmass"].Clone("hmass_rebin_"+nameSuffix)
    fitter["hmass"].Rebin(2)
    fitter["core"] = FitAliHF(fit_pars, histo=fitter["hmass"])
    fitter["core"].fit()
  p.NextPad()
  fitter["core"].draw(p.canvas.cd(p.padIndex))
  if(not fitter["core"].success):
    p.NextPage(title='_FAIL_'+nameSuffix)
    return False
  # PaveText
    # Jet pt bin
  fitter["root_obj"].append(fitter["core"].add_pave_helper_(0.3, 0.9, 0.7, 0.99, "NDC"))
  fitter["draw_ptjet"] = f'{fitter["pt_jet_l"]:.1f} < #it{{p}}_{{T,jet}} < {fitter["pt_jet_u"]:.1f} (GeV/#it{{c}})'
  add_text(fitter["root_obj"][-1],
    fitter["draw_ptjet"], size=0.05, align=22)
  fitter["root_obj"][-1].Draw()
    # Ds cand. pt bin
  fitter["root_obj"].append(fitter["core"].add_pave_helper_(0.15, 0.55, 0.4, 0.7, "NDC"))
  fitter["draw_ptcand"] = f'{fitter["pt_cand_l"]:.1f} < #it{{p}}_{{T,cand}} < {min(fitter["pt_cand_u"], pt_cand_u[-1]):.1f} (GeV/#it{{c}})'
  add_text(fitter["root_obj"][-1], fitter["draw_ptcand"], size=0.03)
  fitter["root_obj"][-1].Draw()
  # Values
  n_sigma_signal = 3
  result = fitter["core"].kernel
  mu = result.GetMean()
  sigma = result.GetSigma()
  mu_sec = result.GetSecondPeakFunc().GetParameter(1)
  sigma_sec = result.GetSecondPeakFunc().GetParameter(2)
  nBkg = c_double()
  errBkg = c_double()
  result.Background(n_sigma_signal, nBkg, errBkg)
  fitBkg = result.GetBackgroundRecalcFunc()
  # Sideband
  n_sigma_sideband = 5
  n_sigma_sideband_min = 5
  n_sigma_sideband_max = 10
  fitter["signal_l"] = mu - n_sigma_signal * sigma
  fitter["signal_u"] = mu + n_sigma_signal * sigma
  fitter["sideband_left_l"] = mu_sec - n_sigma_sideband * (sigma + sigma_sec)
  fitter["sideband_left_u"] = mu_sec - n_sigma_sideband * sigma_sec
  fitter["sideband_right_l"] = mu + n_sigma_sideband_min * sigma
  fitter["sideband_right_u"] = mu + n_sigma_sideband_max * sigma
    # Signal region
  fitter["hSignal"] = DrawRegion(fitter["core"].histo, f'hSignal_{i}',
    fitter["signal_l"], fitter["signal_u"],
    ROOT.kBlue, 3444)
  fitter["hSBleft"] = DrawRegion(fitter["core"].histo, f'hSBleft_{i}',
    fitter["sideband_left_l"], fitter["sideband_left_u"],
    ROOT.kRed, 3354)
  fitter["hSBright"] = DrawRegion(fitter["core"].histo, f'hSBright_{i}',
    fitter["sideband_right_l"], fitter["sideband_right_u"],
    ROOT.kRed, 3354)
  # Raw FF
  recoEff = fitter["eff_val"]
  if(recoEff < 0.0 or recoEff > 1.0):
    print('[X] Error: invalid efficiency found')
    exit()
  h2tmp = fitter['hzvsmass']
  # Signal
  h2tmp_profileZ = h2tmp.ProjectionY(f"_pz_sig",
    h2tmp.FindBin(fitter["signal_l"]),
    h2tmp.FindBin(fitter["signal_u"]))
  fitter["hz_signal"] = h2tmp_profileZ.Clone(f"hz_signal_"+nameSuffix)
  fitter["hz_signal_corrected"] = h2tmp_profileZ.Clone(f"hz_signal_corrected_"+nameSuffix)
  fitter["hz_signal_corrected"].Scale(1. / recoEff)
  # Sideband left
  h2tmp_profileZ = h2tmp.ProjectionY(f"_pz_sbl",
    h2tmp.FindBin(fitter["sideband_left_l"]),
    h2tmp.FindBin(fitter["sideband_left_u"]))
  fitter["hz_sidebandL"] = h2tmp_profileZ.Clone(f"hz_sidebandL_"+nameSuffix)
  fitter["hz_sidebandL_corrected"] = h2tmp_profileZ.Clone(f"hz_sidebandL_corrected_"+nameSuffix)
  fitter["hz_sidebandL_corrected"].Scale(1. / recoEff)
  # Sideband right
  h2tmp_profileZ = h2tmp.ProjectionY(f"_pz_sbr",
    h2tmp.FindBin(fitter["sideband_right_l"]),
    h2tmp.FindBin(fitter["sideband_right_u"]))
  fitter["hz_sidebandR"] = h2tmp_profileZ.Clone(f"hz_sidebandR_"+nameSuffix)
  fitter["hz_sidebandR_corrected"] = h2tmp_profileZ.Clone(f"hz_sidebandL_corrected_"+nameSuffix)
  fitter["hz_sidebandR_corrected"].Scale(1. / recoEff)
    # Substracted
  fitter["hz_sideband"] = fitter["hz_sidebandR"].Clone(f"hz_sideband_"+nameSuffix)
  fitter["hz_sideband"].Add(fitter["hz_sidebandL"])
  area_bkg = fitBkg.Integral(fitter["signal_l"], fitter["signal_u"])
  area_sideband = fitBkg.Integral(fitter["sideband_left_l"], fitter["sideband_left_u"]) + fitBkg.Integral(fitter["sideband_right_l"], fitter["sideband_right_u"])
  area_scale = area_bkg / area_sideband
  fitter["hz_sub"] = fitter["hz_signal"].Clone(f"hz_sub_"+nameSuffix)
  fitter["hz_sub"].Add(fitter["hz_sideband"], -1 * area_scale)
    # Drawing
  DrawRawFF(p, fitter)
    # Corrected
  p.NextPad()
  fitter["hz_sideband_corrected"] = fitter["hz_sidebandL_corrected"].Clone(f"hz_sideband_corrected_"+nameSuffix)
  fitter["hz_sideband_corrected"].Add(fitter["hz_sidebandR_corrected"])
  fitter["hz_sub_corrected"] = fitter["hz_signal_corrected"].Clone(f"hz_sub_corrected_"+nameSuffix)
  fitter["hz_sub_corrected"].Add(fitter["hz_sideband_corrected"], -1 * area_scale)
  fitter["hz_sub_corrected"].GetYaxis().SetRangeUser(0, 2.*fitter["hz_sub_corrected"].GetMaximum())
  fitter["hz_sub_corrected"].SetTitle("Corrected z-distribution")
  fitter["hz_sub_corrected"].SetLineColor(ROOT.kGreen+3)
  fitter["hz_sub_corrected"].SetLineWidth(2)
  fitter["hz_sub_corrected"].Draw("")
    # pT range
  fitter["root_obj"].append(fitter["core"].add_pave_helper_(0.2, 0.75, 0.45, 0.9, "NDC"))
  add_text(fitter["root_obj"][-1], fitter["draw_ptcand"], size=0.03)
  add_text(fitter["root_obj"][-1], fitter["draw_ptjet"], size=0.03)
  fitter["root_obj"][-1].Draw()
  # Output
  p.NextPage(title=nameSuffix)
  return fitter

fitters = [] # integrated pt_cand bins
fitters_ana = [] # (pt_jet, pt_cand)
padAna = Painter(None,printer='analyzer.pdf', nx=3,ny=2,winX=2400,winY=1600)
padAna.PrintCover(title='D_{s}-Jet Analyzer')
for i in range(len(pt_jet_l)):
  fitters.append({"root_obj":[]})
  fitters[i]["pt_jet_l"] = pt_jet_l[i]
  fitters[i]["pt_jet_u"] = pt_jet_u[i]
  fitters[i]["hmass"] = None
  fitters[i]["fit_ptcand"] = []
  c.Clear()
  c.Divide(3,2)
  fitters_ana.append([])
  # Efficiency weight
  nameSuffix = f'_pt_jet_{fitters[i]["pt_jet_l"]:.2f}_{fitters[i]["pt_jet_u"]:.2f}'
    # Prompt
  h_gen_pr = fEff.Get('h_gen_pr' + nameSuffix)
  h_sel_pr = fEff.Get('h_sel_pr' + nameSuffix)
  fitters[i]["heff_pr"] = h_sel_pr.Clone("heff_pr_" + nameSuffix)
  fitters[i]["heff_pr"].SetTitle('D_{s} reco. eff. in |y|<0.5')
  fitters[i]["heff_pr"].SetDirectory(0)
  fitters[i]["heff_pr"].Divide(h_gen_pr)
  cnew.cd(7+i)
  fitters[i]["heff_pr"].SetLineColor(ROOT.kRed)
  fitters[i]["heff_pr"].Draw()
    # Non-Prompt / Feed-down
  h_gen_fd = fEff.Get('h_gen_fd' + nameSuffix)
  h_sel_fd = fEff.Get('h_sel_fd' + nameSuffix)
  fitters[i]["heff_fd"] = h_sel_fd.Clone("heff_fd_" + nameSuffix)
  fitters[i]["heff_fd"].SetDirectory(0)
  fitters[i]["heff_fd"].Divide(h_gen_fd)
  fitters[i]["heff_fd"].SetLineColor(ROOT.kBlack)
  fitters[i]["heff_fd"].Draw("same")
  # Loop on pt_cand bins
  for j in range(len(pt_cand_l)):
    # Test analyzer
    fitters_ana[i].append({})
    fitter = fitters_ana[i][j]
    fitter["pt_jet_l"] = pt_jet_l[i]
    fitter["pt_jet_u"] = pt_jet_u[i]
    fitter["pt_cand_l"] = pt_cand_l[j]
    fitter["pt_cand_u"] = pt_cand_u[j]
    # inv. mass
    hname = histname('hmass', pt_cand_l[j], pt_cand_u[j], pt_jet_l[i], pt_jet_u[i], prob[j])
    htmp = f.Get(hname)
    fitter['hmass'] = htmp
    fitter["eff_val"] = fitters[i]["heff_pr"].GetBinContent(j+1)
    # hz vs mass
    hzname = histname('hzvsmass', pt_cand_l[j], pt_cand_u[j], pt_jet_l[i], pt_jet_u[i], prob[j])
    fitter['hzvsmass'] = f.Get(hzname).Clone(f"hzmass_{i}_{j}")
    AnalyzerJet(padAna, fitter)
    # Integrated 
    if(not fitters[i]["hmass"]):
      try:
        fitters[i]["hmass"] = f.Get(hname).Clone(f'hmass_jet_{pt_jet_l[i]:.0f}_{pt_jet_u[i]:.0f}')
      except Exception:
        print(hname)
        exit()
    else:
      fitters[i]["hmass"].Add(f.Get(hname))
  # End - all pt_cand bins
  c.SaveAs(f"massfit_ptcand_{i}.pdf")
  fitters[i]["core"] = FitAliHF(fit_pars, histo=fitters[i]["hmass"])
  fitters[i]["core"].fit()
  cnew.cd(i+1)
  fitters[i]["core"].draw(cnew.cd(i+1))
  # PaveText
    # Jet pt bin
  fitters[i]["root_obj"].append(fitters[i]["core"].add_pave_helper_(0.3, 0.9, 0.7, 0.99, "NDC"))
  fitters[i]["draw_ptjet"] = f"{pt_jet_l[i]:.1f} < #it{{p}}_{{T,jet}} < {pt_jet_u[i]:.1f} (GeV/#it{{c}})"
  add_text(fitters[i]["root_obj"][-1],fitters[i]["draw_ptjet"],
    size=0.05, align=22)
  fitters[i]["root_obj"][-1].Draw()
    # Ds cand. pt bin
  fitters[i]["root_obj"].append(fitters[i]["core"].add_pave_helper_(0.15, 0.55, 0.4, 0.7, "NDC"))
  fitters[i]["draw_ptcand"] = f"{pt_cand_l[0]:.1f} < #it{{p}}_{{T,cand}} < {min(pt_jet_u[i], pt_cand_u[-1]):.1f} (GeV/#it{{c}})"
  add_text(fitters[i]["root_obj"][-1],fitters[i]["draw_ptcand"],
    size=0.03)
  fitters[i]["root_obj"][-1].Draw()
  # Values
  n_sigma_signal = 3
  result = fitters[i]["core"].kernel
  mu = result.GetMean()
  sigma = result.GetSigma()
  mu_sec = result.GetSecondPeakFunc().GetParameter(1)
  sigma_sec = result.GetSecondPeakFunc().GetParameter(2)
  nBkg = c_double()
  errBkg = c_double()
  result.Background(n_sigma_signal, nBkg, errBkg)
  fitBkg = result.GetBackgroundRecalcFunc()
  # Sideband
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
  # Raw FF - hzvsmass
  fitters[i]["hzvsmass"] = []
  for j in range(len(pt_cand_l)):
    # z vs mass
    hzname = histname('hzvsmass', pt_cand_l[j], pt_cand_u[j], pt_jet_l[i], pt_jet_u[i], prob[j])
    fitters[i]["hzvsmass"].append(f.Get(hzname).Clone(f"hzmass_{i}_{j}"))
    h2tmp = fitters[i]["hzvsmass"][j]
    recoEff = fitters[i]["heff_pr"].GetBinContent(j+1)
    if(recoEff < 0.0 or recoEff > 1.0):
      print('[X] Error: invalid efficiency found')
      exit()
    # Signal
    h2tmp_profileZ = h2tmp.ProjectionY(f"_pz_sig",
      h2tmp.FindBin(fitters[i]["signal_l"]),
      h2tmp.FindBin(fitters[i]["signal_u"]))
    if(not fitters[i].get("hz_signal")):
      fitters[i]["hz_signal"] = h2tmp_profileZ.Clone(f"hz_signal_{i}")
      fitters[i]["hz_signal_corrected"] = h2tmp_profileZ.Clone(f"hz_signal_corrected_{i}")
      fitters[i]["hz_signal_corrected"].Scale(1. / recoEff)
    else:
      fitters[i]["hz_signal"].Add(h2tmp_profileZ)
      fitters[i]["hz_signal_corrected"].Add(h2tmp_profileZ, 1./recoEff)
    # Sideband left
    h2tmp_profileZ = h2tmp.ProjectionY(f"_pz_sbl",
      h2tmp.FindBin(fitters[i]["sideband_left_l"]),
      h2tmp.FindBin(fitters[i]["sideband_left_u"]))
    if(not fitters[i].get("hz_sidebandL")):
      fitters[i]["hz_sidebandL"] = h2tmp_profileZ.Clone(f"hz_sidebandL_{i}")
      fitters[i]["hz_sidebandL_corrected"] = h2tmp_profileZ.Clone(f"hz_sidebandL_{i}_corrected")
      fitters[i]["hz_sidebandL_corrected"].Scale(1. / recoEff)
    else:
      fitters[i]["hz_sidebandL"].Add(h2tmp_profileZ)
      fitters[i]["hz_sidebandL_corrected"].Add(h2tmp_profileZ, 1./recoEff)
    # Sideband right
    h2tmp_profileZ = h2tmp.ProjectionY(f"_pz_sbr",
      h2tmp.FindBin(fitters[i]["sideband_right_l"]),
      h2tmp.FindBin(fitters[i]["sideband_right_u"]))
    if(not fitters[i].get("hz_sidebandR")):
      fitters[i]["hz_sidebandR"] = h2tmp_profileZ.Clone(f"hz_sidebandR_{i}")
      fitters[i]["hz_sidebandR_corrected"] = h2tmp_profileZ.Clone(f"hz_sidebandL_{i}_corrected")
      fitters[i]["hz_sidebandR_corrected"].Scale(1. / recoEff)
    else:
      fitters[i]["hz_sidebandR"].Add(h2tmp_profileZ)
      fitters[i]["hz_sidebandL_corrected"].Add(h2tmp_profileZ, 1./recoEff)
  fitters[i]["hz_signal"].SetLineColor(ROOT.kBlue)
  fitters[i]["hz_sideband"] = fitters[i]["hz_sidebandR"].Clone(f"hz_sideband_{i}")
  fitters[i]["hz_sideband"].Add(fitters[i]["hz_sidebandL"])
  fitters[i]["hz_sideband"].SetLineColor(ROOT.kRed)
  cnew.cd(4+i)
  fitters[i]["hz_signal"].GetYaxis().SetRangeUser(0, 2 * fitters[i]["hz_signal"].GetMaximum())
  fitters[i]["hz_signal"].SetTitle("Raw z-distribution, bkg. subtraction using sideband")
  fitters[i]["hz_signal"].Draw()
  fitters[i]["hz_sideband"].Draw('same')
    # Substracted
  area_bkg = fitBkg.Integral(fitters[i]["signal_l"], fitters[i]["signal_u"])
  area_sideband = fitBkg.Integral(fitters[i]["sideband_left_l"], fitters[i]["sideband_left_u"]) + fitBkg.Integral(fitters[i]["sideband_right_l"], fitters[i]["sideband_right_u"])
  area_scale = area_bkg / area_sideband
  fitters[i]["hz_sub"] = fitters[i]["hz_signal"].Clone(f"hz_sub_{i}")
  fitters[i]["hz_sub"].Add(fitters[i]["hz_sideband"], -1 * area_scale)
  fitters[i]["hz_sub"].SetLineColor(ROOT.kBlack)
  fitters[i]["hz_sub"].SetLineWidth(2)
  fitters[i]["hz_sub"].Draw("same")
    # Corrected
  fitters[i]["hz_sideband_corrected"] = fitters[i]["hz_sidebandL_corrected"].Clone(f"hz_sideband_corrected_{i}")
  fitters[i]["hz_sideband_corrected"].Add(fitters[i]["hz_sidebandR_corrected"])
  fitters[i]["hz_sub_corrected"] = fitters[i]["hz_signal_corrected"].Clone(f"hz_sub_corrected_{i}")
  fitters[i]["hz_sub_corrected"].Add(fitters[i]["hz_sideband_corrected"], -1 * area_scale)
  fitters[i]["hz_sub_corrected"].GetYaxis().SetRangeUser(0, 2.*fitters[i]["hz_sub_corrected"].GetMaximum())
  fitters[i]["hz_sub_corrected"].SetTitle("Corrected z-distribution")
  fitters[i]["hz_sub_corrected"].SetLineColor(ROOT.kGreen+3)
  fitters[i]["hz_sub_corrected"].SetLineWidth(2)
  cnew.cd(10+i)
  fitters[i]["hz_sub_corrected"].Draw("")
    # pT range
  fitters[i]["root_obj"].append( fitters[i]["core"].add_pave_helper_(0.2, 0.75, 0.45, 0.9, "NDC"))
  add_text(fitters[i]["root_obj"][-1], fitters[i]["draw_ptcand"], size=0.03)
  add_text(fitters[i]["root_obj"][-1], fitters[i]["draw_ptjet"], size=0.03)
  fitters[i]["root_obj"][-1].Draw()
  fitters[i]["draw_ptpave"] = fitters[i]["root_obj"][-1]
cnew.SaveAs("test.pdf")

for i in range(len(pt_jet_l)):
  for j in range(len(pt_cand_l)):
    padAna.NextPad()
    fitters_ana[i][j]['core'].draw(ROOT.gPad)
  padAna.NextPage(f'InvMassFit_jet{pt_jet_l[i]:.0f}-{pt_jet_u[i]:.0f}')

for i in range(len(pt_jet_l)):
  # Merge plots
  padAna.NextPad()
  for j in range(len(pt_cand_l)):
    ptCenter = fitters[i]["heff_pr"].GetBinCenter(j+1)
    if(ptCenter > pt_jet_u[i]):
      fitters[i]["heff_pr"].SetBinContent(j+1, 0.)
      fitters[i]["heff_fd"].SetBinContent(j+1, 0.)
    # Efficiency
  fitters[i]["heff_pr"].SetLineColor(ROOT.kRed)
  fitters[i]["heff_pr"].SetMarkerColor(ROOT.kRed)
  fitters[i]["heff_pr"].GetYaxis().SetRangeUser(0, 1.5*fitters[i]["heff_pr"].GetMaximum())
  fitters[i]["heff_pr"].Draw()
    # Non-Prompt / Feed-down
  fitters[i]["heff_fd"].SetLineColor(ROOT.kBlack)
  fitters[i]["heff_fd"].SetMarkerColor(ROOT.kBlack)
  fitters[i]["heff_fd"].Draw("same")
  fitters[i]["draw_ptpave"].Draw("same")
  DrawLegend(fitters[i], [fitters[i]["heff_pr"], fitters[i]["heff_fd"]], ['Prompt','Feed-down'], 0.7, 0.25, 0.9, 0.35)
padAna.NextPage('Efficiency')

for i in range(len(pt_jet_l)):
  # Merge plots
  padAna.NextPad()
  fitters[i]["hz_sub_corrected"].Draw("")
  fitters[i]["draw_ptpave"].Draw("same")
padAna.NextPage('FF_EffCorrected')

padAna.PrintBackCover()
f.Close()
fEff.Close()
fOut.Close()