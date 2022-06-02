#!/usr/bin/env python3

# Processing feeddown output
import argparse
from ROOT import gStyle
from ROOT import TFile, TH1D, TCanvas, TLegend, TPaveText
from ROOT import kRed, kBlack, kBlue, kWhite

parser = argparse.ArgumentParser(description='Feeddown outputs')
parser.add_argument('-f','--file', default='/mnt/d/DsJet/fastsimu/trees_powheg+pythia6+evtgen_beauty.root', help='HF_TreeCreator Generated outputs')
parser.add_argument('--cand', default='Ds', help='HF candidates (tree name suffix)')
parser.add_argument('-o', '--output', help='Output file prefix', default='test')
args = parser.parse_args()

gStyle.SetOptStat(False)
gStyle.SetLegendBorderSize(0)
gStyle.SetLegendFillColor(kWhite)
gStyle.SetLegendFont(42)
gStyle.SetLineWidth(2)

file_input = args.file
file_out = args.output + f'_fastsimu_{args.cand}.root'
fInput = TFile.Open(file_input)
fOutput = TFile.Open(file_out,'RECREATE')
HFcand = args.cand

treeSimu = fInput.Get(f'tree_{HFcand}')

jet_pt_l = [5,7,15]
jet_pt_u = [7,15,35]
pt_cand_l = 3
jet_selection = 'abs(eta_jet)<0.5'

colorset = [kBlack, kRed, kBlue]
hz = []
root_obj = []

c = TCanvas('c1','FastSimu-z')
c.Draw()
lgd = TLegend(0.15,0.7,0.45,0.85)
for i, jetpt in enumerate(jet_pt_l):
  htemp = TH1D('htemp',f'Fragmentation function of {HFcand} in jets', 22, 0, 1.1)
  treeSimu.Draw("z>>htemp",f'pt_cand>{pt_cand_l}&&pt_jet>{jet_pt_l[i]}&&pt_jet<{jet_pt_u[i]}&&{jet_selection}')
  hz.append(htemp.Clone(f'hz_ptjet_{jet_pt_l[i]}_{jet_pt_u[i]}'))
  htmp = hz[-1]
  htmp.SetXTitle("z_{#parallel}^{ch}")
  htmp.SetYTitle("1/#it{N} d#it{N}/d#it{z} (self normalised)")
  htmp.Sumw2()
  htmp.Scale(1./htmp.Integral(),'width')
  htmp.SetLineColor(colorset[i])
  htmp.SetLineWidth(2)
  htmp.SetMarkerColor(colorset[i])
  lgd.AddEntry(hz[-1],f"{jet_pt_l[i]} < #it{{p}}_{{T,jet}} < {jet_pt_u[i]} (GeV/#it{{c}})")
  #htmp.Draw("same")
  fOutput.cd()
  htmp.Write()

hz[0].Draw()
hz[0].GetYaxis().SetRangeUser(0,5)
hz[1].Draw("same")
hz[2].Draw("same")

def add_text(pave : TPaveText, s : str, color=None, size=0.04, align=11):
  text = pave.AddText(s)
  text.SetTextAlign(align)
  text.SetTextSize(size)
  text.SetTextFont(42)
  if(color):
    text.SetTextColor(color)
  return text

pave = TPaveText(0.6,0.7,0.88,0.88,"NDC")
pave.SetFillColor(kWhite)
add_text(pave, "#it{p}_{T,cand} > 3 GeV/#it{c}")
add_text(pave, "|#eta_{jet}| < 0.5")
pave.Draw("same")

lgd.Draw("same")
lgd.Write()
c.Write()
c.SaveAs(f"{args.output}_hz_{HFcand}.pdf")

fInput.Close()
fOutput.Close()