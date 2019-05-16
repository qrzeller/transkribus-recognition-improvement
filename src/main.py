#!/bin/python3.7
from src.xmlParser import XmlParser
import math
import numpy as np
import matplotlib.pyplot as plt
import re
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

def getTextRegionInfo(textRegionIdx, p):
    textRegionCoords = p.textRegion[textRegionIdx].findall("manuscript:Coords", p.ns)[0].attrib['points']
    textRegionPoints = getXYPoints(textRegionCoords)
    # print('textRegionPoints', textRegionPoints)
    verticalBorderLength = np.abs(textRegionPoints[0][1] - textRegionPoints[1][1]) # use only y-points, the textbox is rectangular
    horizontalBorderLength = np.abs(textRegionPoints[0][0] - textRegionPoints[1][0]) # use only x-points, the textbox is rectangular
    return textRegionPoints, verticalBorderLength, horizontalBorderLength

def evaluateTextRegions(p): # remove text regions that are too small
    # Get info about text region boxes
    verticalBorders = []
    horizontalBorders = []
    for i in range(len(p.textRegion)):
        textRegionPoints, verticalBorderLength, horizontalBorderLength = getTextRegionInfo(i, p)
        verticalBorders.append(verticalBorderLength)
        horizontalBorders.append(horizontalBorderLength)

    # Remove textbox that is too small on both x and y dimensions
    hMax = max(horizontalBorders)
    vMax = max(verticalBorders)
    margin = 0.9
    for i in range(len(p.textRegion)):
        if (verticalBorders[i] < margin*vMax) & (horizontalBorders[i] < margin*hMax):
            p.removeTR(p.textRegion[i])

def getLinesPoints(textRegionIdx, p):
    # Get coords and baseline point info about text lines
    linesCoords = OrderedDict()
    linesBaseline = OrderedDict()
    i = 0
    for line in p.textRegion[textRegionIdx].findall("manuscript:TextLine", p.ns):
        linesCoords[i] = line[0].attrib['points'] # line[0] for the coords, line[1] for the baseline; line.get("id")
        linesBaseline[i] = line[1].attrib['points']  # line[0] for the coords, line[1] for the baseline
        i += 1
    return linesCoords, linesBaseline

def getLinesInfo(textRegionIdx, p):
    textRegionPoints, verticalBorderLength, _ = getTextRegionInfo(textRegionIdx, p)
    _, linesBaseline = getLinesPoints(textRegionIdx, p)
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
    # print('verticalBorderLength', verticalBorderLength)
    return lineYCoords, lineLengths, lineDistFromLeft

def getShortLongLines(textRegionIdx, p, factor = 2):
    _, lineLengths, _ = getLinesInfo(textRegionIdx, p)
    shortLines = np.where(np.array(lineLengths) < int(max(lineLengths)/factor)) # lines too short
    longLines = np.where(np.array(lineLengths) > int(max(lineLengths) / factor)) # long lines
    return shortLines, longLines

def farFromBorderLines(textRegionIdx, p, factor = 4):
    _, _, lineDistFromLeft = getLinesInfo(textRegionIdx, p)
    # print('lineDistFromLeft', lineDistFromLeft)
    problemLinesDistance = np.where(np.array(lineDistFromLeft) > int(max(lineDistFromLeft)/factor)) # lines too far away from the left textborder
    return problemLinesDistance

def linesToMergeOrLabel(textRegionIdx, p):
    shortLines, longLines = getShortLongLines(textRegionIdx, p, factor = 2)
    farLines = farFromBorderLines(textRegionIdx, p, factor = 4)
    linesToTagComment = np.intersect1d(shortLines, farLines)
    linesToMerge = np.setdiff1d(shortLines, farLines)
    # print('shortLines', shortLines)
    # print('farLines', farLines)
    # print('linesToTagComment', linesToTagComment)
    # print('linesToMerge', linesToMerge)
    return linesToMerge, linesToTagComment

