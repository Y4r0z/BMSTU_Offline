import os
from pathlib import Path
import sys

from PySide6.QtWidgets import *
from PySide6.QtCore import QFile, qDebug, Qt, QEvent, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon
import requests
from CustomList import *
from DataManager import DataManager
from FileManager import FileManager
from AssignWindow import AssignWindow
from Threads import downloadFileThread, downloadMutex
class CourseWindow(QMainWindow):
    refresh = Signal()
    def __init__(self, main):
        super(CourseWindow, self).__init__(None, Qt.WindowStaysOnTopHint)
        self.ui = None
        self.mainWindow = main
        self.assignWindow = AssignWindow()
        self.assignWindow.hide()
        self.assignWindow.setWindowIcon(FileManager().getIcons()['assign'])
        self.load_ui()
        self.loadWidgets()
        self.lastItemLoaded = None
        self.currentPath = []
        self.threads = []


    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "courseForm.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        #self.ui.show()
        ui_file.close()

    def loadWidgets(self):
        self.ui.activitiesList.installEventFilter(self)
        self.ui.activitiesList.itemDoubleClicked.connect(self.listItemClicked)
        self.assignWindow.refresh.connect(self.openButtonClicked)
        self.ui.openButton.clicked.connect(self.openButtonClicked)

    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self.ui.activitiesList:
            menu = QMenu('Предмет')
            icons = FileManager().getIcons()
            menu.addAction(icons['open'], 'Открыть')
            menu.addAction(icons['download'], 'Скачать')
            menu.addAction(icons['delete'], 'Удалить')
            action = menu.exec(event.globalPos())
            if action:
                item = source.itemAt(event.pos())
                text = action.text()
                if text == 'Открыть':
                    self.listItemClicked(item)
                elif text == 'Скачать':
                    pass
                elif text == 'Удалить':
                    pass
                return True
        return super().eventFilter(source, event)

    def openButtonClicked(self):
        row = self.ui.activitiesList.currentRow()
        item = self.ui.activitiesList.currentItem()
        self.generateFiles(item)
        self.mainWindow.openButtonClicked()
        self.ui.activitiesList.setCurrentRow(row)

    def refreshSignal(self):
        self.listItemClicked(self.lastItemLoaded)
        self.mainWindow.openButtonClicked()

    def listItemClicked(self, item):
        if item is None:
            return
        text = item.text()
        subjects = DataManager().getSubjects()
        for i in subjects:
            if i['text'] != self.windowTitle():
                continue
            for j in i['activities']:
                if j['text'] == text and j['type'] == 'assign':
                    self.generateFiles(item)
                    return
                elif j['text'] == text and j['type'] == 'resource':
                    self.handleResource(j)
                    return


    def generateFiles(self, item):
        if item is None:
            return
        text = item.text()
        self.lastItemLoaded = item
        subjects = DataManager().getSubjects()
        for i in subjects:
            if i['text'] != self.windowTitle():
                continue
            for j in i['activities']:
                if j['text'] == text and j['type'] == 'assign':
                    if j['files'] is None or (len(j['files']) == 0 and not DataManager().isOnline):
                        return
                    list = CustomList(self.assignWindow.ui.filesList)
                    list.clear()
                    if(len(j['files']) == 0 and DataManager().isOnline):
                        j['files'] = DataManager().getFiles(j)
                        if j['files'] is None or len(j['files']) == 0:
                            return
                    for k in j['files']:
                        try:
                            list.addItem(k['text'], k['type'], DataManager().getDownload(k['href']))
                        except Exception as e:
                            list.addItem('Error')
                            print('CourseWindow().listItemClicked() error:')
                            print(e)
                            continue
                    self.assignWindow.setWindowTitle(item.text())
                    self.assignWindow.currentPath = [self.currentPath[0], item.text()]
                    self.assignWindow.show()

    def handleResource(self, file):
        if DataManager().isDownloaded(file['href']):
            if downloadMutex.tryLock():
                FileManager().openFile(file['text'], self.currentPath)
                downloadMutex.unlock()
        else:
            if len(self.threads) > 1:
                n = 0
                for i in self.threads:
                    if i.isRunning: n+=1
                if n > 0:
                    return
            self.threads.append(downloadFileThread(file['text'], self.currentPath))
            self.threads[-1].finished.connect(self.refresh)
            self.threads[-1].start()
            #FileManager().downloadFile(file['text'], self.currentPath)
    def closeEvent(self, event):
        event.ignore()
        self.assignWindow.hide()
        self.hide()

