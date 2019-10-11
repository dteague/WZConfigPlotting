#!/usr/bin/env python
import os
import ROOT as r

from configHelper import *
import InfoGetter
import StyleHelper as style
import configHelper

args = configHelper.getComLineArgs()
r.gROOT.SetBatch(True)
r.gStyle.SetOptTitle(0)


drawOrder = ['ttXY', "ttt", "xg", 'Charge',  'ttz', 'tth', 'nonprompt', 'ttw', '2016']


if args.signal and args.signal not in drawOrder:
    print "signal not in list of groups!"
    print drawOrder
    exit(1)

signalName = args.signal
channels = args.channels.split(',')

inFile = r.TFile(args.infile)
outFile = r.TFile(args.outfile, "RECREATE")

info = InfoGetter.InfoGetter(args.analysis, args.selection, inFile)
info.setLumi(args.lumi*1000)

for histName in info.getListOfHists():
    for chan in channels:
        groupHists = configHelper.getNormedHistos(inFile, info, histName, chan)
        if not groupHists:
            continue

        # signal scaled by 5 and done by hand. my configure this in style.py file
        if signalName in groupHists:
            signal = groupHists[signalName].Clone()
            style.setStyle(signal, "nofill-red-thick")
            signal.Scale(5)
            signal.SetMarkerSize(2)
            del groupHists[signalName]
        else:
            signal = None
        
        stack = r.THStack("%s_%s" % (histName, chan), "")
        for group in [i for i in drawOrder if i in groupHists]:
            hist = groupHists[group]
            style.setStyle(hist, info.getStyle(group))
            stack.Add(hist)
        if args.stack_signal:
            stack.Add(signal)
            signal = None

            
        legend = r.TLegend(*info.getStyleInit("Legend"))
        for group in [i for i in drawOrder[::-1] if i in groupHists]:
            legend.AddEntry(groupHists[group], info.getLegendName(group), 'f')
        if signal:
            legend.AddEntry(signal, "%s x 5" % info.getLegendName(signalName), 'lep')

            
        c = r.TCanvas(histName, histName, *info.getStyleInit("Canvas"))
        c.Draw()
        style.setAttributes(c, info.getStyleInfo("Canvas"))
        if args.logy: c.SetLogy()
        
        stack.Draw("hist")
        style.setAttributes(stack, info.getAxisInfo(histName))
        if histName == "SR":
            stack.GetXaxis().SetRangeUser(1, 9)

        
        if signal: signal.Draw("same")
            
        legend.Draw()
        style.setAttributes(legend, info.getStyleInfo("Legend"))
        
        outFile.cd()
        c.Write()
        




            




