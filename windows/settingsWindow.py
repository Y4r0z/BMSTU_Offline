from PySide6.QtWidgets import *
from PySide6.QtCore import QFile, qDebug, QEvent, QSize
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon, QPalette, QColor

import os
from pathlib import Path

from FileManager import FileManager
from DataManager import DataManager
from Debugger import Debugger

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
        self.setGeometry(self.ui.geometry())
        self.setLayout(self.ui.layout())
        self.setWindowTitle('Settings')
        self.setWindowIcon(FileManager().getIcons()['settings'])
        ui_file.close()

    def loadWidgets(self):
        ui = self.ui;
        ui.saveSubjects.clicked.connect(self.saveSubjectsClicked);

    def saveSubjectsClicked(self):
        if DataManager().isOnline:
            self.mainWindow.initiateSubjects()
        else:
            Debugger().throw("SettingsWindow.saveSubjects() error. Can't save subjects in offline mode.")




    def closeEvent(self, event):
        event.ignore()
        self.hide()
