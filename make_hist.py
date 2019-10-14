#!/usr/bin/env python
import os
import ROOT as r

import InfoGetter
import StyleHelper as style
import configHelper as configHelper

args = configHelper.getComLineArgs()
r.gROOT.SetBatch(True)
r.gStyle.SetOptTitle(0)
        

drawObj = ['ttXY', "rare", "xg", 'Charge',  'ttz', 'tth', 'nonprompt', 'ttw', '2016']


if args.signal and args.signal not in drawObj:
    print "signal not in list of groups!"
    print drawObj
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
        for hist in groupHists.values(): configHelper.addOverflow(hist)
            
        if not groupHists:
            continue

        if signalName in groupHists:
            signal = groupHists[signalName].Clone()
            style.setStyle(signal, info.getStyleInit("Signal"))
            style.setAttributes(signal, info.getStyleInfo("Signal"))
            del groupHists[signalName]
        else:
            signal = None
         
        drawOrder = configHelper.getDrawOrder(groupHists, drawObj)
            
        statError = configHelper.getHistTotal([i for key, i in groupHists.iteritems() if key in drawOrder])
        style.setStyle(statError, info.getStyleInit("ErrorBars"))
        
        
        stack = r.THStack("%s_%s" % (histName, chan), "")
        for group in [i for i in drawOrder if i in groupHists]:
            hist = groupHists[group]
            style.setStyle(hist, info.getStyle(group))
            stack.Add(hist)
        if args.stack_signal:
            stack.Add(signal)
            signal = None

        # setup legend stuff
        legend = r.TLegend(*info.getStyleInit("Legend"))
        for group in [i for i in drawOrder[::-1] if i in groupHists]:
            legend.AddEntry(groupHists[group], info.getLegendName(group), 'f')
        legend.AddEntry(statError, "statError", "f")
        if signal:
            legend.AddEntry(signal, "%s x 5" % info.getLegendName(signalName), 'lep') # need to change
        style.setAttributes(legend, info.getStyleInfo("Legend"))

        # canvas
        c = r.TCanvas(histName, histName, *info.getStyleInit("Canvas"))
        c.Draw()
        style.setAttributes(c, info.getStyleInfo("Canvas"))
        if args.logy: c.SetLogy()

        # draw everything
        stack.Draw("hist")
        style.setAttributes(stack, info.getAxisInfo(histName))
        statError.Draw("E2 same")
        if signal: signal.Draw("same")
        legend.Draw()
        
        
        outFile.cd()
        c.Write()
        




            




