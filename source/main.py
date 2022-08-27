import os
from pathlib import Path
import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QGuiApplication
from windows.AuthWindow import AuthWindow
from windows.UniversalWindow import UniversalWindow
from Debugger import Debugger
from DataManager import DataManager
from FileManager import FileManager

def Auth():
    global authWindow
    authWindow = AuthWindow()
    authWindow.complete.connect(loadProgram)
    authWindow.show()
    authWindow.setWindowState(authWindow.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
    authWindow.activateWindow()

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
            if not FileManager().saveUser(authWindow.ui.loginEdit.text(), authWindow.ui.passwordEdit.text()):
                Debugger().throw("FM.saveUser() failed!")
    mainWindow = UniversalWindow()
    mainWindow.exitAccount.connect(Exit)
    mainWindow.loadWidgets()
    mainWindow.show()

def createSplash():
    global splash
    geometry = QGuiApplication.primaryScreen().geometry()
    w, h, = geometry.width(), geometry.height()
    pix = QPixmap('icons/loadingScreen.png')
    w2, h2 = pix.size().width(), pix.size().height()
    k = (w2 * h2) / (w * h) * 1.33
    splash = QSplashScreen(pix.scaled(k * w2, k * h2))
    splash.show()

def main():
    app = QApplication([])
    createSplash()
    Auth()
    splash.hide()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()