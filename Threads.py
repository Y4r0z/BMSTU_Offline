from DataManager import DataManager
from FileManager import FileManager
from PySide6 import QtCore
from PySide6.QtCore import QThread, Signal, QMutex

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

downloadMutex = QMutex()
class downloadFileThread(QThread):
    def __init__(self, name, path):
        super().__init__()
        self.name = name
        self.path = path
        self.isRunning = True

    def run(self):
        while True:
            if downloadMutex.tryLock():
                FileManager().downloadFile(self.name, self.path)
                downloadMutex.unlock()
                self.isRunning = False
                break
            QThread.msleep(10)


