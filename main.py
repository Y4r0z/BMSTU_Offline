import os
from pathlib import Path
import sys
from PySide6.QtWidgets import *
from MainWindow import MainWindow
from AuthWindow import AuthWindow
from UniversalWindow import UniversalWindow
if __name__ == "__main__":
    app = QApplication([])
    #widget = MainWindow()
    #widget.hide()
    widget = UniversalWindow()
    widget.hide()
    auth = AuthWindow(widget)
    sys.exit(app.exec())
