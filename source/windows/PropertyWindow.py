import os
from pathlib import Path
import sys

from PySide6.QtWidgets import *
from PySide6.QtCore import QFile, qDebug, Qt, QSize, QPoint
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon, QMovie, QCursor
from FileManager import FileManager
from DataManager import DataManager
import Tools

class PropertyWindow(QWidget):
    def __init__(self, item):
        super(PropertyWindow, self).__init__()
        self.item = item
        self.ui = None
        self.load_ui()
        self.loadWidgets()

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "PropertyForm.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        self.setGeometry(self.ui.geometry())
        self.setLayout(self.ui.layout())
        self.setWindowTitle('Свойства')
        self.setWindowIcon(FileManager().getIcons()['bmstu'])
        ui_file.close()

    def loadWidgets(self):
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        res = QApplication.primaryScreen().geometry()
        cursor = QCursor.pos()
        size = self.size()
        newPos = QPoint(cursor.x() - size.width()/2, cursor.y() - size.height()/2)
        newPos.setX(0 if newPos.x() < 0 else newPos.x()) 
        newPos.setY(0 if newPos.y() < 0 else newPos.y())
        newPos.setX(res.width() - size.width() if (newPos.x() + size.width()) > res.width() else newPos.x())
        newPos.setY(res.height() - size.height() if (newPos.y() + size.height()) > res.height() else newPos.y())
        self.move(newPos)

        self.generalTab()
        if (self.item.type == 'assign' or self.item.Signature == 'file') and self.item.description is not None:
            self.assignTab()
        else:
            tab = self.ui.tabWidget.indexOf(self.ui.tabWidget.findChild(QWidget, 'assign'))
            self.ui.tabWidget.removeTab(tab)
        if self.item.Signature == 'file' and len(self.item.path) > 0 and os.path.exists(DataManager().listToPath(self.item.path)):
            self.fileTab()
        else:
            tab = self.ui.tabWidget.indexOf(self.ui.tabWidget.findChild(QWidget, 'file'))
            self.ui.tabWidget.removeTab(tab)

        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()

    def generalTab(self):
        ui = self.ui.tabWidget.findChild(QWidget, 'general')
        icon = ui.findChild(QLabel, 'icon')
        icon.setPixmap(FileManager().getIcons().getItemIcon(self.item).pixmap(32,32))
        name = ui.findChild(QLineEdit, 'name')
        name.setText(self.item.text)
        name.setCursorPosition(0)
    
    def assignTab(self):
        ui = self.ui.tabWidget.findChild(QWidget, 'assign')
        task = ui.findChild(QTextEdit, 'task')
        task.setText(self.item.description)
    
    def fileTab(self):
        ui = self.ui.tabWidget.findChild(QWidget, 'file')
        size = ui.findChild(QLabel, 'size')
        path = ui.findChild(QLineEdit, 'path')
        openButton = ui.findChild(QPushButton, 'openButton')
        openButton.setIcon(FileManager().getIcons()['open'])
        openButton.clicked.connect(self.openFile)
        path.setText(os.path.abspath(DataManager().listToPath(self.item.path)))
        path.setCursorPosition(0)
        size.setText(Tools.sizeof_fmt(os.path.getsize(DataManager().listToPath(self.item.path))))
        
    
    def openFile(self):
        FileManager().openFile(self.item)

    def closeEvent(self, event):
        pass

    