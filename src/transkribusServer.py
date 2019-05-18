import os

from TranskribusPyClient.src.TranskribusPyClient import client

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
        for page in pageList['pages']: ## TODO
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
        print("Uploading page %d to document %d" % (pnum, docId))
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
