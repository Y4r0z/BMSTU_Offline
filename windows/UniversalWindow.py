from PySide6.QtWidgets import *
from PySide6 import QtCore
from PySide6.QtCore import Qt, QFile, qDebug, QEvent, QSize

from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon, QPalette, QColor

import os
from pathlib import Path

from FileManager import FileManager
from DataManager import DataManager
from CustomList import CustomList
from Threads import *
from windows.settingsWindow import SettingsWindow
from Debugger import Debugger
from Downloader import Downloader, DownloadItem
from ListItem import ListFile, ListStorage

"""
Modes:
0 - Subjects
1 - Assigns
2 - Files
"""
class UniversalWindow(QWidget):
    def __init__(self):
        super(UniversalWindow, self).__init__()
        self.ui = None
        self.load_ui()
        self.mode = 0
        self.currentPath = []
        self.styles = {}
        self.isFilterSaved = True
        self.threads = []
        self.threadState = {'downloadFinished': True, 'initFinished': True}
        self.initiatedSubjects = {}

        self.settingsWindow = SettingsWindow(self)

        self.clickedRow = -1

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "UniversalForm.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        self.setLayout(self.ui.layout())
        self.setGeometry(self.ui.geometry())
        self.setWindowTitle('BMSTU Offline')
        self.setWindowIcon(FileManager().getIcons()['bmstu'])
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
        self.ui.list.itemPressed.connect(self.listItemClicked)
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
        DataManager().endSession()
        Debugger().endSession()
        QApplication.quit()

    def refresh(self):
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
            self.refresh()
            self.changeTabs()

    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self.ui.list:
            menu = QMenu('Предмет')
            icons = FileManager().getIcons()
            item = source.itemAt(event.pos())
            if item is None:
                return
            obj = listItem = DataManager().find(str(item.data(Qt.UserRole)))
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

            action = menu.exec(event.globalPos())
            if action:
                text = action.text()
                if text == 'Открыть':
                    self.openClicked(item)
                if text == 'Скачать':
                    self.downloadAll(obj)
                elif text == 'Удалить':
                    self.deleteFile(obj)
                elif text == 'Скачать всё':
                    self.downloadAll(obj)
                elif text == 'Удалить всё':
                    self.deleteAll(obj)
            return True
        return super().eventFilter(source, event)

    def filterChanged(self, text):
        if self.mode != 0:
            return
        DataManager().getSettings()['filter'] = text
        self.generateSubjects(text.lower())
        if self.isFilterSaved:
            self.isFilterSaved = False
            icon = FileManager().getIcons()['saved']
            self.ui.saveFilterButton.setIcon(icon)
            self.ui.saveFilterButton.setIconSize(QSize(22, 22))

    def listItemDoubleClicked(self, item):
        self.openClicked(item)

    def listItemClicked(self, item):
        if self.mode != 0 or self.threadState['initFinished'] == True:
            return
        if self.clickedRow == self.ui.list.currentRow():
            self.openClicked(item)
        self.clickedRow = self.ui.list.currentRow()


    def beginTabClicked(self):
        if self.mode == 0:
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
        listItem = listItem = DataManager().find(str(item.data(Qt.UserRole)))
        if self.mode != 0 and self.tryOpenFile(listItem):
            return
        if self.mode == 0:
            for i in DataManager().getSubjects():
                if item.text() == i['text'] and not self.threadState['initFinished'] and self.initiatedSubjects[i['href']] != 100:
                    return
            if self.generateActivities(listItem):
                self.mode = 1
        elif self.mode == 1:
            if self.generateFiles(listItem):
                self.mode = 2
        self.changeTabs()

    def deleteFile(self, item):
        if item.Signature != 'file':
            Debugger().throw("uw.deleteFile() wrong item signature!")
        if item['download'] == 100:
            FileManager().deleteFile(item)
            self.refresh()
        else:
            Debugger().throw('UniversalWindow().deleteFileClicked() - The file is not downlaoded!')
            return
    
    def deleteAll(self, item):
        if item['download'] == 0: return
        if item.Signature == 'file':
            self.deleteFile(item)
            return
        self.loadItem(item)
        files = []
        ListFile.GetFiles(item, files)
        for i in files:
            self.deleteAll(i)
        
    def tryOpenFile(self, file):
        if file is None or file['type'] in ListStorage.Types:
            return False
        if file['download'] == 100:
            FileManager().openFile(file)
        else:
            self.downloadFile(file)
        return True

    def downloadAll(self, item):
        if not DataManager().isOnline: return
        if item['download'] == 100: return
        if item.Signature == 'file':
            self.downloadFile(item)
            return
        self.loadItem(item)
        files = []
        ListFile.GetFiles(item, files)
        for i in files:
            self.downloadAll(i)

    def settingsButtonClicked(self):
        self.settingsWindow.show()

    def generateSubjects(self, filter = None):
        size = self.ui.list.count()
        row = self.ui.list.currentRow()
        cList = CustomList(self.ui.list)
        cList.clear()
        subjects = DataManager().getSubjects()
        self.ui.label.setText('Мои курсы')
        state = {}
        if not self.threadState['initFinished']:
            state = self.initiatedSubjects
        else:
            for i in subjects:
                state[i['href']] = None
        if filter is None:        
            for i in subjects:
                cList.addItem(i, {'courseState':state[i['href']]})
        else:
            CyrillicTranslateAlphabet = dict(zip(list("qwertyuiop[]asdfghjkl;'zxcvbnm,."), list('йцукенгшщзхъфывапролджэячсмитьбю')))
            find = False
            for i in subjects:
                if i['text'].lower().find(filter) != -1:
                    find = True
                    cList.addItem(i, {'courseState':state[i['href']]})
            if not find:
                text = []
                for i in filter:
                    if i in CyrillicTranslateAlphabet.keys():
                        text.append(CyrillicTranslateAlphabet[i])
                    else:
                        text.append(i)
                for i in subjects:
                    if i['text'].lower().find(''.join(text)) != -1:
                        cList.addItem(i, {'courseState':state[i['href']]})
        if self.ui.list.count() > 0:
            if size == self.ui.list.count():
                self.ui.list.setCurrentRow(row)
            else:
                self.ui.list.setCurrentRow(0)
        self.clickedRow = self.ui.list.currentRow()

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
        self.currentPath = [self.currentPath[0], listItem.text]
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
            assign.setText(self.currentPath[1])
            assign.resize(20 + len(assign.text()) * 8, assign.height())
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
        FileManager().saveSettings()

    def downloadFile(self, file):
        if not DataManager().isOnline:
            Debugger().throw("UniversalWindow.downloadFile. Program is not online!")
            return
        item = DownloadItem(file)
        item.complete.connect(self.refresh)
        Downloader().push(item)
  
    def initiateSubjects(self):
        if self.threadState['downloadFinished'] and self.threadState['initFinished']:
            self.ui.list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.settingsWindow.ui.saveSubjects.hide()
            self.threadState['initFinished'] = False
            self.threads.append(InitSubjectsThread(self.initiatedSubjects))
            self.threads[-1].finished.connect(self.finishInitSubjects)
            self.threads[-1].clk.connect(self.clkInitSubjects)
            self.threads[-1].start()
            return


    def clkInitSubjects(self, progress):
        self.refresh()

    def finishInitSubjects(self):
        if self.threadState['initFinished']:
            return
        self.ui.list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.threadState['initFinished'] = True
        self.settingsWindow.ui.saveSubjects.show()
        FileManager().saveSubjects()
    
    def loadItem(self, item):
        if self.mode == 0:
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









