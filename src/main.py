#!/bin/python3.7
from src.xmlParser import XmlParser

p = XmlParser('../data/xml-sample/old_24_BERGAMO_08.xml')

root = p.root

p.findLines()
p.processTextLine()