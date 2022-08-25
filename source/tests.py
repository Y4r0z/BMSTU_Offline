import os
import sys
from PySide6.QtWidgets import *
from DataManager import DataManager
from FileManager import FileManager
from windows.PropertyWindow import PropertyWindow

class Tests:
    def __init__(self):
        DataManager().isOnline = False
        FileManager().loadSubjects()

    def test_property(self):
        subject = DataManager().getSubjects()[0]
        self.window = PropertyWindow(subject)
        self.window.show()

if __name__ == '__main__':
    app = QApplication([])
    tests = Tests()
    tests.test_property()
    sys.exit(app.exec())