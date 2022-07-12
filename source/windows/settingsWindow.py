from PySide6.QtWidgets import *
from PySide6.QtCore import QFile, qDebug, QEvent, QSize
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon, QPalette, QColor

import os
from pathlib import Path

from FileManager import FileManager
from DataManager import DataManager
from Debugger import Debugger
from ListItem import ListFile
from CustomList import CustomList

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
        cList = CustomList(self.mainWindow.ui.list)
        cList.clear()
        for i in filteredList:
            path = []
            if i.parent is None:
                pass
            elif i.parent.parent is None:
                path = [i.parent.text.split(',')[0]]
            else:
                path = [i.parent.parent.text.split(',')[0], i.parent.text]
            if len(path) == 0:
                cList.addItem(i)
            else:
                path = '\\'.join(i for i in path)
                cList.addItem(i)
                for j in range(self.mainWindow.ui.list.count()):
                    item = self.mainWindow.ui.list.item(j)
                    if item.text() != i.text: continue
                    item.setText(path + '\\' + i.text)

                    
                

        

    def saveSubjectsClicked(self):
        FileManager().saveSubjects()


    def closeEvent(self, event):
        event.ignore()
        self.hide()
