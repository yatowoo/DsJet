#!/usr/bin/env python3

# Render ALICE preliminary figures

import argparse
from copy import deepcopy
import pprint
import math

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
    'sys_err':[0.293077, 0.294699, 0.181021, 0.13501, 0.243771],
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
  },
  'result_D0':{
    'x':  [  0.5,  0.65,  0.75,  0.85,  0.95],
    'y':  [1.381, 1.833, 1.914, 1.676, 1.833],
    'exl':[  0.1,  0.05,  0.05,  0.05,  0.05],
    'exh':[  0.1,  0.05,  0.05,  0.05,  0.05],
    'eyl':[0.238, 0.143, 0.133, 0.095, 0.119],
    'eyh':[0.190, 0.101, 0.119, 0.058, 0.119],
    'stats':[0.073, 0.091, 0.082, 0.067, 0.058],
  },
  'model':{
    'Ds': {
      'pythia6_powheg':'charm_fastsimu_Ds.root',
      'pythia8':'pythia8_charm_fastsimu_Ds.root',
      'pythia8_cr0':'pythia8cr0_charm_fastsimu_Ds.root',
      'pythia8_cr2':'pythia8cr2_charm_fastsimu_Ds.root',
    },
    'D0':{
      'pythia6_powheg':'charm_fastsimu_D0.root',
      'pythia8':'pythia8_charm_fastsimu_D0.root',
      'pythia8_cr0':'pythia8cr0_charm_fastsimu_D0.root',
      'pythia8_cr2':'pythia8cr2_charm_fastsimu_D0.root',
    },
  },
  'model_data':{
'D0': {'pythia6_powheg': {'err': [0.005755199817989637,
                                   0.010061199781847198,
                                   0.010610018638697824,
                                   0.010599502053268551,
                                   0.010945446694122516],
                           'val': [1.1308491693418001,
                                   1.7280385219204728,
                                   1.9217025564121173,
                                   1.91789488483258,
                                   2.1706656981512293]},
        'pythia8': {'err': [0.005755087835737462,
                            0.009050394755741105,
                            0.008887086887476716,
                            0.008312667525287918,
                            0.008516749747177522],
                    'val': [1.5227727510005218,
                            1.8829389246563428,
                            1.8155994431877485,
                            1.5884809465808252,
                            1.6674351835740384]},
        'pythia8_cr0': {'err': [0.006971863055522793,
                                0.01033484997225083,
                                0.010088942033209092,
                                0.009659365778679903,
                                0.009866403429310678],
                        'val': [1.637497551100373,
                                1.7991249265330118,
                                1.7145265757555954,
                                1.5716295720213966,
                                1.639723823489252]},
        'pythia8_cr2': {'err': [0.006872749453741715,
                                0.010304331667496055,
                                0.010174568114966217,
                                0.009712075998997566,
                                0.00972131071348784],
                        'val': [1.6080765118492324,
                                1.8074044483086795,
                                1.762169402309923,
                                1.6056091457038457,
                                1.6086639799790865]}},
 'Ds': {'pythia6_powheg': {'err': [0.014267697148673934,
                                   0.02560060180321059,
                                   0.02715782802604143,
                                   0.027143527657493702,
                                   0.03058950679066015],
                           'val': [1.033103448275862,
                                   1.6630541871921185,
                                   1.8715270935960573,
                                   1.869556650246306,
                                   2.529655172413794]},
        'pythia8': {'err': [0.012681745176149813,
                            0.0206925871642257,
                            0.0202843674173749,
                            0.01955503770291138,
                            0.020832531673832477],
                    'val': [1.3802144022372411,
                            1.837333954789094,
                            1.765555814495454,
                            1.6408762526217668,
                            1.9958051736192037]},
        'pythia8_cr0': {'err': [0.01602641624487138,
                                0.02445993644423467,
                                0.02430472465875974,
                                0.023186660951181284,
                                0.024947792835945053],
                        'val': [1.5053745094693742,
                                1.7532844224535065,
                                1.7311039071830727,
                                1.5754990615935847,
                                1.929363589831087]},
        'pythia8_cr2': {'err': [0.01568584454415444,
                                0.024597593151126543,
                                0.024250053881836948,
                                0.023217658951022534,
                                0.024712353469748646],
                        'val': [1.4627417998317915,
                                1.7984861227922626,
                                1.7480235492010079,
                                1.6023549201009255,
                                1.9256518082422207]}},
  }
}

