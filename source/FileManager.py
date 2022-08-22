import json
from DataManager import DataManager
from PySide6.QtGui import QIcon
import os
import sys
import requests
import subprocess
from IconsManager import IconsManager
from Debugger import Debugger
from ListItem import ListFile, ListStorage
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
    
    def mergeSubjects(self):
        current = DataManager().getSubjects()
        previous = DataManager().bufferSubjects
        if len(current) != len(previous):
            return current
        try:
            merged = [ListFile.Merge(current[i], previous[i]) for i in range(len(current))]
        except Exception as e:
            Debugger().throw("FM.mergeSubjects() error: " + str(e))
            return previous
        return merged


    def saveSubjects(self):
        jsonString = json.dumps([i.toDict() for i in self.mergeSubjects()], ensure_ascii=False)
        with open('data/subjects.json', 'w', encoding = 'utf-8') as file:
            file.write(jsonString)

    def loadSubjects(self):
        try:
            with open('data/subjects.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                DataManager().setSubjects([ListFile.FromDict(i) for i in data])
            return True
        except:
            Debugger().throw('Cant open "data/subjects.json"!')
            return False

    def getIcons(self):
        return self._icons

    def saveUser(self, login=None, password=None):
        if login is None or password is None:
            login = DataManager().username
            password = DataManager().password
            if login is None or password is None:
                return False
        jsonString = json.dumps([{'login':login, 'password':password}], ensure_ascii = False)
        with open('data/user.json', 'w', encoding='utf-8') as file:
            file.write(jsonString)
        return True

    def loadUser(self):
        try:
            with open('data/user.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                DataManager().setUser(data[0]['login'], data[0]['password'])
            return True
        except Exception as e:
            Debugger().throw('Cant open data/user.json\n' + str(e))
            return False

    def saveSettings(self, settings=None):
        if settings is None:
            settings = DataManager().getSettings()
        jsonString = json.dumps(settings, ensure_ascii=False)
        with open('data/settings.json', 'w', encoding='utf-8') as file:
            file.write(jsonString)

    def loadSettings(self):
        try:
            with open('data/settings.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                DataManager().setSettings(data)
            return True
        except Exception as e:
            Debugger().throw('Cant open data/settings.json\n' + str(e))
            return False

    def downloadFile(self, file):
        file.locked = True
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
            file.locked = False
            return True
        except Exception as e:
            file.locked = False
            Debugger().throw('Cant download file\n' + str(e))
            return False
    
    def downloadFileGradually(self, file, signal):
        file.locked = True
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
            r = DataManager().session.get(file['href'], stream = True)
            length = int(r.headers.get('content-length'))
            download = 0
            emitCounter = 0
            with open(fullPath, 'wb') as f:
                for data in r.iter_content(chunk_size=4096):
                    download += len(data)
                    file.downloadProgress = 100 * (download/length)
                    #Вызов апдейта только 10 раз, чтобы избежать лагов
                    if round(file.downloadProgress) / 10 > emitCounter:
                        emitCounter += 1
                        signal.emit()
                    f.write(data)
            file.downloadProgress = 100
            file.locked = False
            return True
        except Exception as e:
            file.locked = False
            Debugger().throw('Cant download file\n' + str(e))
            return False

    def openFile(self, file):
        if file['download'] < 100:
            return False
        path = DataManager().listToPath(file.path)
        if sys.platform.startswith('win'):
            subprocess.Popen(path, shell=True)
        else: #Linux костыль
            myEnv = dict(os.environ)
            lp_key = 'LD_LIBRARY_PATH'
            lp_orig = myEnv.get(lp_key + '_ORIG')
            if lp_orig is not None:
                myEnv[lp_key] = lp_orig
            else:
                lp = myEnv.get(lp_key)
                if lp is not None:
                    myEnv.pop(lp_key)
            try:
                subprocess.Popen(["xdg-open", path], env=myEnv)
            except Exception as e:
                Debugger().throw("FM.openFIle can't open file: " + str(e))
        return True

    def deleteFile(self, file):
        file.locked = True
        if file['download'] < 100:
            return False
        path = DataManager().listToPath(file.path)
        if not os.path.exists(path):
            Debugger().throw('File does not exists: ' + path)
        file.downloadProgress = 0
        parent = file.parent
        try:
            os.remove(path)
        except Exception as e:
            Debugger().throw("FM.deleteFile() can't os.remove: " + str(e))
        file.locked = False
        return True


