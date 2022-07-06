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
        #DataManager().initiateData()
        subjects = DataManager().getSubjects()
        jsonString = json.dumps([i.toDict() for i in DataManager().getSubjects()], ensure_ascii=False)
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

    def downloadFile(self, file):
        if not DataManager().isOnline:
            Debugger().throw('FileManager().downloadFile(). The program is not online!')
            return False
        rawPath = file.path
        try:
            dir = DataManager().listToPath(rawPath[:-1])
            if not os.path.exists(dir):
                os.makedirs(dir)
            filename = rawPath[-1]
            fullPath = f'{dir}/{filename}'
            with open(fullPath, 'wb') as f:
                f.write(DataManager().getDownloadData(file))
            file.downloadProgress = 100
            parent = file.parent
            if parent is not None:
                cnt = len(parent['files'])
                n = 0
                for f in parent['files']:
                    if f['download'] > 0:
                        n += 1
                parent.downloadProgress = n/cnt*100
            return True
        except Exception as e:
            Debugger().throw('Cant download file\n' + str(e))
            return False

    def openFile(self, file):
        if not DataManager().isDownloaded(file['href']):
            return False
        path = DataManager().listToPath(file.path)
        if sys.platform.startswith('win'):
            subprocess.Popen(path, shell = True)
        else: #Linux костыл
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

    def deleteFile(self, file):
        if file['download'] < 100:
            return False
        path = DataManager().listToPath(file.path)
        if not os.path.exists(path):
            Debugger().throw('File does not exists: ' + path)
        file.downloadProgress = 0
        parent = file.parent
        if parent is not None:
            cnt = len(parent['files'])
            n = 0
            for f in parent['files']:
                if f['download'] > 0:
                    n+=1
            if n != 0:
                parent.downloadProgress = n/cnt*100
            else:
                parent.downloadProgress = 0
        os.remove(path)
        return True