Z_BINNING = [0.4,0.6,0.7,0.8,0.9,1.0]
N_BINS = len(Z_BINNING)-1

def draw_cuts(range=None):
  ptxt = ROOT.TPaveText(0.15,0.68,0.60,0.90,"NDC")
  ptxt.SetTextAlign(13)
  ptxt.SetBorderSize(0)
  ptxt.SetTextSize(0.03)
  ptxt.SetFillColor(0)
  ptxt.SetTextFont(42)
  ptxt.AddText('D_{s}^{+}-tagged charged jets, anti-#it{k}_{T}, #it{R} = 0.4')
  ptxt.AddText('7 < #it{p}_{T}^{jet ch.} < 15 GeV/#it{c}, ' +'|#it{#eta}_{jet ch.}| #leq 0.5')
  ptxt.AddText('3 < #it{p}_{T}^{D_{s}^{+}} < 15 GeV/#it{c}, ' +'|#it{y}_{D_{s}^{+}}| #leq 0.8')
  return ptxt

def draw_fd_fraction(path=None):
  c_fd_fr_sys = ROOT.TCanvas('c_fd_fr', 'canvas for preliminary', 1200,1200)
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
  tg_fd_fr_sys.GetYaxis().SetRangeUser(0., 0.63)
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
  ptxtR = ROOT.TPaveText(0.65,0.90,0.95,0.95,"NDC")
  ptxtR.SetTextSize(0.03)
  ptxtR.SetFillColor(0)
  ptxtR.SetBorderSize(0)
  ptxtR.AddText('pp #sqrt{#it{s}} = 13 TeV')

  ptxtM = ROOT.TPaveText(0.62,0.65,0.95,0.70,"NDC")
  ptxtM.SetTextSize(0.025)
  ptxtM.SetFillColor(0)
  ptxtM.SetBorderSize(0)
  ptxtM.AddText('POWHEG+PYTHIA 6+EvtGen')
  # Legend
  lgd = ROOT.TLegend(0.62,0.55,0.95,0.65)
  lgd.SetTextSize(0.025)
  lgd.AddEntry(h_fd_fr_sys, 'POWHEG estimation')
  lgd.AddEntry(tg_fd_fr_sys, 'POWHEG uncertainty')
  # Render
  tg_fd_fr_sys.Draw('A2 P')
  alice.Draw('same')
  h_fd_fr_sys.Draw('P')
  lgd.Draw('same')
  pcuts.Draw('same')
  ptxtR.Draw('same')
  ptxtM.Draw('same')
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
  c_rel_sys = ROOT.TCanvas('c_rel_sys','Canvas for preliminary', 1200, 900)
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
  gr_stats.GetYaxis().SetRangeUser(-0.35, 0.8)
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
  c_invmass = ROOT.TCanvas('c_invmass_sb','Canvas for preliminary', 1200, 1200)
  c_invmass.Draw()
  c_invmass.cd()
  lgd = ROOT.TLegend(0.72, 0.5, 0.95, 0.85)
  hmass.SetXTitle('Invariant mass (GeV/#it{c}^{2})')
  hmass.SetYTitle('Counts per 6 MeV/#it{c}')
  hmass.GetXaxis().SetRangeUser(1.71, 2.14)
  hmass.GetYaxis().SetRangeUser(0,360)
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
  hSBright = root_plot.DrawRegion(hmass, f'hSBright', mean + nsigma_near * sigma, mean + nsigma_away * sigma, ROOT.kBlue, 3354)
  lgd.AddEntry(hSBleft, 'Sideband')
  lgd.Draw('same')
  # Text
  pcuts = draw_cuts()
  pcuts.Draw('same')
  alice = root_plot.InitALICELabel(y1=-0.06, type='prel')
  alice.Draw('same')
  # system
  pcoll = ROOT.TPaveText(0.72,0.88,0.90,0.97,"NDC")
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

