from DataManager import DataManager
from FileManager import FileManager
from PySide6 import QtCore
from PySide6.QtCore import QThread, Signal, QMutex
from ListItem import ListFile, ListStorage, ListItem
class LoginThread(QThread):
    complete = Signal(bool)

    def __init__(self, login, password):
        super().__init__()
        self.login = login
        self.password = password

    def run(self):
        if DataManager().login(self.login, self.password):
            self.complete.emit(True)
        else:
            self.complete.emit(False)


class InitItemThread(QThread):
    complete = Signal(ListItem)
    def __init__(self, item, listMode):
        super().__init__()
        self.item = item
        self.mode = listMode
    
    def run(self):
        self.item.locked = True
        if self.mode == 0:
            item = self.item
            activities = []
            if len(item['files']) == 0:
                activities = DataManager().getActivities(item)
            if len(item['files']) == 0: return
            activities = item['files']
            for i in activities:
                if i.Signature == 'file': continue
                if len(i['files']) == 0:
                    files = DataManager().getFiles(i)
        elif self.mode == 1:
            DataManager().getFiles(item)
        self.item.locked = False
        self.complete.emit(self.item)
