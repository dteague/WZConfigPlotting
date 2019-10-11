#!/usr/bin/env python

import InfoGetter
import Utilities.ConfigHistTools as tools
import os
import ROOT as r
from configHelper import *

r.gROOT.SetBatch(True)
r.gStyle.SetOptTitle(0)

analysis = "ThreeLep"
selection = "Blah"
infile_name = "/afs/cern.ch/work/d/dteague/CMSSW_10_4_0/src/WZConfigPlotting/test_1010.root"
outfile_name = "outfile.root"

channels = ['all']
lumi = 35900
drawOrder = ['ttXY', "ttt", "xg", 'Charge',  'ttz', 'tth', 'nonprompt', 'ttw', '2016']
signalName = "2016"

inFile = r.TFile(infile_name)
outFile = r.TFile(outfile_name, "RECREATE")

info = InfoGetter.InfoGetter(analysis, selection, inFile)
info.setLumi(lumi)

for histName in info.getListOfHists():
    for chan in channels:
        groupHists = getNormedHistos(inFile, info, histName, chan)
        if not groupHists:
            continue

        if signalName in groupHists:
            signal = groupHists[signalName].Clone()
            setStyle(signal, "nofill-red-thick")
            signal.Scale(5)
            signal.SetMarkerSize(2)
            del groupHists[signalName]
        else:
            signal = None
        
        stack = r.THStack("%s_%s" % (histName, chan), "")
        for group in [i for i in drawOrder if i in groupHists]:
            hist = groupHists[group]
            setStyle(hist, info.getStyle(group))
            stack.Add(hist)

        legend = r.TLegend(*info.getStyleInit("Legend"))
        for group in [i for i in drawOrder[::-1] if i in groupHists]:
            legend.AddEntry(groupHists[group], info.getLegendName(group), 'f')
        if signal:
            legend.AddEntry(signal, "%s x 5" % info.getLegendName(signalName), 'lep')

            
        c = r.TCanvas(histName, histName, *info.getStyleInit("Canvas"))
        c.Draw()
        setAttributes(c, info.getStyleInfo("Canvas"))
        
        stack.Draw("hist")
        setAttributes(stack, info.getAxisInfo(histName))
        if histName == "SR":
            stack.GetXaxis().SetRangeUser(1, 9)

        
        signal.Draw("same")
        
        legend.Draw()
        setAttributes(legend, info.getStyleInfo("Legend"))
        
        outFile.cd()
        c.Write()
        




            