def convert_model_data():
  fout = ROOT.TFile.Open(args.model + '/' + 'FF_pythia_hz_DsD0_ptjet_7_15_rebin.root', 'RECREATE')
  for cand in ['Ds', 'D0']:
    for name, modelfile in FF_db['model'][cand].items():
      f = ROOT.TFile.Open(args.model + '/' + modelfile)
      if f.IsOpen():
        print('[-] Processing : ' + modelfile)
      mdata = {'val':[],'err':[]}
      hModelRaw = f.Get('hz_ptjet_7_15')
      hModel = hModelRaw.Rebin(N_BINS, 'hz_'+cand+'_'+name+'_rebin', array('d', Z_BINNING))
      isolatedCandJet = hModelRaw.GetBinContent(hModelRaw.FindBin(1.001)) + hModel.GetBinContent(hModel.FindBin(0.99))
      hModel.SetBinContent(hModel.FindBin(0.99), isolatedCandJet)
      hModel.Scale(1./hModel.Integral(),'width')
      for i in range(1,N_BINS+1):
        mdata['val'].append(hModel.GetBinContent(i))
        mdata['err'].append(hModel.GetBinError(i))
      FF_db['model_data'][cand][name] = deepcopy(mdata)
      fout.WriteObject(hModel, hModel.GetName())
      f.Close()
  fout.Close()
  pprint.pprint(FF_db['model_data'])
  pass

def draw_result():
  # Ds data vs model comparison
  pass

