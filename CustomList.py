from PySide6.QtWidgets import QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QWidget, QLabel
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtCore import QSize, Qt, QRect
from FileManager import FileManager
class CustomList():
    def __init__(self, ui_list):
        super(CustomList, self).__init__()
        self.list = ui_list
        self.icons = FileManager().getIcons()
    def getList(self):
        return self.list

    def clear(self):
        self.list.clear()

    def addItem(self, text, type = None, state = {}):
        if not type is None:
            type = type.lower()
        if type is None:
            item = QListWidgetItem(text)
        elif type == 'assign':
            item = QListWidgetItem(self.icons['assign'], text)
        elif type == 'resource':
            item = QListWidgetItem(self.icons['resource'], text)
        elif type == 'folder':
            item = QListWidgetItem(self.icons['folder'], text)
        elif type == 'course':
            if len(state.keys()) == 0 or state['courseState'] is None:
                item = QListWidgetItem(self.icons['course'], text)
            else:
                value = state['courseState']
                if value == 0:
                    item = QListWidgetItem(self.icons['courseUnsaved'], text)
                elif value == 100:
                    item = QListWidgetItem(self.icons['courseSaved'], text)
                else:
                    icon = self.icons['courseSaved']
                    icon2 = self.icons['courseUnsaved']
                    size = 18
                    pm = QPixmap(size,size)
                    pm.fill(Qt.transparent)
                    p1 = icon.pixmap(icon.actualSize(QSize(32,32)))
                    p1 = p1.scaled(QSize(size, size), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    p2 = icon2.pixmap(icon2.actualSize(QSize(32,32)))
                    p2 = p2.scaled(QSize(size, size), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    fill = value/100
                    r1 = QRect(0,0,size,size)
                    r2 = QRect(0,0,size,size * (1 - fill))
                    painter = QPainter(pm)
                    painter.drawPixmap(r1, p1, r1)
                    painter.drawPixmap(r2, p2, r2)
                    painter.end()
                    newIcon = QIcon(pm)
                    item = QListWidgetItem(newIcon, text)

        elif type in ['doc', 'docx']:
            item = QListWidgetItem(self.icons['doc'], text)
        elif type == 'txt':
            item = QListWidgetItem(self.icons['txt'], text)
        elif type in ['xls', 'xlsx']:
            item = QListWidgetItem(self.icons['xls'], text)
        elif type in ['ppt', 'pptx', 'ppsx']:
            item = QListWidgetItem(self.icons['ppt'], text)
        elif type == 'pdf':
            item = QListWidgetItem(self.icons['pdf'], text)
        elif type in ['jpg', 'png', 'gif', 'tiff', 'bmp', 'psd']:
            item = QListWidgetItem(self.icons['image'], text)
        elif type in ['zip', 'rar', '7zip', '7z']:
            item = QListWidgetItem(self.icons['zip'], text)
        elif type in ['mp3', 'ogg', 'wav', 'flac', 'aac', 'wma']:
            item = QListWidgetItem(self.icons['audio'], text)
        else:
            item = QListWidgetItem(self.icons['unknown'], text)

        if not type == 'course' and 'progress' in state.keys():
            widget = QWidget(self.list)
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addStretch()
            layout.addStrut(0)

            label = QLabel()
            if state['progress'] == 100:
                icon = self.icons['saved']
                pm = icon.pixmap(icon.actualSize(QSize(17, 17)))
            elif state['progress'] == 0:
                icon = self.icons['unsaved']
                pm = icon.pixmap(icon.actualSize(QSize(17, 17)))
            else:
                icon = self.icons['saved']
                icon2 = self.icons['unsaved']
                pm = QPixmap(17,17)
                pm.fill(Qt.transparent)
                p1 = icon.pixmap(icon.actualSize(QSize(32,32)))
                p1 = p1.scaled(QSize(17,17), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                p2 = icon2.pixmap(icon2.actualSize(QSize(32,32)))
                p2 = p2.scaled(QSize(17,17), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                fill = state['progress']/100
                r1 = QRect(0,0,17,17)
                r2 = QRect(0,0,17,17 * (1 - fill))
                painter = QPainter(pm)
                painter.drawPixmap(r1, p1, r1)
                painter.drawPixmap(r2, p2, r2)
                painter.end()

            label.setPixmap(pm)
            layout.addWidget(label)
            widget.setLayout(layout)
            self.list.addItem(item)
            self.list.setItemWidget(item, widget)
        else:
            self.list.addItem(item)

