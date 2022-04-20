# ROOT painter for drawing objects in PDF file

# Basic Usage:
# p = Painter()
# p.PrintCover()
# p.DrawHist(h1)
# p.PrintBackCover()

from ROOT import TCanvas, TPaveText
from ROOT import gPad, gStyle

def NewCanvas(name="c1_painter", title="New Canvas", winX=1600, winY=1000, **kwargs):
  return TCanvas(name, title, winX,winY)

# Params: ROOT.TCanvas, PDF output filename
# - for new canvas: name, title, winX, winY
class Painter:
  def __init__(self, canvas = None, printer = "out.pdf", **kwargs):
    self.canvas = canvas if canvas is not None else NewCanvas(**kwargs)
       # Output PDF in 1 file
    self.printer = printer if printer.endswith(".pdf") else printer +".pdf"
    # Configuration
    self.subPadNX = kwargs['nx'] if kwargs.get('nx') else 1
    self.subPadNY = kwargs['ny'] if kwargs.get('ny') else 1
    # Status
    self.padIndex = 0
    self.pageName = "Start"
    self.hasCover = False
    self.hasBackCover = False
    # Dump
    self.root_obj = []         # Temp storage to avoid GC
  def __del__(self):
    if(self.hasCover and not self.hasBackCover):
      self.PrintBackCover('')
  def ResetCanvas(self):
    self.canvas.Clear()
    self.canvas.Divide(self.subPadNX, self.subPadNY)
  def SetLayout(self, nx, ny):
    self.subPadNX = nx
    self.subPadNY = ny
    self.ResetCanvas()
  def GetLayout(self):
    return (self.subPadNX, self.subPadNY)
  def PrintCover(self, title = '', isBack = False):
    self.canvas.Clear()
    pTxt = TPaveText(0.25,0.4,0.75,0.6, "brNDC")
    if(title == ''):
      if(isBack):
        pTxt.AddText('Thanks for your attention!')
      else:
        pTxt.AddText(self.canvas.GetTitle())
    else:
      pTxt.AddText(title)
    self.canvas.cd()
    self.canvas.Draw()
    pTxt.Draw()
    if(isBack):
      self.canvas.Print(self.printer + ')', 'Title:End')
    else:
      self.canvas.Print(self.printer + '(', 'Title:Cover')
    pTxt.Delete()
    self.ResetCanvas()
  def PrintBackCover(self, title=''):
    self.PrintCover(title, isBack=True)
  def NextPage(self, title=""):
    self.padIndex = 0
    if(title == ""):
      title = self.pageName
    self.canvas.Print(self.printer, f"Title:{title}")
    self.ResetCanvas()
  def NextPad(self, title=""):
    if(self.padIndex == self.subPadNX * self.subPadNY):
      self.NextPage()
    self.padIndex = self.padIndex + 1
    self.canvas.cd(self.padIndex)
    gPad.SetMargin(0.15, 0.02, 0.15, 0.1)
  # Drawing - Histograms
  def DrawHist(self, htmp, title="", option="", optStat=True, samePad=False):
    gStyle.SetOptStat(optStat)
    if(title == ""):
      title = htmp.GetTitle()
    if(not samePad):
      self.NextPad(title)
    print("[+] DEBUG - Pad " + str(self.padIndex) + ' : ' + htmp.GetName()) 
    htmp.Draw(option)
