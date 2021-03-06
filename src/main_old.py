#!/bin/python3.7
from src.xmlParser import XmlParser
import math
import numpy as np
import matplotlib.pyplot as plt
import re
from collections import OrderedDict

# Should find ALL textRegions and keep only the biggest ones
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
    verticalBorderLength1 = np.abs(textRegionPoints[0][1] - textRegionPoints[1][1]) # use only y-points, the textbox is rectangular
    verticalBorderLength2 = np.abs(textRegionPoints[0][1] - textRegionPoints[2][1])
    if verticalBorderLength1 > verticalBorderLength2:
        verticalBorderLength = verticalBorderLength1
    else :
        verticalBorderLength = verticalBorderLength2

    horizontalBorderLength1 = np.abs(textRegionPoints[0][0] - textRegionPoints[1][0])
    horizontalBorderLength2 = np.abs(textRegionPoints[0][0] - textRegionPoints[2][0])
    if horizontalBorderLength1 > horizontalBorderLength2:
        horizontalBorderLength = horizontalBorderLength1
    else:
        horizontalBorderLength = horizontalBorderLength2
        # use only x-points, the textbox is rectangular

    return textRegionPoints, verticalBorderLength, horizontalBorderLength

def evaluateTextRegions(p): # remove text regions that are too small
    # Get info about text region boxes
    verticalBorders = []
    horizontalBorders = []

    if len(p.textRegion) == 0: return

    for i in range(len(p.textRegion)):
        textRegionPoints, verticalBorderLength, horizontalBorderLength = getTextRegionInfo(i, p)
        verticalBorders.append(verticalBorderLength)
        horizontalBorders.append(horizontalBorderLength)

    # Remove textbox that is too small on both x and y dimensions
    hMax = max(horizontalBorders)
    vMax = max(verticalBorders)
    margin = 0.8
    for i in range(len(p.textRegion)):
        if (verticalBorders[i] < margin*vMax) & (horizontalBorders[i] < margin*hMax):
            p.removeTR(p.textRegion[i])

def getLinesPoints(textRegionIdx, p):
    # Get coords and baseline point info about text lines
    linesCoords = OrderedDict()
    linesBaseline = OrderedDict()
    for line in p.textRegion[textRegionIdx].findall("manuscript:TextLine", p.ns):
        i = int(re.findall(r'\d+', line.get("custom"))[0])
        linesCoords[i] = line[0].attrib['points'] # line[0] for the coords, line[1] for the baseline; line.get("id")
        linesBaseline[i] = line[1].attrib['points']  # line[0] for the coords, line[1] for the baseline

    return linesCoords, linesBaseline

def getLinesInfo(textRegionIdx, p):
    textRegionPoints, verticalBorderLength, _ = getTextRegionInfo(textRegionIdx, p)
    _, linesBaseline = getLinesPoints(textRegionIdx, p)
    # Compute lengths of baselines, check the histogram, mark the very short ones as problematic
    # Compute baseline distance wrt the left textbox border

    lineYCoords = []     # needed to compute interline distance further on
    lineXCoords = []
    lineLengths = []
    for item in linesBaseline:
        xyPoints = getXYPoints(linesBaseline[item])
        lineYCoords.append(xyPoints[0][1])
        lineXCoords.append([xyPoints[0][0], xyPoints[-1][0]])
        lineLengths.append(math.sqrt((xyPoints[-1][0] - xyPoints[0][0]) ** 2 + (
                    xyPoints[-1][1] - xyPoints[0][1]) ** 2))  # length = sqrt((x2-x1)^2 + (y2-y1)^2)

    lineDistFromLeft = []
    medianX = np.median([xPoint[0] for xPoint in lineXCoords])
    for i in range(len(lineLengths)):
        lineDistFromLeft.append(np.abs(medianX - lineXCoords[i][0])) # textRegionPoints[0][0]

    return lineYCoords, lineLengths, lineDistFromLeft, lineXCoords

def getShortLongLines(textRegionIdx, p, factor = 2):
    _, lineLengths, _, _ = getLinesInfo(textRegionIdx, p)
    shortLines = np.where(np.array(lineLengths) < int(max(lineLengths)/factor)) # lines too short
    longLines = np.where(np.array(lineLengths) > int(max(lineLengths)/factor)) # long lines

    return shortLines, longLines

def farFromBorderLines(textRegionIdx, p, factor = 7):
    _, lineLengths, lineDistFromLeft, _ = getLinesInfo(textRegionIdx, p)
    problemLinesDistance = np.where(np.array(lineDistFromLeft) > int(max(lineLengths)/factor)) # lines too far away from the left textborder

    return problemLinesDistance

