#!/bin/python3.7
import xml.etree.ElementTree as ET
from collections import OrderedDict


class XmlParser:

    def __init__(self, document: str):
        print("Init XML Parser")
        # self.doc = ET.parse(document)
        self.doc = ET.ElementTree(ET.fromstring(document))
        self.root = self.doc.getroot()

    def findTextRegion(self):
        self.ns = {"manuscript": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}
        self.textRegion = self.root.findall("manuscript:Page/manuscript:TextRegion", self.ns) #[0]
        self.parentTR = self.root.findall("manuscript:Page", self.ns)[0] # assumme one page

    def getChildByName(self,root: ET.ElementTree,  node: str) -> ET.ElementTree:
        return root.get(node)

    def removeTR(self, TR):
        print('Removed TR: ', TR.attrib)
        self.parentTR.remove(TR)

    def prettyPrintTo(self, fileDest):
        self.doc.write(fileDest)

    def toString(self):
        s = ET.tostring(self.root, encoding='utf8', method='xml').decode()
        return s

    def removeTL(self, textRegionIdx, textLine):
        print("Removed line : ", textLine.attrib['id'])
        self.textRegion[textRegionIdx].remove(textLine)