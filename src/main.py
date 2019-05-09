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

p = XmlParser('./data/xml-sample/old_24_BERGAMO_08.xml')

root = p.root

p.findTextRegion()
# p.processTextLine()

def getXYPoints(stringList):
    result =[[int(point) for point in pair.split(',')] for pair in stringList.split(' ')]
    return result

# Get info about text region box
textRegionCoords = p.textRegion.findall("bergamo:Coords", p.ns)[0].attrib['points']
textRegionPoints = getXYPoints(textRegionCoords)
leftBorderLength = np.abs(textRegionPoints[0][1] - textRegionPoints[1][1]) # use only y-points, the textbox is rectangular

# Get info about text lines
linesCoords = OrderedDict()
linesBaseline = OrderedDict()
for line in p.textRegion.findall("bergamo:TextLine", p.ns):
    linesCoords[line.get("id")] = line[0].attrib['points'] # line[0] for the coords, line[1] for the baseline
    linesBaseline[line.get("id")] = line[1].attrib['points']  # line[0] for the coords, line[1] for the baseline

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
                            textRegionPoints[0][1]*textRegionPoints[1][0])/leftBorderLength) # wiki formula

longLines = np.where(np.array(lineLengths) > int(max(lineLengths)/2)) # lines too short

for y in longLines[0]:


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

linesToRemove = np.intersect1d(problemLinesLength, problemLinesDistance)
linesToMerge = np.setdiff1d(problemLinesLength, problemLinesDistance)

# hist, bin_edges = np.histogram(lineLengths)