def matchLongLinesForMerge(textRegionIdx, p):
    linesToMerge, _ = linesToMergeOrLabel(textRegionIdx, p)
    _, longLines = getShortLongLines(textRegionIdx, p, factor=2)
    _, verticalBorderLength, _ = getTextRegionInfo(textRegionIdx, p)
    lineYCoords, _, _ = getLinesInfo(textRegionIdx, p)

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
        else:
            idxNextLongLine.append(longLines[0][np.argmax(longLines[0] > lineIdx)])
            distNextLongLine.append(np.abs(lineYCoords[lineIdx] - lineYCoords[idxNextLongLine[-1]]))

    print('linesToMerge', linesToMerge)
    print('longLines', longLines)
    print('idxPrevLongLine', idxPrevLongLine)
    print('idxNextLongLine', idxNextLongLine)
    print('distPrevLongLine', distPrevLongLine)
    print('distNextLongLine', distNextLongLine)
    idxMerge = [idxPrevLongLine[i] if distPrevLongLine[i] < distNextLongLine[i] else idxNextLongLine[i] for i in range(len(distNextLongLine))]

    return idxMerge

def mergeLinesBaselines(textRegionIdx, p): # merges small lines to long lines and removes the smaller line
    idxMerge = matchLongLinesForMerge(textRegionIdx, p)
    if len(idxMerge) > len(set(idxMerge)):
        print('Attention: long line matches multiple merges')

    linesCoords, linesBaseline = getLinesPoints(textRegionIdx, p)
    linesToMerge, _ = linesToMergeOrLabel(textRegionIdx, p)

    linesToRemove = []
    for l in range(len(idxMerge)):
        # TODO merge coordinates
        # linesCoords[idxMerge[l]] =

        # merge baselines
        linesBaseline[idxMerge[l]] = linesBaseline[linesToMerge[l]] + linesBaseline[idxMerge[l]]
        # add short merged lines to a list to be removed
        linesToRemove.append(linesToMerge[l])
    # print('linesToMerge', linesToMerge)

    # i = 0
    for line in p.textRegion[textRegionIdx].findall("manuscript:TextLine", p.ns):
        i = int(re.findall(r'\d+', line.get("custom"))[0])
        line[0].attrib['points'] = linesCoords[i]
        line[1].attrib['points'] = linesBaseline[i]
        if i in linesToRemove:
            p.removeTL(textRegionIdx, line)
        # i += 1

def addCommentLabels(textRegionIdx, p): # merges small lines to long lines and removes the smaller line
    _, linesToLabel = linesToMergeOrLabel(textRegionIdx, p)
    # i = 0
    for line in p.textRegion[textRegionIdx].findall("manuscript:TextLine", p.ns):
        i = int(re.findall(r'\d+', line.get("custom"))[0])
        if i in linesToLabel:
            line.set("custom", line.get("custom") + 'structure {type:footnote;}')
        # i += 1

def extendBaselines(textRegionIdx, p): # not currently used
    textRegionPoints = getTextRegionInfo(textRegionIdx, p)
    for line in p.textRegion[textRegionIdx].findall("manuscript:TextLine", p.ns):
        # line[0].attrib['points'] = str(textRegionPoints[0][0])+ ',' + line[0].attrib['points'].split(' ')[0].split(',')[1] + ' ' + line[0].attrib['points'] # line[0] for the coords, line[1] for the baseline
        line[1].attrib['points'] = str(textRegionPoints[0][0])+ ',' + line[1].attrib['points'].split(' ')[0].split(',')[1] + ' ' + line[1].attrib['points']

def computeInterDistance(textRegionIdx, p): # not currently used
    # typical interline distance based on long lines only
    _, longLines = getShortLongLines(textRegionIdx, p, factor = 2)
    lineYCoords, _, _ = getLinesInfo(textRegionIdx, p)
    interDistance = round(np.mean(np.diff([lineYCoords[i] for i in longLines[0]])))
    return interDistance

p = XmlParser('./data/xml-sample/old_24_BERGAMO_08.xml')
root = p.root
p.findTextRegion()

evaluateTextRegions(p)
for textRegionIdx in range(len(p.textRegion)):
    addCommentLabels(textRegionIdx, p)
    mergeLinesBaselines(textRegionIdx, p)

pp = p.prettyPrintTo("./test2.xml")


# plt.figure(0)
# plt.hist(lineLengths, bins=100)
# plt.title("Histogram of baseline lengths")
# plt.show()
#
# plt.figure(1)
# plt.hist(lineDistFromLeft, bins=100)
# plt.title("Histogram of baseline distances from left textbox border")
# plt.show()




