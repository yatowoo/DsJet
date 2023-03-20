#!/usr/bin/env python3

# Render ALICE preliminary figures

import argparse

# Directory contents
# results/
# - unfolding_results.root
# - systematics_results.root
# - yields.root
# model/
# - [pythia8_]charm/beauty_fastsimu_D[].root

parser = argparse.ArgumentParser(description='DsJet pp FF - preliminary figures')
parser.add_argument('-p','--path', default='HP23/results/', help='Directory of results ROOT files, pp_data/')
parser.add_argument('-m','--model', default='HP23/model/', help='Directory of model ROOT files, model/')
parser.add_argument('--sys', default='HP23/results/systematics_results.root', help='Systematic uncertainties')
parser.add_argument('-i','--iter',type=int, default=4, help='N iterations for unfolding')
parser.add_argument('-o','--output',default='DsJetFF-preliminary.root', help='Output file')
parser.add_argument('--extra',default=None, help='unfolding_results.root, Extra variation for comparison')

args = parser.parse_args()


import ROOT
from ROOT import TFile, TH1D, TCanvas, TLegend, TPaveText
from ROOT import kRed, kBlack, kBlue, kWhite, kGray
from array import array
import root_plot

FF_db = {
  'xbins': [  0.5,  0.65,  0.75,  0.85,  0.95],
  'xwidth':[  0.1,  0.05,  0.05,  0.05,  0.05],
  'fd_fr':{
    'x':  [  0.5,  0.65,  0.75,  0.85,  0.95],
    'y':  [0.225, 0.150, 0.159, 0.124,0.0823],
    'exl':[  0.1,  0.05,  0.05,  0.05,  0.05],
    'exh':[  0.1,  0.05,  0.05,  0.05,  0.05],
    'eyl':[0.069, 0.045, 0.047, 0.036, 0.023],
    'eyh':[0.104, 0.069, 0.072, 0.056, 0.036],
    'stats':
          [0.0470, 0.0167, 0.0158, 0.0088, 0.00343],
  },
  'result':{
    'value':[1.1401532487992456, 1.724176622691029, 1.2898143999709701, 1.6379722484777985, 3.067730231261713],
    'stat_err':[0.3328854826107637, 0.3089413083853938, 0.23251800218472218, 0.17782185013302257, 0.16535576809128452],
    'rel_stat':[0.29196556073610513, 0.17918193781285008, 0.18027245019900187, 0.10856218736201183, 0.053901665278852144],
  },
  'rel_sys':{
    'fitting':[0.14185705179160712,0.03061390913998445,0.07577470424896529,0.06120050575454162,0.024889099453537927],
    'sideband sub.':[0.0686720676948628,0.042903688258697066,0.03827440866798068,0.029273180558109357,0.024117004021977913],
    'feed-down':[0.04019865724926155,0.005071693716729552,0.005155782039157784,0.015023007949582081,0.023734388439575732],
    'prior':[0.012191799431693155,0.0045381358105456154,0.02185222418873305,0.012186804310170933,0.004490828621826153],
    'regularisation':[0.006843147890322303,0.007205349759254949,0.02774227241756033,0.006693637288929119,0.000977903589641402],
    'tracking eff.':[0.01637722317315104,0.061091962851334614,0.016021437713521137,0.005160642569285007,0.050197412160425156],
    'BDT selection':[0.20095998586001837,0.1525976556037381,0.09708925345975195,0.04363196444248601,0.044546410921448856],
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
  tg_fd_fr_sys.SetFillStyle(1001)
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
  save_canvas(c_fd_fr_sys)
  # End - fd_fr

def save_canvas(c : ROOT.TCanvas, name = None):
  if name is None:
    name = c.GetName()
  c.Write(name)
  c.SaveAs(name + '.eps')
  c.SaveAs(name + '.pdf')
  c.SaveAs(name + '.png')
  c.SaveAs(name + '.root')


def draw_rel_sys(path=None):
  c_rel_sys = ROOT.TCanvas('c_rel_sys','Canvas for preliminary', 900, 800)
  c_rel_sys.SetRightMargin(0.25)
  c_rel_sys.Draw()
  c_rel_sys.cd()
  leg_relativesys = ROOT.TLegend(.77, .2, 0.95, .85)
  color_i = 0
  gr_stats = ROOT.TGraphErrors(N_BINS,
                         array('d', FF_db['xbins']),
                        array('d',[0.0]*5),
                         array('d', FF_db['xwidth']),
                         array('d', FF_db['result']['rel_stat']))
  gr_stats.SetName('gr_rel_stats')
  gr_stats.SetLineWidth(3)
  gr_stats.SetLineColor(root_plot.COLOR_SET_ALICE[color_i])
  gr_stats.SetMarkerColor(root_plot.COLOR_SET_ALICE[color_i])
  gr_stats.Draw('AP')
  leg_relativesys.AddEntry(gr_stats, 'stat. unc.', 'E')
  gr_relsys = [gr_stats]
  for cat, vals in FF_db['rel_sys'].items():
    color_i +=1
    gr_now = ROOT.TGraphErrors(N_BINS,
                         array('d', FF_db['xbins']),
                         array('d',[0.0]*5),
                         array('d', FF_db['xwidth']),
                         array('d', vals))
    gr_now.SetName('gr_rel_sys_' + cat)
    gr_now.SetLineColor(root_plot.COLOR_SET_ALICE[color_i])
    gr_now.SetMarkerColor(root_plot.COLOR_SET_ALICE[color_i])
    gr_now.SetLineWidth(3)
    gr_now.SetFillStyle(0)
    gr_now.Draw('2')
    gr_now.Write()
    gr_relsys.append(gr_now)
    leg_relativesys.AddEntry(gr_now, cat, 'F')
  # Render
  leg_relativesys.Draw('same')
  gr_stats.GetXaxis().SetRangeUser(0.4, 1)
  gr_stats.GetYaxis().SetRangeUser(-0.32, 0.8)
  gr_stats.GetYaxis().SetTitle('Relative systematic uncertainty')
  gr_stats.GetXaxis().SetTitle('#it{z}_{#parallel}^{ch}')
  pcuts = draw_cuts()
  pcuts.Draw('same')
  alice = root_plot.InitALICELabel(y1=-0.06, type='prel')
  alice.Draw('same')
  # system
  pcoll = ROOT.TPaveText(0.56,0.88,0.70,0.97,"NDC")
  pcoll.SetTextSize(0.03)
  pcoll.SetFillColor(0)
  pcoll.SetBorderSize(0)
  pcoll.AddText('pp #sqrt{#it{s}} = 13 TeV')
  pcoll.Draw('same')
  # Save
  gr_stats.Write()
  save_canvas(c_rel_sys)

def draw_inv_mass(path=None, savefile = None):
  # Require: AliHFInvMassFitter (AliPhysics env.)
  if not getattr(ROOT, 'AliHFInvMassFitter', False):
    print('[x] AliHFInvMassFitter not found. Skip plotting inv. mass.')
    return
  # Input: fitter
  yieldsFile = ROOT.TFile.Open(args.path + '/yields.root')
  dir_fitting = yieldsFile.Get('pt_cand6_8_0.90pt_jet_7.00_15.00')
  mass_fitter = dir_fitting.Get('fitter2')
  # Fitting info.
  mean = mass_fitter.GetMean()
  sigma = mass_fitter.GetSigma()
  fun_bkg = mass_fitter.GetBackgroundRecalcFunc()
  fun_sig = mass_fitter.GetSignalFunc()
  fun_tot = mass_fitter.GetMassFunc()
  fun_sec = mass_fitter.GetSecondPeakFunc()
  mean_sec = fun_sec.GetParameter(1)
  sigma_sec = fun_sec.GetParameter(2)
  hmass = mass_fitter.GetHistoClone()
  # Render
  c_invmass = ROOT.TCanvas('c_invmass_sb','Canvas for preliminary', 900, 800)
  c_invmass.Draw()
  c_invmass.cd()
  lgd = ROOT.TLegend(0.75, 0.5, 0.95, 0.85)
  hmass.SetXTitle('Invariant mass (GeV/#it{c}^{2})')
  hmass.SetYTitle('Counts / (6 MeV/#it{c})')
  hmass.GetXaxis().SetRangeUser(1.71, 2.14)
  hmass.GetYaxis().SetRangeUser(0,340)
  hmass.SetMarkerStyle(root_plot.kRoundHollow)
  hmass.SetLineWidth(2)
  hmass.Draw()
  lgd.AddEntry(hmass, 'data')
  fun_tot.SetLineColor(root_plot.kRed)
  fun_tot.SetLineWidth(2)
  fun_tot.SetNpx(500)
  fun_tot.Draw('same')
  lgd.AddEntry(fun_tot, 'Total fitting')
  fun_bkg.SetLineColor(root_plot.kBlue)
  fun_bkg.SetNpx(500)
  fun_bkg.SetLineWidth(2)
  fun_bkg.Draw('same')
  lgd.AddEntry(fun_bkg, 'Bkg. (pol2)')
  fun_sec.SetLineWidth(2)
  fun_sec.SetNpx(500)
  fun_sec.Draw('same')
  lgd.AddEntry(fun_sec, 'Bkg. (D^{+} gaus.)')
  # Regions
  nsigma_near = 5
  nsigma_away = 10
  nsigma_width = 5
  nsigma_signal = 2
  hSignal = root_plot.DrawRegion(hmass, f'hSignalRegion', mean - nsigma_signal * sigma, mean + nsigma_signal * sigma, ROOT.kRed, 3444)
  lgd.AddEntry(hSignal, 'Signal')
  hSBleft = root_plot.DrawRegion(hmass, f'hSBleft', mean_sec - nsigma_width * (sigma + sigma_sec), mean_sec - nsigma_width * sigma_sec, ROOT.kBlue, 3354)
  hSBright = root_plot.DrawRegion(hmass, f'hSBright', mean + nsigma_near * sigma, mean + nsigma_away * sigma, ROOT.kBlue, 3345)
  lgd.AddEntry(hSBleft, 'Sideband')
  lgd.Draw('same')
  # Text
  pcuts = draw_cuts()
  pcuts.Draw('same')
  alice = root_plot.InitALICELabel(y1=-0.06, type='prel')
  alice.Draw('same')
  # system
  pcoll = ROOT.TPaveText(0.75,0.88,0.95,0.97,"NDC")
  pcoll.SetTextSize(0.03)
  pcoll.SetFillColor(0)
  pcoll.SetBorderSize(0)
  pcoll.AddText('pp #sqrt{#it{s}} = 13 TeV')
  pcoll.Draw('same')
  # Save
  savefile.cd()
  hmass.Write('h_invmass')
  mass_fitter.Write('mass_fitter')
  fun_tot.Write('func_tot')
  fun_bkg.Write('fun_bkg')
  fun_sec.Write('fun_sec')
  fun_sig.Write('fun_sig')
  save_canvas(c_invmass)
  yieldsFile.Close()

if __name__ == '__main__':
  root_plot.ALICEStyle()
  rootFile = ROOT.TFile.Open('preliminary.root','RECREATE')
  draw_fd_fraction()
  draw_rel_sys()
  draw_inv_mass(None, rootFile)
  rootFile.Close()