def linesToMergeOrLabel(textRegionIdx, p, factorL, factorD):

    shortLines, longLines = getShortLongLines(textRegionIdx, p, factor=factorL)
    farLines = farFromBorderLines(textRegionIdx, p, factor=factorD)
    linesToLabel = list(np.intersect1d(shortLines, farLines))
    linesToMerge = list(np.setdiff1d(shortLines, farLines))

    _, verticalBorderLength, _ = getTextRegionInfo(textRegionIdx, p)
    lineYCoords, _, _, lineXCoords  = getLinesInfo(textRegionIdx, p)

    idxPrevLongLine = []
    idxNextLongLine = []
    distNextLongLine = []
    distPrevLongLine = []
    for lineIdx in linesToMerge:
        if lineIdx < longLines[0][0]:
            idxPrevLongLine.append(longLines[0][0])
            distPrevLongLine.append(verticalBorderLength)
        else:
            idxPrevLongLine.append(longLines[0][np.argmax(longLines[0] > lineIdx) - 1])
            distPrevLongLine.append(np.abs(lineYCoords[lineIdx] - lineYCoords[idxPrevLongLine[-1]]))

        if lineIdx > longLines[0][-1]:
            idxNextLongLine.append(longLines[0][-1])
            distNextLongLine.append(verticalBorderLength)
        else:
            idxNextLongLine.append(longLines[0][np.argmax(longLines[0] > lineIdx)])
            distNextLongLine.append(np.abs(lineYCoords[lineIdx] - lineYCoords[idxNextLongLine[-1]]))

    idxMerge = [idxPrevLongLine[i] if distPrevLongLine[i] < distNextLongLine[i] else idxNextLongLine[i] for i in range(len(distNextLongLine))]

    if len(idxMerge) > 0:
        for i in range(len(idxMerge)):
            if lineXCoords[linesToMerge[i]][1] > lineXCoords[idxMerge[i]][0]:
                linesToMerge[i] = None
                idxMerge[i] = None
                linesToLabel.append(linesToMerge[i])

    linesToMerge = [line for line in linesToMerge if line is not None]
    idxMerge = [line for line in idxMerge if line is not None]

    return linesToMerge, idxMerge, linesToLabel

def mergeCommentLines(textRegionIdx, p, annotation): # merges small lines to long lines and removes the smaller line
    linesToMerge, idxMerge, linesToLabel = linesToMergeOrLabel(textRegionIdx, p, 2, 7)
    if len(idxMerge) > len(set(idxMerge)):
        print('Attention: long line matches multiple merges')

    linesCoords, linesBaseline = getLinesPoints(textRegionIdx, p)

    linesToRemove = []
    for l in range(len(idxMerge)):
        # merge coordinates
        str1 = " ".join(linesCoords[linesToMerge[l]].split(' ')[0:round(len(linesCoords[linesToMerge[l]].split(' '))/2)])
        str2 = " ".join(linesCoords[linesToMerge[l]].split(' ')[round(len(linesCoords[linesToMerge[l]].split(' '))/2):])
        linesCoords[idxMerge[l]] = str1 + " " +linesCoords[idxMerge[l]] + " " + str2

        # merge baselines
        linesBaseline[idxMerge[l]] = linesBaseline[linesToMerge[l]] + " " +linesBaseline[idxMerge[l]]

        # add short merged lines to a list to be removed
        linesToRemove.append(linesToMerge[l])

    for line in p.textRegion[textRegionIdx].findall("manuscript:TextLine", p.ns):
        i = int(re.findall(r'\d+', line.get("custom"))[0])
        line[0].attrib['points'] = linesCoords[i]
        line[1].attrib['points'] = linesBaseline[i]
        if i in linesToRemove:
            p.removeTL(textRegionIdx, line)

    for line in p.textRegion[textRegionIdx].findall("manuscript:TextLine", p.ns):
        i = int(re.findall(r'\d+', line.get("custom"))[0])
        if i in linesToLabel:
            line.set("custom", line.get("custom") + 'structure {type:' + annotation + ';}')

def extendBaselines(textRegionIdx, p):
    _, _, _, lineXCoords = getLinesInfo(textRegionIdx, p)
    linesCoords, linesBaseline = getLinesPoints(textRegionIdx, p)
    _, longLines = getShortLongLines(textRegionIdx, p, factor = 2)

    medianX = np.percentile([xPoint[0] for xPoint in lineXCoords], 50)
    for l in longLines[0]:
        k = list(linesBaseline.keys())[l]
        if medianX < int(linesBaseline[k].split(' ')[0].split(',')[0]):
            linesBaseline[k] = str(int(medianX)) + ',' + linesBaseline[k].split(' ')[0].split(',')[1] + ' ' + linesBaseline[k]
            linesCoords[k] =  str(int(medianX)) + ',' + linesCoords[k].split(' ')[0].split(',')[1] + ' ' + linesCoords[k] + ' ' + str(int(medianX)) + ',' + linesCoords[k].split(' ')[-1].split(',')[1]

    for line in p.textRegion[textRegionIdx].findall("manuscript:TextLine", p.ns):
        i = int(re.findall(r'\d+', line.get("custom"))[0])
        line[1].attrib['points'] = linesBaseline[i]
        line[0].attrib['points'] = linesCoords[i]

def computeInterDistance(textRegionIdx, p): # not currently used
    # typical interline distance based on long lines only
    _, longLines = getShortLongLines(textRegionIdx, p, factor = 2)
    lineYCoords, _, _, _  = getLinesInfo(textRegionIdx, p)
    interDistance = round(np.mean(np.diff([lineYCoords[i] for i in longLines[0]])))
    return interDistance


# p = XmlParser('./data/xml-sample/old_24_BERGAMO_08.xml')
# root = p.root
# p.findTextRegion()
# evaluateTextRegions(p)
# textRegionIdx = 0
# for textRegionIdx in range(len(p.textRegion)):
#     mergeCommentLines(textRegionIdx, p)
#     extendBaselines(textRegionIdx, p)

# _, lineLengths, lineDistFromLeft, _ = getLinesInfo(textRegionIdx, p)
# plt.figure(0)
# plt.hist(lineLengths, bins=100)
# plt.title("Histogram of baseline lengths")
# plt.show()
#
#
# plt.figure(1)
# plt.hist(lineDistFromLeft, bins=100)
# plt.title("Histogram of baseline distances from left textbox border")
# plt.show()