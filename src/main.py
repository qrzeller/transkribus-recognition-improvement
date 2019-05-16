#!/bin/python3.7
from src.xmlParser import XmlParser
import math
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict

# Should find ALL textRegions and keep only the biggest one as main text region
# remove all lines outside of the main text region
# calibrate interline distance as the distance between longest lines
# for all lines inside the text box, compute the line length, line distance to the left text box border

# Problematic lines: the very short lines | the lines away from the textbox border | lines that are too close to long lines
# lines that are short AND close to the textbox border should be merged to the closest one on the Ox axis
# other problematic lines should be removed

def getXYPoints(stringList):
    result =[[int(point) for point in pair.split(',')] for pair in stringList.split(' ')]
    return result

def getTextRegionInfo(textRegion, p):
    textRegionCoords = textRegion.findall("manuscript:Coords", p.ns)[0].attrib['points']
    textRegionPoints = getXYPoints(textRegionCoords)
    verticalBorderLength = np.abs(textRegionPoints[0][1] - textRegionPoints[-1][1]) # use only y-points, the textbox is rectangular
    horizontalBorderLength = np.abs(textRegionPoints[0][0] - textRegionPoints[1][0]) # use only x-points, the textbox is rectangular
    return textRegionPoints, verticalBorderLength, horizontalBorderLength

def extendBaselines(textRegion, p):
    textRegionPoints = getTextRegionInfo(textRegion, p)
    for line in textRegion.findall("manuscript:TextLine", p.ns):
        # line[0].attrib['points'] = str(textRegionPoints[0][0])+ ',' + line[0].attrib['points'].split(' ')[0].split(',')[1] + ' ' + line[0].attrib['points'] # line[0] for the coords, line[1] for the baseline
        line[1].attrib['points'] = str(textRegionPoints[0][0])+ ',' + line[1].attrib['points'].split(' ')[0].split(',')[1] + ' ' + line[1].attrib['points']

def evaluateTextRegions(p): # remove text regions that are too small
    # Get info about text region boxes
    verticalBorders = []
    horizontalBorders = []
    for i in range(len(p.textRegion)):
        textRegionPoints, verticalBorderLength, horizontalBorderLength = getTextRegionInfo(p.textRegion[i], p)
        verticalBorders.append(verticalBorderLength)
        horizontalBorders.append(horizontalBorderLength)

    # Remove textbox that is too small on both x and y dimensions
    hMax = max(horizontalBorders)
    vMax = max(verticalBorders)
    margin = 0.9
    for i in range(len(p.textRegion)):
        if (verticalBorders[i] < margin*vMax) & (horizontalBorders < margin*hMax):
            p.removeTR(p.textRegion[i])

def getLinesPoints(textRegion, p):
    # Get coords and baseline point info about text lines
    linesCoords = OrderedDict()
    linesBaseline = OrderedDict()
    i = 0
    for line in textRegion.findall("manuscript:TextLine", p.ns):
        linesCoords[i] = line[0].attrib['points'] # line[0] for the coords, line[1] for the baseline; line.get("id")
        linesBaseline[i] = line[1].attrib['points']  # line[0] for the coords, line[1] for the baseline
        i += 1
    return linesCoords, linesBaseline

def getLinesInfo(textRegion, p):
    textRegionPoints, verticalBorderLength, _ = getTextRegionInfo(textRegion, p)
    _, linesBaseline = getLinesPoints(textRegion, p)
    # Compute lengths of baselines, check the histogram, mark the very short ones as problematic
    # Compute baseline distance wrt the left textbox border
    lineLengths = []
    lineDistFromLeft = []
    lineYCoords = [] # needed to compute interline distance further on
    for item in linesBaseline:
        xyPoints = getXYPoints(linesBaseline[item])
        lineYCoords.append(xyPoints[0][1])
        lineLengths.append(math.sqrt((xyPoints[-1][0] - xyPoints[0][0])**2 + (xyPoints[-1][1] - xyPoints[0][1])**2)) # length = sqrt((x2-x1)^2 + (y2-y1)^2)
        lineDistFromLeft.append(np.abs((textRegionPoints[0][1] - textRegionPoints[1][1])*xyPoints[0][0] +
                                textRegionPoints[0][0]*textRegionPoints[1][1] -
                                textRegionPoints[0][1]*textRegionPoints[1][0]) / verticalBorderLength) # wiki formula

    return lineYCoords, lineLengths, lineDistFromLeft

def getShortLongLines(textRegion, p, factor = 2):
    _, lineLengths, _ = getLinesInfo(textRegion, p)
    shortLines = np.where(np.array(lineLengths) < int(max(lineLengths)/factor)) # lines too short
    longLines = np.where(np.array(lineLengths) > int(max(lineLengths) / factor)) # long lines
    return shortLines, longLines

