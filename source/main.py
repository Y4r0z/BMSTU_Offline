import os
from pathlib import Path
import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap
from windows.AuthWindow import AuthWindow
from windows.UniversalWindow import UniversalWindow
from Debugger import Debugger
from DataManager import DataManager
from FileManager import FileManager

def Auth():
    global authWindow
    authWindow = AuthWindow()
    authWindow.complete.connect(loadProgram)

def Exit():
    global mainWindow
    mainWindow.hide()
    DataManager().subjects.clear()
    mainWindow.settingsWindow.hide()
    Auth()


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
    mainWindow.exitAccount.connect(Exit)
    mainWindow.loadWidgets()
    mainWindow.show()



if __name__ == "__main__":
    app = QApplication([])
    splash = QSplashScreen(QPixmap('icons/loadingScreen.png'))
    splash.show()
    Auth()
    splash.hide()
    sys.exit(app.exec())
