from src.main import evaluateTextRegions, mergeCommentLines, extendBaselines
from src.transkribusServer import TrtanskribusServer
from src.xmlParser import XmlParser


class controllerTS:
    def __init__(self, user, password, colId, docId, annotation):

        # credentials = {'user': "quentin.zeller@etu.unige.ch", 'password': "pttptt3*"}
        # documentsInfo = {'colId': 35875, 'docId': 163893}
        credentials = {'user': user, 'password': password}
        documentsInfo = {'colId': colId, 'docId': docId}

        ts = TrtanskribusServer(credentials['user'], credentials['password'], colId=documentsInfo['colId'])
        docList, docId = ts.list_documents()
        # parse doc from the server (specific document)
        pages = ts.get_documents(documentsInfo['docId'])

        for npage in range(len(pages)):
            p_test = pages[npage]
            print("Page number %d ----------- " % npage)

            p_test = p_test.replace("CITlab_LA_ML:v=?0.1", "NTIC:v=?0.8")

            p = XmlParser(p_test)
            root = p.root
            p.findTextRegion()

            evaluateTextRegions(p)
            for textRegionIdx in range(len(p.textRegion)):
                mergeCommentLines(textRegionIdx, p, annotation)
                extendBaselines(textRegionIdx, p)
            p_test = p.toString()

            response = ts.uploadDocument(documentsInfo['docId'], npage + 1, p_test)
