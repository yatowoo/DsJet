#!/usr/bin/env python3

# Present FF results and model comparison

import argparse

parser = argparse.ArgumentParser(description='FF results')
parser.add_argument('-f','--file', default='/mnt/d/DsJet/systematics/merged_full0714/pp_data/unfolding_results.root', help='Unfolded data results')
parser.add_argument('-m','--model', default='/mnt/d/DsJet/fastsimu/', help='Model outputs')
parser.add_argument('--sys', default='/mnt/d/DsJet/systematics/merged_full0705/pp_data/systematics_results.root', help='Systematic uncertainties')
parser.add_argument('-i','--iter',type=int, default=4, help='N iterations for unfolding')
parser.add_argument('-o','--output',default='DsJetFF-results.root', help='Output file')
parser.add_argument('--extra',default=None, help='unfolding_results.root, Extra variation for comparison')
parser.add_argument('--dzero',default=False, action='store_true', help='Compare with D0 results from ALICE')

args = parser.parse_args()

# result: unfolded_z_[Niter]_pt_jet_15.00_35.00
# model: hz_ptjet_7_15

import ROOT
from ROOT import TFile, TH1D, TCanvas, TLegend, TPaveText
from ROOT import kRed, kBlack, kBlue, kWhite, kGray
from array import array
import root_plot

root_plot.ALICEStyle()

# Output from feeddown.py (alice-fast-simulation)
model_db = {
  "pythia6":{
    "label": "POWHEG+PYTHIA6",
    "file": "charm_fastsimu_Ds.root",
    "color": root_plot.kRed+1,
    "line": 2, # dashed
  },
  "pythia8":{
    "label": "Monash",
    "file": "pythia8_charm_fastsimu_Ds.root",
    "color": root_plot.kBlue+1,
    "line": 6, # dashed
  },
  "pythia8_cr2":{
    "label": "CR-BLC Mode 2",
    "file": "pythia8cr2_charm_fastsimu_Ds.root",
    "color": root_plot.kGreen+3,
    "line": 9, # dashed
  },
  "pythia8_cr0":{
    "label": "PYTHIA 8 CR Mode 0",
    "file": "charm_fastsimu_Ds.root",
    "color": root_plot.kMagenta+1,
    "line": 2, # dashed
  },
}

# D0-tagged jets result (from Lc-jet paper)
FF_db = {
  'D0':{
    'x':  [  0.5,  0.65,  0.75,  0.85,  0.95],
    'y':  [1.381, 1.833, 1.914, 1.676, 1.833],
    'exl':[  0.1,  0.05,  0.05,  0.05,  0.05],
    'exh':[  0.1,  0.05,  0.05,  0.05,  0.05],
    'eyl':[0.238, 0.143, 0.133, 0.095, 0.119],
    'eyh':[0.190, 0.101, 0.119, 0.058, 0.119],
  }
}
FF_db['D0']['result'] = ROOT.TGraphAsymmErrors(5,
  array('d', FF_db['D0']['x']),
  array('d', FF_db['D0']['y']),
  array('d', FF_db['D0']['exl']),
  array('d', FF_db['D0']['exh']),
  array('d', FF_db['D0']['eyl']),
  array('d', FF_db['D0']['eyh']))
FF_db['D0']['result'].SetName('FF_D0_ALICEpp13TeV_pt_jet_7_15')
FF_db['D0']['result'].SetLineWidth(0)
FF_db['D0']['result'].SetMarkerColor(root_plot.kGreen+3)
FF_db['D0']['result'].SetFillColor(root_plot.kGreen-8)
FF_db['D0']['result'].SetMarkerStyle(root_plot.kBlock)
FF_db['D0']['result'].SetMarkerSize(1.5)
FF_db['D0']['result'].SetFillStyle(1001)
FF_db['D0']['result'].SetDrawOption('2P')

# args.extra = '/mnt/d/DsJet/Ongoing/ana-705test/DsJet-test/pp_data/unfolding_results.root'

model_plotting = ['pythia6', 'pythia8', 'pythia8_cr2']
if args.extra or args.dzero:
  model_plotting = ['pythia8']

Z_BINNING = [0.4,0.6,0.7,0.8,0.9,1.0]
PT_JET_BINNING = [5, 7, 15, 35]
pt_cand_l = [3, 3, 8]
pt_cand_u = [7, 15, 24]
N_JETBINS = 3
fResult = TFile.Open(args.file)
fExtra = None

