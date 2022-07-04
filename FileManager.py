import json
from DataManager import DataManager
from PySide6.QtGui import QIcon
import os
import sys
import requests
import subprocess
from IconsManager import IconsManager
from Debugger import Debugger
class FileManager():
    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(FileManager, cls).__new__(cls)
            cls._icons = IconsManager()
        if not os.path.exists('data'):
            os.makedirs('data')
        if not os.path.exists('repository'):
            os.makedirs('repository')

        return cls.__instance

    def saveSubjects(self):
        DataManager().initiateData()
        jsonString = json.dumps(DataManager().getSubjects(), ensure_ascii=False)
        with open('data/subjects.json', 'w', encoding = 'utf-8') as file:
            file.write(jsonString)

    def loadSubjects(self):
        try:
            with open ('data/subjects.json', 'r', encoding = 'utf-8') as file:
                data = json.load(file)
                DataManager().setSubjects(data)
            return True
        except:
            Debugger().throw('Cant open "data/subjects.json"!')
            return False

    def saveDownloads(self):
        if not DataManager().dataInitiated and False:
            Debugger().throw("Can't save downloads info without Datamanager's init!")
            return False
        jsonString = json.dumps(DataManager().getDownloads(), ensure_ascii=False)
        try:
            with open('data/downloads.json', 'w', encoding = 'utf-8') as file:
                file.write(jsonString)
        except Exception as e:
            Debugger().throw('Cant save Downloads!\n' + str(e))
            return False
        return True

    def loadDownloads(self):
        downloads = []
        try:
            with open ('data/downloads.json', 'r', encoding = 'utf-8') as file:
                downloads = json.load(file)
                DataManager().setDownloads(downloads)
        except:
            Debugger().throw('Cant load downloads!')
            return False
        return True

    def getIcons(self):
        return self._icons

    def saveUser(self, login = None, password = None):
        if login is None or password is None:
            login = DataManager().username
            password = DataManager().password
            if login is None or password is None:
                return False
        jsonString = json.dumps([{'login':login,'password':password}],ensure_ascii = False)
        with open('data/user.json', 'w', encoding = 'utf-8') as file:
            file.write(jsonString)
        return True

    def loadUser(self):
        try:
            with open ('data/user.json', 'r', encoding = 'utf-8') as file:
                data = json.load(file)
                DataManager().setUser(data[0]['login'], data[0]['password'])
            return True
        except Exception as e:
            Debugger().throw('Cant open data/user.json\n' + str(e))
            return False

    def saveSettings(self, settings = None):
        if settings is None:
            settings = DataManager().getSettings()
        jsonString = json.dumps(settings, ensure_ascii = False)
        with open ('data/settings.json', 'w', encoding = 'utf-8') as file:
            file.write(jsonString)

    def loadSettings(self):
        try:
            with open ('data/settings.json', 'r', encoding = 'utf-8') as file:
                data = json.load(file)
                DataManager().setSettings(data)
            return True
        except Exception as e:
            Debugger().throw('Cant open data/settings.json\n' + str(e))
            return False

    def downloadFile(self, name, wPath):
        if not DataManager().isOnline:
            Debugger().throw('FileManager().downloadFile(). The program is not online!')
            return False
        path, file = DataManager().getFilePath(name, wPath)
        if len(path) < 2:
            return False
        try:
            dir = '/'.join([path[i] for i in range(0, len(path)-1)])
            if not os.path.exists(dir):
                os.makedirs(dir)
            filename = path[-1]
            fullPath = f'{dir}/{filename}'
            with open(fullPath, 'wb') as f:
                f.write(DataManager().getDownloadData(file['href']))
            DataManager().addDownload(file['href'])
            parent = DataManager().getFileParent(file, wPath)
            if not parent is None:
                cnt = len(parent['files'])
                n = 0
                for f in parent['files']:
                    if DataManager().isDownloaded(f['href']):
                        n+=1
                DataManager().addDownload(parent['href'], n/cnt*100)
            self.saveDownloads()
            return True
        except Exception as e:
            Debugger().throw('Cant download file\n' + str(e))
            return False

    def openFile(self, text, wPath):
        pathRaw = DataManager().getFilePath(text, wPath)
        if not DataManager().isDownloaded(pathRaw[1]['href']):
            return False
        if len(pathRaw) == 0:
            return False
        if sys.platform.startswith('win'):
            path = '\\'.join(pathRaw[0])
            subprocess.Popen(path, shell = True)
        else:
            path = '/'.join(pathRaw[0])
            myEnv = dict(os.environ)
            lp_key = 'LD_LIBRARY_PATH'
            lp_orig = myEnv.get(lp_key + '_ORIG')
            if lp_orig is not None:
                myEnv[lp_key] = lp_orig
            else:
                lp = myEnv.get(lp_key)
                if lp is not None:
                    myEnv.pop(lp_key)
            subprocess.Popen(["xdg-open", path], env=myEnv)

        return True

    def deleteFile(self, text, wPath):
        pathRaw = DataManager().getFilePath(text, wPath)
        file = pathRaw[1]
        if not DataManager().isDownloaded(file['href']):
            return False
        if len(pathRaw) == 0:
            return False
        path = '/'.join(pathRaw[0])
        if not os.path.exists(path):
            Debugger().throw('File does not exists: ' + path)
        DataManager().removeDownload(file['href'])
        self.saveDownloads()
        parent = DataManager().getFileParent(file, wPath)
        if not parent is None:
            cnt = len(parent['files'])
            n = 0
            for f in parent['files']:
                if DataManager().isDownloaded(f['href']):
                    n+=1
            if n != 0:
                DataManager().addDownload(parent['href'], n/cnt*100)
            else:
                DataManager().removeDownload(parent['href'])
            self.saveDownloads()
        os.remove(path)
        return True


