import os

from TranskribusPyClient.src.TranskribusPyClient import client
import lxml.etree as etree

"""
s = client.TranskribusClient()

user = "quentin.zeller@etu.unige.ch"
password = "pttptt3*"

s.auth_login(user, password)
colId = 35875
ntic_col = s.listDocsByCollectionId(colId)

print("Document accessible : ")
for i in ntic_col:
    print(i['title'], end=', ')
print("\r\n")

download_directory = "../data/collection/"
# download images
#s.download_document(colId,ntic_col[0]['docId'], download_directory+"%d"%colId)

docId = ntic_col[0]['docId']
#dom = s.getDocByIdAsXml(colId, docId, nrOfTranscripts=1 ) # number of trankripts to receive per page

# Transcription
#doc1 = etree.tostring(dom, pretty_print=True).decode("utf-8")

#s.download_collection(colId,download_directory+"%d-collection"%colId, bNoImage=True)


trp = s.getDocById(colId, docId, nrOfTranscripts=1)

pageList = trp["pageList"]

"""


class TrtanskribusServer():

    def __init__(self, user, password, colId=-1):
        self.s = client.TranskribusClient()
        if self.s.auth_login(user, password): print("Login successful")
        else: print("Cannot login")
        self.current_Collection = colId


    def get_documents(self, docId, nr_transkripts = 1, colId = None):
        if colId is None: colId=self.current_Collection
        # inspired from TranskribusPyClient implementation
        trp = self.s.getDocById(colId, docId, nr_transkripts)
        pageList = trp["pageList"]
        lFileList = []
        self.pages = []
        for page in pageList['pages']:
            pagenum = page['pageNr']
            imgFileName = page['imgFileName']
            base, _ = os.path.splitext(imgFileName)
            lFileList.append(base)
            urlImage = page['url']
            dicTranscript0 = page['tsList']["transcripts"][0]
            urlXml = dicTranscript0['url']
            resp = self.s._GET(urlXml)
            self.pages.append(resp.text)

        return self.pages

    def uploadDocument(self, docId, pnum, transkript):
        respText = self.s.postPageTranscript(self.current_Collection, docId, pnum, transkript)

        return respText


    def download_collection_to_file(self, colId = None, download_directory = "../data/collection/", bNoImage=True):
        if colId is None: colId=self.current_Collection
        self.s.download_collection(colId, download_directory + "%d-collection" % colId, bNoImage)

    def list_documents(self, colId = None):
        if colId is None: colId=self.current_Collection
        print("list collection : ", colId)
        docList = self.s.listDocsByCollectionId(colId)
        docIDs = []
        print("Document accessible : (return docList, docIDs)")
        for i in docList:
            print(i['title'], end=', ')
            docIDs.append(i['docId'])
        print("\r\n")
        return docList, docIDs


    def __del__(self):
        self.logout()

    def logout(self):
        self.s.auth_logout()


user = "quentin.zeller@etu.unige.ch"
password = "pttptt3*"
ts = TrtanskribusServer(user, password, colId = 35875)
docList, docId = ts.list_documents()
# parse doc from the server (specific document)
pages = ts.get_documents(docId[0])

npage = 8
p_test = pages[npage]

p_test = p_test.replace("quentintest", "banane")
somecomment = "<!--" \
              " helloworld " \
              "-->"
p_test = p_test + somecomment
file = open("testfile.xml","w")
file.write(p_test)
file.close()

response = ts.uploadDocument(docId[0],npage+1,p_test)

#s.auth_logout()