if args.extra:
  fExtra = TFile.Open(args.extra)
fSysematics = TFile.Open(args.sys)

c = TCanvas('c1','draw',1200,1200)
#c.Divide(N_JETBINS) # Issue - figure distorted when subcanvas.SaveAs

def add_text(pave : TPaveText, s : str, color=None, size=0.04, align=11):
  text = pave.AddText(s)
  text.SetTextAlign(align)
  text.SetTextSize(size)
  text.SetTextFont(42)
  if(color):
    text.SetTextColor(color)
  return text

root_objs = []

def newObj(obj):
  global root_objs
  root_objs.append(obj)
  return root_objs[-1]

def draw_model(model_name : dict, pt_jet_l=5, pt_jet_u=7):
  """
  """
  model_vars = model_db[model_name]
  fModel = TFile.Open(args.model + '/' + model_vars['file'])
  suffix = f'{pt_jet_l:.0f}_{pt_jet_u:.0f}'
  hname = f'hz_ptjet_{suffix}'
  hnameNew = f'{hname}_{model_name}'
  hModelRaw = fModel.Get(f'hz_ptjet_{suffix}')
  model_vars['hist_z'] = newObj(hModelRaw.Rebin(len(Z_BINNING)-1,hnameNew+'_rebin', array('d', Z_BINNING)))
  hModel = model_vars['hist_z']
  hModel.SetDirectory(0x0)
  isolatedCandJet = hModelRaw.GetBinContent(hModelRaw.FindBin(1.001)) + hModel.GetBinContent(hModel.FindBin(0.99))
  hModel.SetBinContent(hModel.FindBin(0.99), isolatedCandJet)
  hModel.Scale(1./hModel.Integral(),'width')
  # style
  hModel.UseCurrentStyle()
  hModel.SetLineWidth(3)
  hModel.SetLineStyle(model_vars['line'])
  hModel.SetLineColor(model_vars["color"])
  hModel.SetMarkerColor(model_vars['color'])
  hModel.SetDrawOption('E0')
  fModel.Close()
  return hModel


# Output
fOutput = TFile.Open(args.output, 'RECREATE')

