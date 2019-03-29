#!/bin/python3.7
import xml.etree.ElementTree as ET


class XmlParser:

    def __init__(self, document: str):
        print("Init XML Parser")
        self.root = ET.parse(document).getroot()

    def findLines(self):
        self.ns = {"bergamo": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}
        self.textRegion = self.root.findall("bergamo:Page/bergamo:TextRegion", self.ns)[0]

        return self.textRegion

    def processTextLine(self):
        for line in self.textRegion.findall("bergamo:TextLine", self.ns):
            print(line[0].attrib)
            # TODO


    def getChildByName(self,root: ET.ElementTree,  node: str) -> ET.ElementTree:
        return root.get(node)