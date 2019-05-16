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

p = XmlParser('../data/xml-sample/new_493_PARIS_01.xml')

root = p.root
p.findTextRegion()
# p.processTextLine()

def getXYPoints(stringList):
    result =[[int(point) for point in pair.split(',')] for pair in stringList.split(' ')]
    return result

# Get info about text region boxes
verticalBorderLength = []
horizontalBorderLength = []
for i in range(len(p.textRegion)):
    textRegionCoords = p.textRegion[i].findall("manuscript:Coords", p.ns)[0].attrib['points']
    textRegionPoints = getXYPoints(textRegionCoords)
    verticalBorderLength.append(np.abs(textRegionPoints[0][1] - textRegionPoints[-1][1])) # use only y-points, the textbox is rectangular
    horizontalBorderLength.append(np.abs(textRegionPoints[0][0] - textRegionPoints[1][0])) # use only x-points, the textbox is rectangular

# Remove textbox that is too small on both x and y dimensions
hMax = max(horizontalBorderLength)
vMax = max(verticalBorderLength)
margin = 0.9
for i in range(len(p.textRegion)):
    if (verticalBorderLength[i] < margin*vMax) & (horizontalBorderLength[i] < margin*hMax):
        print(i)
        p.removeTR(p.textRegion[i])

pp = p.prettyPrintTo("./test2.xml")






"""

# Get info about text lines
linesCoords = OrderedDict()
linesBaseline = OrderedDict()
i = 0
for line in p.textRegion.findall("manuscript:TextLine", p.ns):
    linesCoords[i] = line[0].attrib['points'] # line[0] for the coords, line[1] for the baseline; line.get("id")
    linesBaseline[i] = line[1].attrib['points']  # line[0] for the coords, line[1] for the baseline
    i += 1

# Compute lengths of baselines, check the histogram, mark the very short ones as problematic
# Compute baseline distance wrt the left textbox border
lineLengths = []
lineDistFromLeft = []
yCoordsAllPoints = []
for item in linesBaseline:
    xyPoints = getXYPoints(linesBaseline[item])
    yCoordsAllPoints.append(xyPoints[0][1])
    lineLengths.append(math.sqrt((xyPoints[-1][0] - xyPoints[0][0])**2 + (xyPoints[-1][1] - xyPoints[0][1])**2)) # length = sqrt((x2-x1)^2 + (y2-y1)^2)
    lineDistFromLeft.append(np.abs((textRegionPoints[0][1] - textRegionPoints[1][1])*xyPoints[0][0] +
                            textRegionPoints[0][0]*textRegionPoints[1][1] -
                            textRegionPoints[0][1]*textRegionPoints[1][0]) / verticalBorderLength) # wiki formula

longLines = np.where(np.array(lineLengths) > int(max(lineLengths)/2))
interDistance = round(np.mean(np.diff([yCoordsAllPoints[i] for i in longLines[0]])))

for line in p.textRegion.findall("bergamo:TextLine", p.ns):
    # line[0].attrib['points'] = str(textRegionPoints[0][0])+ ',' + line[0].attrib['points'].split(' ')[0].split(',')[1] + ' ' + line[0].attrib['points'] # line[0] for the coords, line[1] for the baseline
    line[1].attrib['points'] = str(textRegionPoints[0][0])+ ',' + line[1].attrib['points'].split(' ')[0].split(',')[1] + ' ' + line[1].attrib['points']

plt.figure(0)
plt.hist(lineLengths, bins=100)
plt.title("Histogram of baseline lengths")
plt.show()

plt.figure(1)
plt.hist(lineDistFromLeft, bins=100)
plt.title("Histogram of baseline distances from left textbox border")
plt.show()

problemLinesLength = np.where(np.array(lineLengths) < int(max(lineLengths)/2)) # lines too short
problemLinesDistance = np.where(np.array(lineDistFromLeft) > int(max(lineDistFromLeft)/4)) # lines too far away from the left textborder

linesToTagComment = np.intersect1d(problemLinesLength, problemLinesDistance)
linesToMerge = np.setdiff1d(problemLinesLength, problemLinesDistance)

idxPrevLongLine = []
idxNextLongLine = []
distNextLongLine = []
distPrevLongLine = []
for lineIdx in linesToMerge:
    if lineIdx < longLines[0][0]:
        idxPrevLongLine.append(None)
        distPrevLongLine.append(verticalBorderLength)
    else :
        idxPrevLongLine.append(longLines[0][np.argmax(longLines[0] > lineIdx) - 1])
        distPrevLongLine.append(np.abs(yCoordsAllPoints[lineIdx] - yCoordsAllPoints[idxPrevLongLine[-1]]))

    if lineIdx > longLines[0][-1]:
        idxNextLongLine.append(None)
        distNextLongLine.append(verticalBorderLength)
        # linesToRemove.append(line)
    else :
        idxNextLongLine.append(longLines[0][np.argmax(longLines[0] > lineIdx)])
        distNextLongLine.append(np.abs(yCoordsAllPoints[lineIdx] - yCoordsAllPoints[idxNextLongLine[-1]]))

idxMerge = [idxPrevLongLine[i] if distPrevLongLine[i] < distNextLongLine[i] else idxNextLongLine[i] for i in range(len(distNextLongLine))]

if len(idxMerge) > len(set(idxMerge)):
    print('Attention: long line matches multiple merges')

linesToRemove = []
for l in range(len(idxMerge)):
    linesBaseline[idxMerge[l]] = linesBaseline[linesToMerge[l]] + linesBaseline[idxMerge[l]]
    linesToRemove.append(linesToMerge[l])





# hist, bin_edges = np.histogram(lineLengths)

"""