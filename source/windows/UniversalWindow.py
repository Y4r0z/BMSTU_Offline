from PySide6.QtWidgets import *
from PySide6 import QtCore
from PySide6.QtCore import Qt, QFile, qDebug, QEvent, QSize, Signal

from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon, QPalette, QColor

import os
from pathlib import Path

from FileManager import FileManager
from DataManager import DataManager
from CustomList import CustomList
from windows.settingsWindow import SettingsWindow
from Debugger import Debugger
from Downloader import Downloader, DownloadItem
from Remover import Remover, RemoveItem
from ListItem import ListFile, ListStorage
import Tools
"""
Modes:
0 - Subjects
1 - Assigns
2 - Files
"""
class UniversalWindow(QWidget):
    exitAccount = Signal()
    def __init__(self):
        super(UniversalWindow, self).__init__()
        self.ui = None
        self.load_ui()
        self.mode = 0
        self.currentPath = []
        self.styles = {}
        self.isFilterSaved = True
        self.settingsWindow = SettingsWindow(self)

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "UniversalForm.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        self.setLayout(self.ui.layout())
        self.setGeometry(self.ui.geometry())
        self.setWindowTitle('BMSTU Offline')
        self.setWindowIcon(FileManager().getIcons()['bmstu_small'])
        ui_file.close()

    def loadWidgets(self):
        self.move(QApplication.primaryScreen().availableGeometry().center() - self.rect().center())
        filter = DataManager().getSettings()['filter']
        if not filter is None and len(filter) > 0:
            self.ui.filterEdit.setText(filter.lower())
            self.generateSubjects(filter.lower())
        else:
            self.generateSubjects()

        icon = FileManager().getIcons()['unsaved']
        self.ui.saveFilterButton.setIcon(icon)
        self.ui.saveFilterButton.setIconSize(QSize(22, 22))

        self.ui.list.installEventFilter(self)
        self.ui.filterEdit.textChanged.connect(self.filterChanged)
        self.ui.list.itemDoubleClicked.connect(self.listItemDoubleClicked)
        self.ui.beginTab.clicked.connect(self.beginTabClicked)
        self.ui.courseTab.clicked.connect(self.courseTabClicked)
        self.ui.saveFilterButton.clicked.connect(self.saveFilter)
        self.ui.settingsButton.clicked.connect(self.settingsButtonClicked)

        self.styles['beginTab'] = self.ui.beginTab.styleSheet()
        self.styles['courseTab'] = self.ui.courseTab.styleSheet()
        self.styles['assignTab'] = self.ui.assignTab.styleSheet()

        self.changeTabs()

    def closeEvent(self, event):
        self.hide()
        FileManager().saveSubjects()
        DataManager().endSession()
        Debugger().endSession()
        QApplication.quit()

    def refresh(self, reset = False):
        if not reset:
            lst = CustomList(self.ui.list)
            lst.update()
            return
        scrollBar = self.ui.list.verticalScrollBar()
        scrollRange = scrollBar.maximum()
        scrollValue = scrollBar.sliderPosition()
        row = self.ui.list.currentRow()
        if self.mode == 0:
            self.generateSubjects(DataManager().getSettings()['filter'])
        elif self.mode == 1:
            listItem = DataManager().findByName(self.currentPath[0])
            self.generateActivities(listItem)
        elif self.mode == 2:
            listItem = DataManager().findByName(self.currentPath[-1], [self.currentPath[0]])
            self.generateFiles(listItem)
        if scrollRange == scrollBar.maximum():
            scrollBar.setSliderPosition(scrollValue)
            row = self.ui.list.setCurrentRow(row)



    def keyPressEvent(self, event):
        if event.key() == 16777220 or event.key() == 16777236:
            self.openClicked(self.ui.list.currentItem())
        elif event.key() == 16777216 or event.key() == 16777234:
            if self.mode == 0:
                return
            self.mode -= 1
            self.currentPath.pop()
            self.refresh(reset = True)
            self.changeTabs()

    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self.ui.list:
            menu = QMenu('Предмет')
            icons = FileManager().getIcons()
            item = source.itemAt(event.pos())
            if item is None:
                return
            obj = DataManager().find(str(item.data(Qt.UserRole)))
            if obj.locked:
                return
            if len(self.ui.list.selectedItems()) == 1:
                menu.addAction(icons['open'], 'Открыть')
                if obj.Signature == 'file':
                    if obj['download'] == 0 and DataManager().isOnline:
                        menu.addAction(icons['download'], 'Скачать')
                    if obj['download'] == 100:
                        menu.addAction(icons['delete'], 'Удалить')
                else:
                    if obj['download'] < 100 and DataManager().isOnline:
                        menu.addAction(icons['download'], 'Скачать всё')
                    if obj['download'] > 0:
                        menu.addAction(icons['delete'], 'Удалить всё')
            elif len(self.ui.list.selectedItems()) > 1:
                if DataManager().isOnline:
                    menu.addAction(icons['download'], 'Скачать всё')
                menu.addAction(icons['delete'], 'Удалить всё')
            action = menu.exec(event.globalPos())
            if action:
                text = action.text()
                if len(self.ui.list.selectedItems()) == 1:
                    if text == 'Открыть':
                        self.openClicked(item)
                    if text == 'Скачать':
                        self.downloadItem(obj)
                    elif text == 'Удалить':
                        self.deleteItem(obj)
                    elif text == 'Скачать всё':
                        self.downloadItem(obj)
                    elif text == 'Удалить всё':
                        self.deleteItem(obj)
                elif len(self.ui.list.selectedItems()) > 1:
                    items = self.ui.list.selectedItems()
                    for i in items:
                        find = DataManager().find(str(i.data(Qt.UserRole)))
                        if find is None: continue
                        if text == 'Скачать всё':
                            self.downloadItem(find)
                        elif text == 'Удалить всё':
                            self.deleteItem(find)
            return True
        return super().eventFilter(source, event)

    def filterChanged(self, text):
        if self.mode != 0:
            return
        DataManager().getSettings()['filter'] = text
        newList = []
        self.generateSubjects(text.lower())
        if self.isFilterSaved:
            self.isFilterSaved = False
            icon = FileManager().getIcons()['saved']
            self.ui.saveFilterButton.setIcon(icon)
            self.ui.saveFilterButton.setIconSize(QSize(22, 22))

    def listItemDoubleClicked(self, item):
        self.openClicked(item)


    def beginTabClicked(self):
        if self.mode == 0:
            self.refresh(True)
            return
        self.currentPath = []
        self.mode = 0
        self.generateSubjects(DataManager().getSettings()['filter'].lower())
        self.changeTabs()

    def courseTabClicked(self):
        if self.mode == 1:
            return
        text = self.currentPath[0]
        self.currentPath.pop(-1)
        self.mode = 1
        listItem = DataManager().findByName(text)
        self.generateActivities(listItem)
        self.changeTabs()


    def openClicked(self, item):
        listItem = DataManager().find(str(item.data(Qt.UserRole)))
        if listItem.locked:
            return
        if self.tryOpenFile(listItem):
            return
        if listItem.parent is None:
            if self.generateActivities(listItem):
                self.mode = 1
        elif listItem.parent.parent is None:
            if self.generateFiles(listItem):
                self.mode = 2
        self.changeTabs()

    def deleteItem(self, file):
        if file['download'] != 0:
            item = RemoveItem(file)
            self.refresh()
            item.complete.connect(self.refresh)
            item.update.connect(self.refresh)
            Remover().push(item)
            self.refresh()
        else:
            Debugger().throw('uw.deleteItem() - The file is not downlaoded!')
            return 
        
    def tryOpenFile(self, file):
        if file is None or file['type'] in ListStorage.Types:
            return False
        if file['download'] == 100:
            FileManager().openFile(file)
        else:
            self.downloadItem(file)
        return True

    def settingsButtonClicked(self):
        self.settingsWindow.show()
        self.settingsWindow.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.settingsWindow.activateWindow()

    def generateSubjects(self, filter = None):
        size = self.ui.list.count()
        row = self.ui.list.currentRow()
        cList = CustomList(self.ui.list)
        cList.clear()
        subjects = DataManager().getSubjects()
        self.ui.label.setText('Мои курсы')
        if filter is None:        
            for i in subjects:
                cList.addItem(i)
        else:
            for i in subjects:
                if Tools.stringCmp(i.text, filter):
                    cList.addItem(i)
        if self.ui.list.count() > 0:
            if size == self.ui.list.count():
                self.ui.list.setCurrentRow(row)
            else:
                self.ui.list.setCurrentRow(0)

    def generateActivities(self, listItem):
        activities = DataManager().getActivities(listItem)
        if len(activities) == 0: return False
        list = CustomList(self.ui.list)
        list.clear()
        self.ui.label.setText(listItem['text'])
        self.currentPath = [listItem['text']]
        self.mode = 1
        for i in activities:
            try:
                list.addItem(i)
            except Exception as e:
                Debugger().throw("UniversalWindow.generateActivities error:\n" + str(e))
                list.addItem('Error')
                continue
        if self.ui.list.count() > 0:
            self.ui.list.setCurrentRow(0)
        return True

    def generateFiles(self, listItem):
        if listItem['type'] not in ['assign', 'folder']:
            return False
        if len(listItem['files']) == 0 and DataManager().isOnline:
            listItem.set(DataManager().getFiles(listItem))
            if listItem['files'] is None or len(listItem['files']) == 0:
                return False
        elif len(listItem['files']) == 0 and not DataManager().isOnline:
            return False
        list = CustomList(self.ui.list)
        list.clear()
        for i in listItem['files']:
            try:
                list.addItem(i)
            except Exception as e:
                list.addItem('Error')
                Debugger().throw('UniversalWindow().generateFiles() error:\n' + str(e))
                continue
        self.ui.label.setText(listItem.text)
        self.currentPath = [listItem.parent.text, listItem.text]
        if self.ui.list.count() > 0:
            self.ui.list.setCurrentRow(0)
        return True

    def changeTabs(self):
        begin = self.ui.beginTab
        course = self.ui.courseTab
        assign = self.ui.assignTab
        active = 'background-color:rgb(230, 230, 230);}'
        inactive = 'background-color:rgb(210, 210, 210);}'
        inactive2 = 'background-color:rgb(190, 190, 190);}'
        path = self.currentPath
        if len(path) == 0:
            course.hide()
            assign.hide()
            begin.setStyleSheet(self.styles['beginTab'] + \
            'QPushButton{' + active + 'QPushButton::hover{' + active)
            self.ui.filterEdit.setEnabled(True)
            self.ui.saveFilterButton.setEnabled(True)
        elif len(path) == 1:
            assign.hide()
            begin.setStyleSheet(self.styles['beginTab'] + \
            'QPushButton{' + inactive + 'QPushButton::hover{' + active)
            course.setStyleSheet(self.styles['courseTab'] + \
            'QPushButton{' + active + 'QPushButton::hover{' + active)
            course.setText(self.currentPath[0])
            self.setTabWidth()
            self.ui.filterEdit.setEnabled(False)
            self.ui.saveFilterButton.setEnabled(False)
            course.show()
        else:
            course.setStyleSheet(self.styles['courseTab'] + \
            'QPushButton{' + inactive + 'QPushButton::hover{' + active)
            begin.setStyleSheet(self.styles['beginTab'] + \
            'QPushButton{' + inactive2 + 'QPushButton::hover{' + active)
            course.setText(self.currentPath[0])
            assign.setText(self.currentPath[1])
            assign.resize(20 + len(assign.text()) * 8, assign.height())
            self.setTabWidth()
            self.ui.filterEdit.setEnabled(False)
            self.ui.saveFilterButton.setEnabled(False)
            assign.show()
            course.show()

    def setTabWidth(self):
        maxWidth = 465
        font = 8
        course = self.ui.courseTab
        assign = self.ui.assignTab
        size = len(course.text()) * font
        if size > maxWidth: size = maxWidth

        course.resize(size, course.height())
        assign.move(course.pos().x() + size, assign.pos().y())

    def saveFilter(self):
        icon = FileManager().getIcons()['unsaved']
        self.ui.saveFilterButton.setIcon(icon)
        self.ui.saveFilterButton.setIconSize(QSize(22, 22))
        self.isFilterSaved = True
        FileManager().saveSettings()

    def downloadItem(self, file):
        if not DataManager().isOnline:
            Debugger().throw("UniversalWindow.downloadItem. Program is not online!")
            return
        item = DownloadItem(file)
        self.refresh()
        item.complete.connect(self.refresh)
        item.update.connect(self.refresh)
        Downloader().push(item)  
    





