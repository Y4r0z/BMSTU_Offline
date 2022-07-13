from PySide6.QtWidgets import *
from PySide6.QtCore import QFile, qDebug, QEvent, QSize, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon, QPalette, QColor

import os
from pathlib import Path

from FileManager import FileManager
from DataManager import DataManager
from Debugger import Debugger
from ListItem import ListFile
from CustomList import CustomList
import Threads

class SettingsWindow(QWidget):
    def __init__(self, mainwindow):
        super(SettingsWindow, self).__init__()
        self.ui = None
        self.mainWindow = mainwindow
        self.load_ui()
        self.loadWidgets()

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "SettingsForm.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())
        self.setLayout(self.ui.layout())
        self.setWindowTitle('Settings')
        self.setWindowIcon(FileManager().getIcons()['settings'])

    def loadWidgets(self):
        ui = self.ui
        ui.saveSubjects.clicked.connect(self.saveSubjectsClicked)
        ui.exitAccountButton.clicked.connect(self.mainWindow.exitAccount)
        ui.findButton.clicked.connect(self.findButtonClicked)
        self.addItems()
    
    def addItems(self):
        box = self.ui.typeComboBox
        box.addItem('Все')
        box.addItem('Курс')
        box.addItem('Задание')
        box.addItem('Файл')
        box.setItemIcon(0, FileManager().getIcons()['unknown'])
        box.setItemIcon(1, FileManager().getIcons()['course'])
        box.setItemIcon(2, FileManager().getIcons()['assign'])
        box.setItemIcon(3, FileManager().getIcons()['doc'])
        box.setCurrentIndex(0)

    def findButtonClicked(self):
        find = self.ui.findEdit.text().lower()
        itype = self.ui.typeComboBox.currentText()
        if itype == 'Все':
            itype = None
        elif itype == 'Курс':
            itype = 'course'
        elif itype == 'Задание':
            itype = 'assign'
        elif itype == 'Файл':
            itype = 'file'
        subjects = DataManager().getSubjects()
        findedList = []
        for i in subjects:
            ListFile.findByName(find, i, findedList)
        filteredList = []
        for i in findedList:
            if itype is None:
                filteredList.append(i)
                continue
            if itype == 'course' and i.type == 'course':
                filteredList.append(i)
            elif itype == 'assign' and i.type == 'assign':
                filteredList.append(i)
            elif itype == 'file' and i.Signature == 'file':
                filteredList.append(i)
            else: continue
        if len(filteredList) == 0:
            return
        self.mainWindow.mode = 0
        self.mainWindow.currentPath.clear()
        self.mainWindow.refresh(True)
        self.mainWindow.changeTabs()
        oList = self.mainWindow.ui.list
        cList = CustomList(oList)
        cList.clear()
        lastCourse = 'None'
        lastAssign = 'None'
        for i in filteredList:
            cList.addItem(i, lowPerfomance = True)
        for i in range(oList.count()):
            item = oList.item(i)
            listItem = DataManager().find(str(item.data(Qt.UserRole)))
            path = []
            DataManager().getAllParents(listItem, path)
            if self.ui.addSpacesCheck.checkState():
                path.append(listItem.text)
                if lastCourse not in path:
                    lastCourse = path[0]
                if lastAssign not in path[0] and len(path) > 1:
                    lastAssign = path[1]
                path.pop(-1)
                if lastCourse in path:
                    path[0] = '  '
                if lastAssign in path:
                    path[1] = '      '
            else:
                for i in range(len(path)):
                    path[i] = path[i] + '\\'
            item.setText(''.join(path) + listItem.text)
        items = []
        listItems = []     
        for i in range(oList.count()):
            item = oList.item(i)
            listItem = DataManager().find(str(item.data(Qt.UserRole)))
            items.append(item)
            listItems.append(listItem)
        self.thread = Threads.setWigets(items, listItems, CustomList(oList))
        self.thread.run()


    def saveSubjectsClicked(self):
        FileManager().saveSubjects()


    def closeEvent(self, event):
        event.ignore()
        self.hide()
