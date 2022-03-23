import os
from pathlib import Path

from PySide6.QtWidgets import *
from PySide6.QtCore import QFile, qDebug, Qt, QEvent, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon
from FileManager import FileManager
from DataManager import DataManager
from Threads import downloadFileThread
class AssignWindow(QMainWindow):
    refresh = Signal()
    def __init__(self):
        super(AssignWindow, self).__init__(None, Qt.WindowStaysOnTopHint)
        self.ui = None
        self.load_ui()
        self.loadWidgets()
        self.currentPath = []
        self.threads = []
        self.threadFinished = True

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "AssignForm.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        self.setGeometry(self.ui.geometry())
        #self.ui.show()
        ui_file.close()

    def loadWidgets(self):
        self.ui.filesList.installEventFilter(self)
        self.ui.downloadButton.clicked.connect(self.downloadButtonClicked)
        self.ui.openButton.clicked.connect(self.openButtonClicked)
        self.ui.filesList.itemDoubleClicked.connect(self.listItemClicked)

    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self.ui.filesList:
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
                    self.openFile(item)
                elif text == 'Скачать':
                    self.downloadFile(item)
                elif text == 'Удалить':
                    self.deleteFile(item)
                return True
        return super().eventFilter(source, event)

    def listItemClicked(self, item):
        rawPath, file, fileext = DataManager().getRawPath(item.text(), self.currentPath)
        if DataManager().isDownloaded(file['href']):
            self.openFile(item)
        else:
            self.downloadFile(item)

    def downloadButtonClicked(self):
        item = self.ui.filesList.currentItem()
        self.downloadFile(item)

    def downloadFile(self, item):
        if item is None or not self.threadFinished:
            return
        self.threadFinished = False
        self.threads.append(downloadFileThread(item.text(), self.currentPath))
        self.threads[-1].finished.connect(self.finish)
        self.threads[-1].start()
    def finish(self):
        if self.threadFinished:
            return
        self.threadFinished = True
        self.refresh.emit()


    def openButtonClicked(self):
        item = self.ui.filesList.currentItem()
        self.openFile(item)

    def openFile(self, item):
        FileManager().openFile(item.text(), self.currentPath)

    def deleteFile(self, item):
        print(f'Remove {item.text()}')
        FileManager().deleteFile(item.text(), self.currentPath)
        self.refresh.emit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