def farFromBorderLines(textRegion, p, factor = 4):
    _, _, lineDistFromLeft = getLinesInfo(textRegion, p)
    problemLinesDistance = np.where(np.array(lineDistFromLeft) > int(max(lineDistFromLeft)/factor)) # lines too far away from the left textborder
    return problemLinesDistance

def computeInterDistance(textRegion, p):
    # typical interline distance based on long lines only
    _, longLines = getShortLongLines(textRegion, p, factor = 2)
    lineYCoords, _, _ = getLinesInfo(textRegion, p)
    interDistance = round(np.mean(np.diff([lineYCoords[i] for i in longLines[0]])))
    return interDistance

def linesToMergeOrLabel(textRegion, p):
    shortLines, longLines = getShortLongLines(textRegion, p, factor = 2)
    farLines = farFromBorderLines(textRegion, p, factor = 4)

    linesToTagComment = np.intersect1d(shortLines, farLines)
    linesToMerge = np.setdiff1d(shortLines, farLines)
    return linesToMerge, linesToTagComment

def matchLongLinesForMerge(textRegion, p):
    linesToMerge, _ = linesToMergeOrLabel(textRegion, p)
    _, longLines = getShortLongLines(textRegion, p, factor=2)
    verticalBorderLength = getTextRegionInfo(textRegion, p)
    lineYCoords, _, _ = getLinesInfo(textRegion, p)

    idxPrevLongLine = []
    idxNextLongLine = []
    distNextLongLine = []
    distPrevLongLine = []
    for lineIdx in linesToMerge:
        if lineIdx < longLines[0][0]:
            idxPrevLongLine.append(None)
            distPrevLongLine.append(verticalBorderLength)
        else:
            idxPrevLongLine.append(longLines[0][np.argmax(longLines[0] > lineIdx) - 1])
            distPrevLongLine.append(np.abs(lineYCoords[lineIdx] - lineYCoords[idxPrevLongLine[-1]]))

        if lineIdx > longLines[0][-1]:
            idxNextLongLine.append(None)
            distNextLongLine.append(verticalBorderLength)
            # linesToRemove.append(line)
        else:
            idxNextLongLine.append(longLines[0][np.argmax(longLines[0] > lineIdx)])
            distNextLongLine.append(np.abs(lineYCoords[lineIdx] - lineYCoords[idxNextLongLine[-1]]))

    idxMerge = [idxPrevLongLine[i] if distPrevLongLine[i] < distNextLongLine[i] else idxNextLongLine[i] for i in
                range(len(distNextLongLine))]

    return idxMerge

def mergeLinesBaselines(textRegion, p): # merges small lines to long lines and removes the smaller line
    idxMerge = matchLongLinesForMerge(textRegion, p)
    if len(idxMerge) > len(set(idxMerge)):
        print('Attention: long line matches multiple merges')

    _, linesBaseline = getLinesPoints(textRegion, p)
    linesToMerge, _ = linesToMergeOrLabel(textRegion, p)
    # merge lines
    linesToRemove = []
    for l in range(len(idxMerge)):
        linesBaseline[idxMerge[l]] = linesBaseline[linesToMerge[l]] + linesBaseline[idxMerge[l]]
        linesToRemove.append(linesToMerge[l])

    i = 0
    for line in textRegion.findall("manuscript:TextLine", p.ns):
        # line[0].attrib['points'] = str(textRegionPoints[0][0])+ ',' + line[0].attrib['points'].split(' ')[0].split(',')[1] + ' ' + line[0].attrib['points'] # line[0] for the coords, line[1] for the baseline
        line[1].attrib['points'] = linesBaseline[i]
        if i in linesToRemove:
            p.textRegion.removeTL(textRegion, line)
        i += 1


# def linesToMerge(textRegion, p):

p = XmlParser('./data/xml-sample/new_493_PARIS_01.xml')

root = p.root
p.findTextRegion()
# p.processTextLine()

for i in range(len(p.textRegion)):
    textRegion = p.textRegion[i]
    _, linesToLabel = linesToMergeOrLabel(textRegion, p)# needs a labeling function
    mergeLinesBaselines(textRegion, p)






# plt.figure(0)
# plt.hist(lineLengths, bins=100)
# plt.title("Histogram of baseline lengths")
# plt.show()
#
# plt.figure(1)
# plt.hist(lineDistFromLeft, bins=100)
# plt.title("Histogram of baseline distances from left textbox border")
# plt.show()


# pp = p.prettyPrintTo("./test2.xml")



# hist, bin_edges = np.histogram(lineLengths)

