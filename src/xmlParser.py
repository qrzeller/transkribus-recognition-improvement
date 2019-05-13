#!/bin/python3.7
import xml.etree.ElementTree as ET
from collections import OrderedDict


class XmlParser:

    def __init__(self, document: str):
        print("Init XML Parser")
        self.doc = ET.parse(document)
        self.root = self.doc.getroot()

    def findTextRegion(self):
        self.ns = {"manuscript": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}
        self.textRegion = self.root.findall("manuscript:Page/manuscript:TextRegion", self.ns) #[0]
        self.parentTR = self.root.findall("manuscript:Page", self.ns)[0] # assumme one page

    # def processTextLine(self):
    #     self.textRegionCoords = self.textRegion.findall("bergamo:Coords", self.ns)[0].attrib['points']
    #     self.linesCoords = OrderedDict()
    #     self.linesBaseline = OrderedDict()
    #     for line in self.textRegion.findall("bergamo:TextLine", self.ns):
    #         self.linesCoords[line.get("id")] = line[0].attrib['points'] # line[0] for the coords, line[1] for the baseline
    #         self.linesBaseline[line.get("id")] = line[1].attrib['points']  # line[0] for the coords, line[1] for the baseline
    #         # print(line[0].attrib['points'])
    #         # TODO


    def getChildByName(self,root: ET.ElementTree,  node: str) -> ET.ElementTree:
        return root.get(node)

    def removeTR(self, TR):
        print(TR.attrib)
        self.parentTR.remove(TR)

    def prettyPrintTo(self, fileDest):
        self.doc.write(fileDest)

    def removeTL(self, textRegion, textLine):
        print("Removed line : ", textLine.attrib['id'])
        textRegion.remove(textLine)