import os
from pathlib import Path
import sys
from PySide6.QtWidgets import *
from windows.AuthWindow import AuthWindow
from windows.UniversalWindow import UniversalWindow
if __name__ == "__main__":
    app = QApplication([])
    widget = UniversalWindow()
    widget.hide()
    auth = AuthWindow(widget)

    sys.exit(app.exec())
