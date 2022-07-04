from PySide6.QtGui import QIcon
from Debugger import Debugger

class IconsManager:
    icons = {}

    def find(self, name):
        if name in self.icons.keys():
            return True
        return False

    def __add(self, name, path):
        if self.find(name):
            Debugger().throw('IconsManager.__add(obj). obj is already exists')
            return
        icon = False
        try:
            icon = QIcon(path)
        except:
            icon = False
            Debugger().throw("IconsManager.__add() failed!")
        if icon is False:
            return
        self.icons[name] = icon


    def get(self, name):
        if self.find(name):
            return self.icons[name]
        return self.icons['unknown']
    def __getitem__(self, key):
        return self.get(key)

    def __init__(self):
        self.__add('download', 'icons/download.png')
        self.__add('delete', 'icons/delete.png')
        self.__add('open', 'icons/open.png')
        self.__add('assign', 'icons/assign.png')
        self.__add('resource', 'icons/resource.png')
        self.__add('course', 'icons/course.png')
        self.__add('folder', 'icons/folder.png')
        self.__add('pdf', 'icons/pdf.png')
        self.__add('zip', 'icons/zip.png')
        self.__add('doc', 'icons/doc.png')
        self.__add('txt', 'icons/txt.png')
        self.__add('xls', 'icons/xls.png')
        self.__add('ppt', 'icons/ppt.png')
        self.__add('unknown', 'icons/unknown.png')
        self.__add('image', 'icons/image.png')
        self.__add('audio', 'icons/audio.png')
        self.__add('bmstu', 'icons/bmstu.png')
        self.__add('saved', 'icons/saved.png')
        self.__add('unsaved', 'icons/unsaved.png')
        self.__add('semisaved', 'icons/semiSaved.png')
        self.__add('return', 'icons/return.png')
        self.__add('settings', 'icons/settings.png')
        self.__add('courseSaved', 'icons/courseSaved')
        self.__add('courseSemiSaved', 'icons/courseSemiSaved.png')
        self.__add('courseUnsaved', 'icons/courseUnsaved.png')