for iptjet in range(N_JETBINS):
  pt_jet_l = PT_JET_BINNING[iptjet]
  pt_jet_u = PT_JET_BINNING[iptjet+1]
  name_suffix = f'pt_jet_{pt_jet_l:.0f}_{pt_jet_u:.0f}'
  hname_result = f'unfolded_z_{args.iter}_pt_jet_{pt_jet_l:.2f}_{pt_jet_u:.2f}'
  # Results + sys. unc. - TGraphAsymmErrors (no line, fill rect.)
  # + stats. unc. - TH1 or TGraphErrors  (no marker, no legend)
  hResult = fResult.Get(hname_result)
  hResult.UseCurrentStyle()
  hResult.SetMarkerStyle(root_plot.kRoundHollow)
  hResult.SetMarkerSize(2)
  hResult.SetLineWidth(2)
  hResult.SetLineColor(kBlack)
  hResult.SetMarkerColor(kBlack)
  hResult.SetXTitle('#it{z}_{#parallel}^{ch}')
  hResult.SetYTitle("(1/#it{N}_{jet}) d#it{N}/d#it{z}_{#parallel}^{ch}")
  hResult.GetYaxis().SetTitle('(1/#it{N}_{jet}) d#it{N}/d#it{z}_{#parallel}^{ch}')
  hResult.GetYaxis().SetTitleOffset(0.9)
  hResult.GetYaxis().SetTitleSize(0.07)
  hResult.GetYaxis().SetLabelSize(0.06)
  hResult.GetXaxis().SetRangeUser(0.4,1.0)
  hResult.GetYaxis().SetRangeUser(0.5, 2. * hResult.GetMaximum())
  # syst. unc.
  hSyserr = fSysematics.Get(f'tgsys_pt_jet_{pt_jet_l:.2f}_{pt_jet_u:.2f}')
  hSyserr.SetName(f'FF_Ds_sysunc_pt_jet_{pt_jet_l:.2f}_{pt_jet_u:.2f}')
  hSyserr.UseCurrentStyle()
  hSyserr.GetYaxis().SetTitle('(1/#it{N}_{jet}) d#it{N}/d#it{z}_{#parallel}^{ch}')
  hSyserr.GetYaxis().SetTitleOffset(1.0)
  hSyserr.GetYaxis().SetTitleSize(0.07)
  hSyserr.GetYaxis().SetLabelSize(0.06)
  hSyserr.SetMarkerStyle(root_plot.kRoundHollow)
  hSyserr.SetMarkerSize(2)
  hSyserr.SetLineWidth(0)
  hSyserr.SetFillColor(kGray+1)
  hSyserr.SetFillStyle(1001)
    # update unfolded result
  syserrX = hSyserr.GetX()
  for ibin in range(hSyserr.GetN()):
    ibinResult = hResult.FindBin(syserrX[ibin])
    hSyserr.SetPointY(ibin, hResult.GetBinContent(ibinResult))
  # canvas
  root_objs.append(root_plot.NewRatioPads(c.cd(), f'padz_ptjet_{pt_jet_l:.0f}_{pt_jet_u:.0f}', f'padratio_ptjet_{pt_jet_l:.0f}_{pt_jet_u:.0f}', gap=0.0))
  pMain, pRatio = root_objs[-1]
  c.cd()
  pMain.SetBottomMargin(0.0)
  pRatio.SetTopMargin(0.0)
  pRatio.SetBottomMargin(0.3)
  pMain.cd()
  hSyserr.GetXaxis().SetRangeUser(0.4,1.0)
  hSyserr.GetYaxis().SetRangeUser(0.1, 2. * hResult.GetMaximum())
  hResult.Draw('E0')
  hSyserr.Draw('2 P')
  hResult.Draw('same')
  hSyserr.GetYaxis().SetTitleOffset(0.8)
  # Output
  fOutput.WriteObject(hSyserr, f'FF_Ds_sysunc_{name_suffix}')
  fOutput.WriteObject(hResult, f'FF_Ds_statsunc_{name_suffix}')
  # Main
  hModels = {}
  for model in model_plotting:
    model_vars = model_db[model]
    hModels[model] = draw_model(model, pt_jet_l, pt_jet_u)
    hModels[model].Draw('same')
    fOutput.WriteObject(hModels[model], f'FF_Ds_{model}_{name_suffix}')
    # Legend
  lgdLeft = 0.62
  lgdRight = 0.95
  dsjetTxt = newObj(TPaveText(lgdLeft,0.88,0.95,0.92,"NDC"))
  dsjetTxt.SetFillColor(kWhite)
  root_plot.add_text(dsjetTxt, 'D_{s}^{+}-tagged jets')
  dsjetTxt.Draw('same')
  lgd = newObj(TLegend(lgdLeft,0.78,0.95,0.88))
  lgd.SetTextSize(0.04)
  lgd.SetFillColorAlpha(0,0)
  lgd.AddEntry(hSyserr,'data')
  lgd.AddEntry(hModels['pythia6'],'POWHEG+PYTHIA 6')
  pythiaTxt = newObj(TPaveText(lgdLeft,0.73,0.95,0.77,"NDC"))
  pythiaTxt.SetFillColor(kWhite)
  root_plot.add_text(pythiaTxt, 'PYTHIA 8:')
  pythiaTxt.Draw('same')
  lgd_pythia = newObj(TLegend(lgdLeft,0.63,0.95,0.73))
  lgd_pythia.SetFillColorAlpha(0,0)
  lgd_pythia.SetTextSize(0.04)
  lgd_pythia.AddEntry(hModels['pythia8'], 'Monash')
  lgd_pythia.AddEntry(hModels['pythia8_cr2'], 'CR-BLC Mode 2')
  # Description
  alice = root_plot.InitALICELabel(y1=-0.06, type='prel')
  root_objs.append(alice)
  alice.Draw('same')
  root_objs.append(TPaveText(0.16,0.58,0.54,0.88,"NDC"))
  pave = root_objs[-1]
  pave.SetFillColor(kWhite)
  root_plot.add_text(pave, 'pp #sqrt{#it{s}} = 13 TeV')
  root_plot.add_text(pave, 'charged jets, anti-#it{k}_{T}, #it{R} = 0.4')
  root_plot.add_text(pave, f'{pt_jet_l} < #it{{p}}_{{T}}^{{jet ch.}} < {pt_jet_u} GeV/#it{{c}}, ' +'|#it{#eta}_{jet ch.}| #leq 0.5')
  root_plot.add_text(pave, f'{pt_cand_l[iptjet]} < #it{{p}}_{{T}}^{{D_{{s}}}} < {pt_cand_u[iptjet]} GeV/#it{{c}}, ' +'|#it{y}_{D_{s}^{+}}| #leq 0.8')
    # variation
  if args.extra:
    hExtra = fExtra.Get(hname_result)
    hExtra.SetLineColor(root_plot.kRed)
    hExtra.SetMarkerColor(root_plot.kRed)
    hExtra.SetLineWidth(2)
    hExtra.SetMarkerStyle(root_plot.kBlockHollow)
    lgd.AddEntry(hExtra, args.extra.split('/')[-3]) # [ana-220720test]/pp_data/unfolding_results.root
    hExtra.Draw('same')
    fOutput.WriteObject(hExtra, f'FF_Ds_extra_{name_suffix}')
  if args.dzero: # D0 comp.
    FF_db['D0']['result'].Draw('same 2P')
    lgd.AddEntry(FF_db['D0']['result'],'D^{0}-tagged jets')
    fOutput.WriteObject(FF_db['D0']['result'], f'FF_D0_ALICEpp13TeV_{name_suffix}')
  lgd.Draw('same')
  lgd_pythia.Draw('same')
  pave.Draw("same")
  # Ratio
  hRatioPrimary = None
  ymin, ymax = 0.1, 2.4
  for model in model_plotting:
    model_vars = model_db[model]
    hModel = model_db[model]['hist_z']
    hRatio = newObj(hModel.Clone(f'{model}_hratio_ptjet_{pt_jet_l:.0f}_{pt_jet_u:.0f}'))
    hRatio.Divide(hResult)
    hRatio.SetLineStyle(model_vars['line'])
    hRatio.SetLineColor(model_vars["color"])
    hRatio.SetLineWidth(2)
    hRatio.SetMarkerSize(1.5)
    hRatio.SetMarkerColor(model_vars['color'])
    hRatio.SetYTitle('MC/data')
    hRatio.SetXTitle('#it{z}_{#parallel}^{ch}')
    hRatio.SetDrawOption('E0')
    pRatio.cd()
    ymin = min(ymin, hRatio.GetMinimum())
    ymax = max(ymax, hRatio.GetMaximum()+0.3)
    hRatio.GetYaxis().SetRangeUser(ymin, ymax)
    hRatio.GetXaxis().SetRangeUser(0.4, 1.0)
    if model == model_plotting[0]:
      hRatioPrimary = hRatio
      hRatio.GetYaxis().SetNdivisions(505)
      hRatio.GetYaxis().SetRangeUser(ymin, ymax)
      hRatio.GetXaxis().SetRangeUser(0.4, 1.0)
      hRatio.SetTitleSize(0.15,"xy")
      hRatio.GetXaxis().SetTitleOffset(0.8)
      hRatio.GetYaxis().SetTitleOffset(0.45)
      hRatio.GetXaxis().SetLabelSize(0.13)
      hRatio.GetYaxis().SetLabelSize(0.13)
      hRatio.Draw('E0')
    else:
      hRatio.Draw('same')
    fOutput.WriteObject(hRatio, f'FFratio_Ds_{model}_{name_suffix}')
  if hRatioPrimary:
    #hRatioPrimary.GetYaxis().SetRangeUser(ymin, ymax)
    hRatioPrimary.GetYaxis().SetRangeUser(0.2, 2.13)
    hRatioPrimary.GetXaxis().SetRangeUser(0.4, 1.0)
  hResult.GetXaxis().SetLabelSize(0.0)
  c.cd()
  ROOT.gPad.SaveAs(f'DsJetFF_result_pt_jet_{pt_jet_l:.0f}_{pt_jet_u:.0f}.pdf')
  ROOT.gPad.SaveAs(f'DsJetFF_result_pt_jet_{pt_jet_l:.0f}_{pt_jet_u:.0f}.eps')
  ROOT.gPad.SaveAs(f'DsJetFF_result_pt_jet_{pt_jet_l:.0f}_{pt_jet_u:.0f}.png')
  fOutput.WriteObject(c, f'canvas_pt_jet_{pt_jet_l:.0f}_{pt_jet_u:.0f}')

#c.SaveAs(args.output)
cmd = input('<exit>')

# End
fOutput.Close()
fResult.Close()
fSysematics.Close()
if args.extra:
  fExtra.Close()
