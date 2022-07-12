import os
from pathlib import Path
import sys
from PySide6.QtWidgets import *
from windows.AuthWindow import AuthWindow
from windows.UniversalWindow import UniversalWindow
from Debugger import Debugger
from DataManager import DataManager
from FileManager import FileManager


def loadProgram(isOnline):
    global mainWindow
    authWindow.close()
    authWindow.splash.hide()
    authWindow.splash.close()
    
    DataManager().isOnline = isOnline
    FileManager().loadSettings()
    if isOnline:
        FileManager().loadSubjects()
        if authWindow.ui.rememberMe.isChecked():
            FileManager().saveUser(authWindow.ui.loginEdit.text(), DataManager().password)
    mainWindow = UniversalWindow()
    mainWindow.loadWidgets()
    mainWindow.show()

if __name__ == "__main__":
    global authWindow
    Debugger().timer.start()
    app = QApplication([])
    authWindow = AuthWindow()
    authWindow.complete.connect(loadProgram)
    sys.exit(app.exec())
