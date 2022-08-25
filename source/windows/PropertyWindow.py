import os
from pathlib import Path
import sys

from PySide6.QtWidgets import *
from PySide6.QtCore import QFile, qDebug, Qt, QSize, QPoint
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon, QMovie, QCursor
from FileManager import FileManager
from DataManager import DataManager

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

        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()

    def generalTab(self):
        ui = self.ui.tabWidget.findChild(QWidget, 'general')
        icon = ui.findChild(QLabel, 'icon')
        icon.setPixmap(FileManager().getIcons()[self.item.type].pixmap(32,32))
        name = ui.findChild(QLineEdit, 'name')
        name.setText(self.item.text)
        name.setCursorPosition(0)

    def closeEvent(self, event):
        pass