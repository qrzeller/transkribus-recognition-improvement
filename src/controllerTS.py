from src.main import evaluateTextRegions, mergeCommentLines, extendBaselines
from src.transkribusServer import TrtanskribusServer
from src.xmlParser import XmlParser

credentials = {'user': "quentin.zeller@etu.unige.ch", 'password': "pttptt3*"}
documentsInfo = {'colId': 35875, 'docId': 163753}

ts = TrtanskribusServer(credentials['user'], credentials['password'], colId=documentsInfo['colId'])
docList, docId = ts.list_documents()
# parse doc from the server (specific document)
pages = ts.get_documents(documentsInfo['docId'])

for npage in range(11):#range(len(pages)):
    p_test = pages[npage]
    print("Page number %d ----------- " % npage)

    p_test = p_test.replace("CITlab_LA_ML:v=?0.1", "NTIC:v=?0.8")

    p = XmlParser(p_test)
    root = p.root
    p.findTextRegion()

    evaluateTextRegions(p)
    for textRegionIdx in range(len(p.textRegion)):
        mergeCommentLines(textRegionIdx, p)
        extendBaselines(textRegionIdx, p)
    p_test = p.toString()

    #pp = p.prettyPrintTo("./test2.xml")


    # p_test = p_test.replace("quentintest", "banane")
    # somecomment = "<!--" \
    #               " helloworld " \
    #               "-->"
    # p_test = p_test + somecomment
    # file = open("testfile.xml", "w")
    # file.write(p_test)
    # file.close()

    response = ts.uploadDocument(documentsInfo['docId'], npage + 1, p_test)
