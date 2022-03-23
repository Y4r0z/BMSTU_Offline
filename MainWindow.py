# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
import requests

from PySide6.QtWidgets import *
from PySide6.QtCore import QFile, qDebug, QEvent
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon

from CustomList import *
from DataManager import DataManager
from CourseWindow import *
from FileManager import FileManager
from Threads import *
from FileThread import *
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = None
        #self.loadWidgets()
        self.courseWindow = CourseWindow(self)
        self.courseWindow.setGeometry(self.courseWindow.ui.geometry())
        self.courseWindow.hide()
        self.load_ui()
        self.saveThread = None

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "mainForm.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        #self.ui.show()
        self.setGeometry(self.ui.geometry())
        self.setWindowTitle('BMSTU Offline.')
        self.setWindowIcon(FileManager().getIcons()['bmstu'])
        self.courseWindow.setWindowIcon(FileManager().getIcons()['course'])
        ui_file.close()

    def loadWidgets(self):
        #FileManager().loadSubjects()
        filter = DataManager().getSettings()['filter']
        if not filter is None and len(filter) > 0:
            self.ui.filterEdit.setText(filter.lower())
            self.generateSubjects(filter.lower())
        else:
            self.generateSubjects()

        self.ui.subjectsList.installEventFilter(self)
        self.ui.subjectsList.itemDoubleClicked.connect(self.listItemClicked)
        self.ui.saveButton.clicked.connect(self.saveButtonClicked)
        self.ui.openButton.clicked.connect(self.openButtonClicked)
        self.ui.filterEdit.textChanged.connect(self.filterChanged)
        self.ui.saveFilterButton.clicked.connect(self.saveFilter)
        self.courseWindow.refresh.connect(self.openButtonClicked)

    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self.ui.subjectsList:
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
                    self.generateActivities(item)
                elif text == 'Скачать':
                    pass
                elif text == 'Удалить':
                    pass
            return True
        return super().eventFilter(source, event)

    def saveProgressChanged(self, progress):
        self.ui.saveBar.setValue(progress)

    def saveButtonClicked(self):
        self.ui.saveButton.setEnabled(False)
        self.saveThread = ProgressBarThread()
        self.saveThread.clk.connect(self.saveProgressChanged)
        self.saveThread.finished.connect(self.enableSaveButton)
        self.saveThread.start()

    def enableSaveButton(self):
        self.ui.saveButton.setEnabled(True)
        self.ui.saveBar.setValue(0)

    def listItemClicked(self, item):
        self.generateActivities(item)

    def openButtonClicked(self):
        item = self.ui.subjectsList.currentItem()
        self.generateActivities(item)

    def generateSubjects(self, filter = None):
        list = CustomList(self.ui.subjectsList)
        list.clear()
        subjects = DataManager().getSubjects()
        if filter is None:
            for i in subjects:
                list.addItem(i['text'], 'course')
        else:
            for i in subjects:
                if i['text'].lower().find(filter) != -1:
                    list.addItem(i['text'], 'course')


    def generateActivities(self, item):
        subjects = DataManager().getSubjects()
        for i in subjects:
            if i['text'] == item.text():
                list = CustomList(self.courseWindow.ui.activitiesList)
                list.clear()
                acts = DataManager().getActivities(i['id'])
                if len(acts) == 0:
                    return
                self.courseWindow.setWindowTitle(i['text'])
                self.courseWindow.currentPath = [i['text']]
                self.courseWindow.show()
                for j in acts:
                    try:
                        list.addItem(j['text'], j['type'], DataManager().getDownload(j['href']))
                    except Exception as e:
                        list.addItem('Error')
                        print(e)
                        continue
    def filterChanged(self, text):
        DataManager().getSettings()['filter'] = text
        self.generateSubjects(text.lower())

    def saveFilter(self):
        FileManager().saveSettings()

    def closeEvent(self, event):
        self.settingsWindow.ui.close()
        DataManager().endSession()

