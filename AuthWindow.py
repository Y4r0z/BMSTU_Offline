import os
from pathlib import Path
import sys

from PySide6.QtWidgets import *
from PySide6.QtCore import QFile, qDebug, Qt, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon
from FileManager import FileManager
from DataManager import DataManager
from Threads import LoginThread
from SplashScreen import SplashScreen

class AuthWindow(QMainWindow):

    def __init__(self, window):
        super(AuthWindow, self).__init__()
        window.hide()
        self.mainWindow = window
        self.ui = None
        self.load_ui()
        self.loadWidgets()

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "AuthForm.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        self.setGeometry(self.ui.geometry())
        #self.ui.show()
        self.show()
        self.setWindowTitle('Авторизация BMSTU')
        self.setWindowIcon(FileManager().getIcons()['bmstu'])
        ui_file.close()

    def loadWidgets(self):
        self.move(QApplication.primaryScreen().availableGeometry().center() - self.rect().center())
        if FileManager().loadUser():
            self.ui.loginEdit.setText(DataManager().username)
            self.ui.passwordEdit.setText(DataManager().password)
        self.ui.offlineButton.clicked.connect(self.authOffline)
        self.ui.onlineButton.clicked.connect(self.authOnline)
        self.ui.Fields.setAlignment(Qt.AlignCenter)
        self.ui.Buttons.setAlignment(Qt.AlignCenter)
        self.ui.Label.setAlignment(Qt.AlignCenter)

        self.splash = SplashScreen(self)

    def closeEvent(self, event):
        DataManager().endSession()

    def authOffline(self):
        if FileManager().loadSubjects():
            FileManager().loadSettings()
            FileManager().loadDownloads()
            DataManager().isOnline = False
            self.mainWindow.loadWidgets()
            self.mainWindow.show()
            self.hide()
            #self.mainWindow.ui.saveButton.setEnabled(False)
            #self.mainWindow.ui.saveButton.hide()
            #self.mainWindow.ui.saveBar.hide()
        else:
            QApplication.setQuitOnLastWindowClosed(False);
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText('Не удалось войти в автономном режиме!')
            msg.setInformativeText('Возможно вы ни разу не входили в онлайн, чтобы сохранить данные для автономного режима.')
            msg.setWindowTitle('Автономный режим')
            msg.exec()
            QApplication.setQuitOnLastWindowClosed(True);

    def authOnline(self):
        self.hide()
        self.splash.run()
        login = self.ui.loginEdit.text()
        password = self.ui.passwordEdit.text()
        self.thread = LoginThread(login, password)
        self.thread.complete.connect(self.authComplete)
        self.thread.start()

    def authComplete(self, state):
        if state:
            self.authOnlineSuccess()
        else:
            self.authOnlineFail()
        self.splash.hide()

    def authOnlineSuccess(self):
        DataManager().isOnline = True
        FileManager().loadSettings()
        FileManager().loadDownloads()
        if self.ui.rememberMe.isChecked():
            FileManager().saveUser(login, password)
        self.mainWindow.loadWidgets()
        self.mainWindow.show()
        #self.hide()

    def authOnlineFail(self):
        self.show()
        QApplication.setQuitOnLastWindowClosed(False);
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText('Не удалось войти в аккаунт!')
        msg.setInformativeText('Возможно вы ввели неправильные данные.')
        msg.setWindowTitle('Вход')
        msg.exec()
        QApplication.setQuitOnLastWindowClosed(True)