def draw_result_ratio():
  # Ds / D0 comparison
    # D0
  h_dzero = ROOT.TH1F('hz_D0','FF D0',N_BINS,array('d', Z_BINNING))
  tg_dzero_sys = ROOT.TGraphAsymmErrors(5,
    array('d', FF_db['result_D0']['x']),
    array('d', FF_db['result_D0']['y']),
    array('d', FF_db['result_D0']['exl']),
    array('d', FF_db['result_D0']['exh']),
    array('d', FF_db['result_D0']['eyl']),
    array('d', FF_db['result_D0']['eyh']))
    # Ds
  h_ds = ROOT.TH1F('hz_Ds','FF Ds',N_BINS,array('d', Z_BINNING))
  tg_ds_sys = ROOT.TGraphAsymmErrors(5,
    array('d', FF_db['xbins']),
    array('d', FF_db['result']['value']),
    array('d', FF_db['xwidth']),
    array('d', FF_db['xwidth']),
    array('d', FF_db['result']['sys_err']),
    array('d', FF_db['result']['sys_err']))
  # Ratio
  hratio_powheg = ROOT.TH1F('hratio_powheg','FF Ds/D0',N_BINS,array('d', Z_BINNING))
  hratio_py8cr2 = ROOT.TH1F('hratio_py8cr2','FF Ds/D0',N_BINS,array('d', Z_BINNING))
  db_dsdzero_ratio = []
  db_dsdzero_ratio_sys_err = []
  for i in range(0,N_BINS):
    h_dzero.SetBinContent(i+1, FF_db['result_D0']['y'][i])
    h_dzero.SetBinError(i+1, FF_db['result_D0']['stats'][i])
    h_ds.SetBinContent(i+1, FF_db['result']['value'][i])
    h_ds.SetBinError(i+1, FF_db['result']['stat_err'][i])
    hratio_powheg.SetBinContent(i+1, FF_db['model_data']['Ds']['pythia6_powheg']['val'][i] / FF_db['model_data']['D0']['pythia6_powheg']['val'][i])
    hratio_py8cr2.SetBinContent(i+1, FF_db['model_data']['Ds']['pythia8_cr2']['val'][i] / FF_db['model_data']['D0']['pythia8_cr2']['val'][i])
    # ratio_val
    ratio_val = FF_db['result']['value'][i] / FF_db['result_D0']['y'][i]
    db_dsdzero_ratio.append(ratio_val)
    ratio_err_ds = FF_db['result']['sys_err'][i] / FF_db['result']['value'][i]
    ratio_err_dzero = FF_db['result_D0']['eyl'][i] / FF_db['result_D0']['y'][i]
    db_dsdzero_ratio_sys_err.append(ratio_val * math.sqrt(ratio_err_ds**2 + ratio_err_dzero**2))
  hratio = h_ds.Clone('hratio_dsd0_data')
  hratio.Divide(h_dzero)
  tg_ds_ratio_sys = ROOT.TGraphAsymmErrors(5,
    array('d', FF_db['xbins']),
    array('d', db_dsdzero_ratio),
    array('d', FF_db['xwidth']),
    array('d', FF_db['xwidth']),
    array('d', db_dsdzero_ratio_sys_err),
    array('d', db_dsdzero_ratio_sys_err))
  # Render
    # Pads
  c_FF_ratio = TCanvas('c_FF_ratio','preliminary plots',1200,1200)
  pMain, pRatio = root_plot.NewRatioPads(c_FF_ratio.cd(), f'padz', f'padratio', gap=0.0, ratio=0.4)
  c_FF_ratio.cd()
  pMain.SetBottomMargin(0.0)
  pRatio.SetTopMargin(0.0)
  pRatio.SetBottomMargin(0.3)
  # Main
  pMain.cd()
    # Color, Marker and line
    # Ds
  h_ds.UseCurrentStyle()
  h_ds.SetMarkerStyle(root_plot.kRoundHollow)
  h_ds.SetMarkerSize(2)
  h_ds.SetLineWidth(2)
  h_ds.SetLineColor(kBlack)
  h_ds.SetMarkerColor(kBlack)
  tg_ds_sys.SetLineColor(kBlack)
  tg_ds_sys.SetMarkerColor(kBlack)
  tg_ds_sys.SetMarkerStyle(root_plot.kRoundHollow)
  tg_ds_sys.SetMarkerSize(2)
  tg_ds_sys.SetLineWidth(0)
  tg_ds_sys.SetFillColorAlpha(root_plot.kGray+1, 0.9)
  tg_ds_sys.SetFillStyle(1001)
    # D0
  h_dzero.SetMarkerStyle(root_plot.kBlockHollow)
  h_dzero.SetMarkerSize(2)
  h_dzero.SetLineWidth(2)
  h_dzero.SetLineColor(root_plot.kCyan+2)
  h_dzero.SetMarkerColor(root_plot.kCyan+2)
  tg_dzero_sys.SetLineColor(root_plot.kCyan+2)
  tg_dzero_sys.SetMarkerColor(root_plot.kCyan+2)
  tg_dzero_sys.SetMarkerStyle(root_plot.kBlockHollow)
  tg_dzero_sys.SetMarkerSize(2)
  tg_dzero_sys.SetLineWidth(0)
  tg_dzero_sys.SetFillColorAlpha(root_plot.kCyan-8, 0.9)
  tg_dzero_sys.SetFillStyle(1001)
    # Axis
  h_ds.GetXaxis().SetRangeUser(0.4,1.0)
  h_ds.GetYaxis().SetRangeUser(0.1, 2. * h_ds.GetMaximum())
  h_ds.SetXTitle('#it{z}_{#parallel}^{ch}')
  h_ds.GetYaxis().SetTitle('(1/#it{N}_{jet}) d#it{N}/d#it{z}_{#parallel}^{ch}')
  h_ds.GetYaxis().SetTitleOffset(0.8)
  h_ds.GetYaxis().SetTitleSize(0.08)
  h_ds.GetYaxis().SetLabelSize(0.09)
    # Draw main
  ROOT.gStyle.SetErrorX(0)
  h_ds.Draw('E0')
  tg_ds_sys.Draw('2 P')
  h_ds.Draw('same')
  tg_dzero_sys.Draw('2 P')
  h_dzero.Draw('same')
    # Text
  mainTextSize = 0.06
  alice = root_plot.InitALICELabel(y1=-0.06, type='prel', size=mainTextSize)
  alice.Draw('same')
  pave = ROOT.TPaveText(0.16,0.45,0.54,0.85,"NDC")
  pave.SetFillColor(kWhite)
  root_plot.add_text(pave, 'pp #sqrt{#it{s}} = 13 TeV', size=mainTextSize)
  root_plot.add_text(pave, 'charged jets, anti-#it{k}_{T}, #it{R} = 0.4', size=mainTextSize)
  root_plot.add_text(pave, '7 < #it{p}_{T}^{jet ch.} < 15 GeV/#it{c}, ' +'|#it{#eta}_{jet ch.}| #leq 0.5', size=mainTextSize)
  root_plot.add_text(pave, '3 < #it{p}_{T}^{h} < 15 GeV/#it{c}, ' +'|#it{y}_{h}| #leq 0.8', size=mainTextSize)
  pave.Draw('same')
    # Legend
  lgd = ROOT.TLegend(0.66,0.78,0.95,0.93)
  lgd.SetTextSize(mainTextSize)
  lgd.SetFillColorAlpha(0,0)
  lgd.AddEntry(tg_ds_sys, 'D_{s}^{+}-tagged jets')
  lgd.AddEntry(tg_dzero_sys, 'D^{0}-tagged jets')
  lgd.Draw('same')
  # Ratio
  pRatio.cd()
    # data
  hratio.SetMarkerStyle(root_plot.kDiamondHollow)
  hratio.SetMarkerSize(3)
  hratio.SetLineWidth(4)
  hratio.SetLineColor(root_plot.kOrange-1)
  hratio.SetMarkerColor(root_plot.kOrange-1)
  hratio.GetXaxis().SetRangeUser(0.4,1.0)
  hratio.GetYaxis().SetRangeUser(0.1, 2.13)
  hratio.SetXTitle('#it{z}_{#parallel}^{ch}')
  hratio.GetYaxis().SetTitle('D_{s}^{+}/D^{0}')
  hratio.GetYaxis().SetNdivisions(505)
  hratio.SetTitleSize(0.13,"xy")
  hratio.GetXaxis().SetTitleOffset(0.8)
  hratio.GetYaxis().SetTitleOffset(0.51)
  hratio.GetXaxis().SetLabelSize(0.12)
  hratio.GetYaxis().SetLabelSize(0.12)
  tg_ds_ratio_sys.SetLineColor(root_plot.kOrange-1)
  tg_ds_ratio_sys.SetMarkerColor(root_plot.kOrange-1)
  tg_ds_ratio_sys.SetMarkerStyle(root_plot.kDiamondHollow)
  tg_ds_ratio_sys.SetMarkerSize(3)
  tg_ds_ratio_sys.SetLineWidth(0)
  tg_ds_ratio_sys.SetFillColorAlpha(root_plot.kOrange-9, 0.9)
  tg_ds_ratio_sys.SetFillStyle(1001)
    # model
  hratio_powheg.SetLineStyle(2)
  hratio_powheg.SetLineColor(root_plot.kRed+1)
  hratio_powheg.SetLineWidth(4)
  hratio_py8cr2.SetLineStyle(9)
  hratio_py8cr2.SetLineColor(root_plot.kGreen+3)
  hratio_py8cr2.SetLineWidth(4)
   # Draw
  hratio.Draw('E0')
  tg_ds_ratio_sys.Draw('2 P')
  hratio.Draw('same')
  hratio_powheg.Draw('same')
  hratio_py8cr2.Draw('same')
    # Legend
  ratioTextSize = 0.08
  lgd_data = ROOT.TLegend(0.16, 0.84, 0.50, 0.93)
  lgd_data.SetTextSize(ratioTextSize)
  lgd_data.AddEntry(tg_ds_ratio_sys, 'data')
  lgd_data.Draw('same')
  lgd_model = ROOT.TLegend(0.30, 0.7, 0.6, 0.95)
  lgd_model.SetTextSize(ratioTextSize)
  lgd_model.AddEntry(hratio_powheg, 'POWHEG + PYTHIA 6')
  lgd_model.AddEntry(hratio_py8cr2, 'PYTHIA 8 CR-BLC Mode 2')
  lgd_model.Draw('same')
  # Save
  h_ds.Write()
  h_dzero.Write()
  tg_ds_sys.Write()
  tg_dzero_sys.Write()
  hratio.Write()
  hratio_powheg.Write()
  hratio_py8cr2.Write()
  save_canvas(c_FF_ratio)

if __name__ == '__main__':
  #convert_model_data()
  #exit()
  root_plot.ALICEStyle()
  rootFile = ROOT.TFile.Open('preliminary.root','RECREATE')
  draw_fd_fraction()
  draw_rel_sys()
  draw_inv_mass(None, rootFile)
  draw_result_ratio()
  rootFile.Close()
