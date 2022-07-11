from PySide6 import QtCore
from PySide6.QtCore import QThread, Signal, QMutex, QObject
from Debugger import Debugger
from FileManager import FileManager
from DataManager import DataManager
from ListItem import ListFile, ListStorage

class RemoveItem(QObject):
    complete = Signal()
    update = Signal()
    def __init__(self, file):
        super().__init__()
        self.file = file
        self.file.locked = True

    def execute(self):
        if self.file['download'] == 0:
            self.complete.emit()
            return
        if self.file.Signature == 'file':
            FileManager().deleteFile(self.file)
        else:
            self._initItem()
            files = []
            ListFile.GetFiles(self.file, files)
            for i in files:
                FileManager().deleteFile(i)
                self.update.emit()
        self.file.locked = False
        self.complete.emit()
    
    def _initItem(self):
        item = self.file
        if item.parent is None:
            activities = []
            if len(item['files']) == 0:
                activities = DataManager().getActivities(item)
            if len(item['files']) == 0: return
            activities = item['files']
            for i in activities:
                if i.Signature == 'file': continue
                if len(i['files']) == 0:
                    files = DataManager().getFiles(i)
        elif item.parent.parent is None:
            DataManager().getFiles(item)


RemoverMutex = QMutex()
class RemoverThread(QThread):
    queue = []

    def __init__(self):
        super().__init__()

    def push(self, item):
        while True:
            if RemoverMutex.tryLock():
                self.queue.append(item)
                RemoverMutex.unlock()
                return
            QThread.msleep(20)

    def run(self):
        currentTask = None
        while True:
            QThread.msleep(150)
            if len(self.queue) == 0:
                continue
            if RemoverMutex.tryLock():
                currentTask = self.queue.pop()
                RemoverMutex.unlock()
                currentTask.execute()



class Remover:
    __instance = None

    thread = None

    def __new__(self):
        if self.__instance is None:
            self.__instance = super(Remover, self).__new__(self)
            self.thread = RemoverThread()
            self.thread.start()
        return self.__instance

    def push(self, item):
        self.thread.push(item)