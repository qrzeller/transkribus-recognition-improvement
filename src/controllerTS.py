from src.transkribusServer import TrtanskribusServer

credentials = {'user': "quentin.zeller@etu.unige.ch", 'password': "pttptt3*"}
documentsInfo = {'colId': 35875, 'docId': 135607}

ts = TrtanskribusServer(credentials['user'], credentials['password'], colId=documentsInfo['colId'])
docList, docId = ts.list_documents()
# parse doc from the server (specific document)
pages = ts.get_documents(documentsInfo['docId'])

for npage in range(len(pages)):
    p_test = pages[npage]


    p_test = p_test.replace("CITlab_LA_ML:v=?0.1", "NTIC:v=?0.8")

    # p_test = p_test.replace("quentintest", "banane")
    # somecomment = "<!--" \
    #               " helloworld " \
    #               "-->"
    # p_test = p_test + somecomment
    # file = open("testfile.xml", "w")
    # file.write(p_test)
    # file.close()

    response = ts.uploadDocument(documentsInfo['docId'], npage + 1, p_test)
