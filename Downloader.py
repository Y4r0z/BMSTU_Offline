from PySide6 import QtCore
from PySide6.QtCore import QThread, Signal, QMutex, QObject
from Debugger import Debugger
from FileManager import FileManager


class DownloadItem(QObject):
    complete = Signal()
    def __init__(self, _name, _path):
        super().__init__()
        self.name = _name
        self.path = _path

    def execute(self):
        Debugger().throw("DI_Execute: " + self.name)
        FileManager().downloadFile(self.name, self.path)
        Debugger().throw("DI_Execute complete")
        self.complete.emit()


downloaderMutex = QMutex()
class DownloaderThread(QThread):
    queue = []

    def __init__(self):
        super().__init__()

    def push(self, item):
        while True:
            if downloaderMutex.tryLock():
                Debugger().throw("DT_push")
                self.queue.append(item)
                downloaderMutex.unlock()
                return
            Debugger().throw("Attempt to push")
            QThread.msleep(20)

    def run(self):
        currentTask = None
        while True:
            QThread.msleep(150)
            Debugger().throw("wait, len: " + str(len(self.queue)))
            if len(self.queue) == 0:
                continue
            if downloaderMutex.tryLock():
                currentTask = self.queue.pop()
                downloaderMutex.unlock()
                currentTask.execute()






class Downloader:
    __instance = None

    thread = None

    def __new__(self):
        if self.__instance is None:
            self.__instance = super(Downloader, self).__new__(self)
            self.thread = DownloaderThread()
            self.thread.start()
        return self.__instance

    def push(self, item):
        self.thread.push(item)

