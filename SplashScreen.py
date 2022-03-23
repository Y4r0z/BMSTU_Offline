import os
from pathlib import Path
import sys

from PySide6.QtWidgets import *
from PySide6.QtCore import QFile, qDebug, Qt, QSize
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon, QMovie
from FileManager import FileManager
from DataManager import DataManager

class SplashScreen(QWidget):
    def __init__(self, parent):
        super(SplashScreen, self).__init__()
        self.ui = None
        self.load_ui()
        self.loadWidgets()
        self.parent = parent

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "SplashScreenForm.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        self.setGeometry(self.ui.geometry())
        self.hide()
        self.setWindowTitle('Авторизация BMSTU')
        self.setWindowIcon(FileManager().getIcons()['bmstu'])
        ui_file.close()

    def loadWidgets(self):
        self.setLayout(self.ui.layout())
        self.ui.widget.setAlignment(Qt.AlignCenter)
        movie = QMovie('icons/pulse.gif')
        movie.setScaledSize(QSize(160,160))
        self.ui.label.setMovie(movie)
        movie.start()

    def run(self):
        self.setGeometry(self.parent.geometry())
        self.show()

    def closeEvent(self, event):
        DataManager().endSession()
