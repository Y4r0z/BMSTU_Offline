import lxml.html
import requests
import urllib.parse
import os
from Debugger import Debugger
from NetworkFunctions import *


class DataManager():
    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(DataManager, cls).__new__(cls)
            cls.session = requests.Session()
            cls.subjects = []
            cls.downloads = []
            cls.loadedFiles = []
            cls.username = None
            cls.password = None
            cls.settings = {
            'filter': '',
            'mainWindow': None,
            'courseWindow': None,
            'assignWindow': None
            }


            cls.loginResult = None
            cls.isOnline = False
            cls.dataInitiated = False
        return cls.__instance


    def getSubjects(self):
        if len(self.subjects) > 0:
            return self.subjects
        if self.loginResult is None:
            return []
        try:
            self.subjects = getSubjects(self.session, self.loginResult)
        except Exception as e:
            Debugger().throw("getSubjects() error:\n" + str(e))
        return self.subjects

    def getActivities(self, id):
        subjects = self.getSubjects()
        try:
            activities = getActivities(self.session, id, subjects)
            return activities
        except Exception as e:
            Debugger().throw("GetActivities() error:\n" + str(e))
        return []


    def getFiles(self, assign):
        files = getFiles(self.session, assign)
        if files is None:
            return None
        for i in files:
            self.loadedFiles.append(i)
        return files

    def endSession(self):
        if not self.isOnline:
            return
        endSession(self.session)

    def initiateData(self):
        subs = self.getSubjects()
        for i in subs:
            acts = self.getActivities(i['id'])
            for j in acts:
                if j['files'] is None:
                    continue
                if len(j['files']) == 0 and j['type'] == 'assign':
                    j['files'] = self.getFiles(j)
        self.dataInitiated = True

    def setSubjects(self, data):
        if len(self.subjects) == 0:
            self.subjects = data
        else:
            Debugger().throw("DataManaget().setSubjects(data): self.subjects isn't empty")

    def setUser(self, l, p):
        if l is None or p is None:
            Debugger().throw('DataManager().setUser(log, pas): log or pas is None')
        else:
            self.username = l
            self.password = p

    def reloadOnline(self):
        self.subjects = []
        self.initiateData()

    def login(self, username, password):
        response = loginOnline(username, password, self.session)
        self.loginResult = response
        if response.status_code == 200:
            return True
        else:
            return False

    def getSettings(self):
        return self.settings

    def setSettings(self, sets):
        self.settings = sets

    def getFileParent(self, file, path):
        if len(path) < 2:
            return None
        subs = self.getSubjects()
        for i in subs:
            if i['text'] != path[0]:
                continue
            acts = self.getActivities(i['id'])
            for j in acts:
                if j['text'] == path[1] and j['href'] == file['parent']:
                    return j
        return None


    def getRawPath(self, text, path):
        file = None
        subs = self.getSubjects()
        for i in subs:
            if i['text'] != path[0]:
                continue        
            acts = self.getActivities(i['id'])
            for j in acts:
                if j['text'] == text and len(path) == 1:
                    file = j
                    #filename, fileext = os.path.splitext(file['text'])
                    filename = text
                    fileext = '.' + file['type']
                    rawPath = ['repository', path[0], filename]
                    return (rawPath, file, fileext)
                elif len(path) == 1:
                    continue
                if j['text'] != path[1]:
                    continue
                for k in j['files']:
                    if k['text'] == text:
                        file = k

        filename, fileext = file['text'], '.' + file['type']
        rawPath = ['repository', path[0], path[1], filename]
        return (rawPath, file, fileext)


    def getFilePath(self, text, path):
        rawPath, file, fileext = self.getRawPath(text, path)
        if file is None or len(rawPath) == 0:
            Debugger().throw('DM().getFilePath() cant get path.')
            return ([], None)
        chars = [i for i in(' -./<>:"\|?*#%&{}$!@=+`,()' + "'")]
        path = []
        for i in rawPath:
            temp = ''
            for j in i:
                if not j in chars:
                    temp += j
            path.append(temp)
        #Debugger().throw(1, rawPath, '|', fileext)
        path[-1] = path[-1]+fileext
        return (path, file)


    def getDownloadData(self, href):
        r = self.session.get(href)
        return r.content

    def isDownloaded(self, href):
        for i in self.downloads:
            if i['href'] == href:
                return True
        return False

    def getDownload(self, href):
        for i in self.downloads:
            if i['href'] == href:
                return i
        return {'href':None, 'progress':0}

    def addDownload(self, href, progress = 100):
        if not self.isDownloaded(href):
            self.downloads.append({'href':href, 'progress':progress})
        else:
            self.getDownload(href)['progress'] = progress
        if type is None:
            return

    def removeDownload(self, href):
        self.downloads = [i for i in self.downloads if i['href'] != href]


    def getDownloads(self):
        return self.downloads

    def setDownloads(self, downloads):
        self.downloads = downloads

    def findByName(self, text, path):
        subjects = self.getSubjects()
        n = len(path)
        for i in subjects:
            if n == 0:
                if i['text'] == text:
                    return i
                continue
            if i['text'] != path[0]: continue
            activities = self.getActivities(i['id'])
            for j in activities:
                if n == 1:
                    if j['text'] == text:
                        return j
                    continue
                if j['text'] != path[1] or j['files'] is None: continue
                for k in j['files']:
                    if k['text'] == text:
                        return k





























