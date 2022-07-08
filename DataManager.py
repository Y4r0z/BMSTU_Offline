import requests
from Debugger import Debugger
from NetworkFunctions import *
import os
import sys
from ListItem import ListFile, ListStorage
class DataManager():
    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(DataManager, cls).__new__(cls)
            cls.session = requests.Session()
            cls.subjects = []
            cls.bufferSubjects = []
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
            rawSubjects = getSubjects(self.session, self.loginResult)
            subjects = []
            for i in rawSubjects:
                subject = ListStorage(i['text'], 'course', i['href'])
                for i in self.bufferSubjects:
                    find = ListFile.FindByHref(subject.href, i)
                    if find is not None:
                        subject.downloadProgress = find.downloadProgress
                subjects.append(subject)
            self.subjects = subjects
        except Exception as e:
            Debugger().throw("getSubjects() error:\n" + str(e))
        return self.subjects

    def getActivities(self, subject):
        if len(subject['files']) != 0:
            return subject['files']
        try:
            rawActivities = getActivities(self.session, subject)
            activities = []
            for i in rawActivities:
                if i['type'] in ListStorage.Types:
                    activity = ListStorage(i['text'], i['type'], i['href'])
                    activity.parent = subject
                else:
                    activity = ListFile(i['text'], i['type'], i['href'])
                    activity.parent = subject
                    activity.path = self.generateFilePathList(activity)
                for i in self.bufferSubjects:
                    find = ListFile.FindByHref(activity.href, i)
                    if find is not None:
                        activity.downloadProgress = find.downloadProgress
                activities.append(activity)
            if len(subject.storage) == 0:
                subject.set(activities)
            return activities
        except Exception as e:
            Debugger().throw("GetActivities() error:\n" + str(e))
        return []


    def getFiles(self, assign):
        rawFiles = getFiles(self.session, assign)
        files = []
        if rawFiles is None or len(rawFiles) == 0:
            return None
        for i in rawFiles:
            file = ListFile(i['text'], i['type'], i['href'])
            file.parent = assign
            file.path = self.generateFilePathList(file)
            for i in self.bufferSubjects:
                find = ListFile.FindByHref(file.href, i)
                if find is not None:
                    file.downloadProgress = find.downloadProgress
            files.append(file)
        if len(assign.storage) == 0:
            assign.set(files)
        return files

    def endSession(self):
        if not self.isOnline:
            return
        endSession(self.session)

    def initiateData(self):
        subs = self.getSubjects()
        for i in subs:
            acts = self.getActivities(i)
            for j in acts:
                if j['files'] is None:
                    continue
                if len(j['files']) == 0 and j['type'] == 'assign':
                    j.set( self.getFiles(j))
        self.dataInitiated = True

    def setSubjects(self, data):
        if len(self.subjects) == 0:
            if self.isOnline:
                self.bufferSubjects = data
            else:
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
            acts = self.getActivities(i)
            for j in acts:
                if j['text'] == path[1] and j['href'] == file['parent']:
                    return j
        return None


    def listToPath(self, rawPath):
        if rawPath is None or len(rawPath) == 0:
            Debugger().throw("ListToPath() wrong input!")
            return None
        if sys.platform.startswith('win'):
            return '\\'.join(rawPath)
        else:
            return '/'.join(rawPath)

    def getAllParents(self, listItem, lst):
        if listItem.parent is None:
            return lst
        lst.insert(0, listItem.parent.text)
        return self.getAllParents(listItem.parent, lst)

    def generateFilePathList(self, file):
        rawFileName = file.text
        fileExtension = '.' + file.type
        rawPathList = ['repository'] + self.getAllParents(file, []) + [rawFileName]
        forbiddenChars = [i for i in(' -./<>:"\|?*#%&{}$!@=+`,()' + "'")]
        for i in range(len(rawPathList)):
            newStr = ''.join(c for c in rawPathList[i] if c not in forbiddenChars)
            rawPathList[i] = newStr
        rawPathList[-1] = rawPathList[-1] + fileExtension
        return rawPathList

    def getDownloadData(self, file):
        r = self.session.get(file['href'])
        return r.content


    def findByName(self, text, path = []):
        subjects = self.getSubjects()
        n = len(path)
        for i in subjects:
            if n == 0:
                if i['text'] == text:
                    return i
                continue
            if i['text'] != path[0]: continue
            activities = self.getActivities(i)
            for j in activities:
                if n == 1:
                    if j['text'] == text:
                        return j
                    continue
                if j['text'] != path[1] or j['files'] is None or len(j['files']) == 0: continue
                for k in j['files']:
                    if k['text'] == text:
                        return k

    def find(self, herf):
        for i in self.getSubjects():
            found = ListFile.FindByHref(href, i)
            if i is not None:
                return i

                
























