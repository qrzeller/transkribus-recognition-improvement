from lxml import etree
import random, collections

tree = etree.parse("./data/xml-sample/old_24_BERGAMO_08.xml")
root = tree.getroot()
print("Reading", root.tag, "root node.")
print("Attribute : ", root.attrib)

print(root.find("Page"))

for node in tree.xpath("//PcGts/Page/TextRegion"):
    print(node.tag)




