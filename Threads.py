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


class InitSubjectsThread(QThread):
    clk = Signal(float)

    def __init__(self, initState):
        super().__init__()
        self.progress = 0
        self.initState = initState

    def run(self):
        if not DataManager().isOnline:
            return
        cnt = 0
        subs = DataManager().getSubjects()
        if len(self.initState.keys()) == 0:
            for i in subs:
                self.initState[i['href']] = 0
                self.clk.emit(0)
        size = len(subs)
        for i in subs:
            #self.initState[i['href']] = 50
            acts = DataManager().getActivities(i)
            n = 0
            for j in acts:
                if j['type'] in ['assign', 'folder']:
                    j.set(DataManager().getFiles(j))
                n += 1
                self.initState[i['href']] = (n / len(acts)) * 100
                self.clk.emit(self.progress)
            cnt += 1
            self.progress = cnt/size * 100
            self.initState[i['href']] = 100
            self.clk.emit(self.progress)

class ProgressBarThread(QThread):
    clk = Signal(int)
    def __init__(self, parent = None):
        super().__init__()

    def run(self):
        if DataManager().isOnline:
            progress = 0
            cnt = 0
            subs = DataManager().getSubjects()
            size = len(subs)
            for i in subs:
                acts = DataManager().getActivities(i['id'])
                self.fileThreads = []
                n = 0
                for j in acts:
                    if j['files'] is None:
                        continue
                    self.fileThreads.append(setFilesThread(href = j['href'], storage = j))
                    self.fileThreads[n].start()
                    n+=1
                k = 0
                threadsCnt = len(self.fileThreads)
                while True:
                    for t in self.fileThreads:
                        if not t.isRunning: k+=1
                    if k == threadsCnt: break
                    k = 0
                    QThread.msleep(1)
                cnt += 1
                progress = (cnt/size) * 95
                self.clk.emit(progress)
            #FileManager().saveSubjects()
            progress = 100
            QThread.msleep(500)
            self.clk.emit(progress)
        self.stop()

    def stop(self):
        self.finished.emit()


filesMutex = QMutex()
class setFilesThread(QThread):
    def __init__(self, assign):
        super().__init__()
        self.assign = assign
        self.isRunning = True
        self.session = DataManager().session

    def run(self):
        files = DataManager().getFiles(self.assign)
        while True:
            if filesMutex.tryLock():
                self.assign['files'] = files
                filesMutex.unlock()
                break
            QThread.msleep(1)
        self.stop()

    def stop(self):
        self.isRunning = False
        #self.finished.emit()


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


