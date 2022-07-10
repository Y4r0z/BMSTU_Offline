from PySide6.QtGui import QIcon
from Debugger import Debugger

class FileTypeIcon:
    fileTypes = {}

    def __init__(self, iconName, typeNames):
        self.icon = iconName
        self.type = typeNames
        self.fileTypes[str(iconName)] = typeNames



class IconsManager:
    icons = {}

    def find(self, name):
        if name in self.icons.keys():
            return True
        return False
    
    def getItemIcon(self, item):
        if item.type in self.icons.keys():
            return self.icons[item.type]
            return
        types = FileTypeIcon.fileTypes
        for i in types.keys():
            if item.type in types[i]:
                return self.icons[i]
        return self.icons['unknown']


    def __add(self, name, path, namesList = None):
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
        if namesList is not None:
            FileTypeIcon(name, namesList)


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
        self.__add('pdf', 'icons/pdf.png', ['pdf'])
        self.__add('zip', 'icons/zip.png', ['zip', 'rar', '7zip', '7z'])
        self.__add('doc', 'icons/doc.png', ['doc', 'docx', 'odt'])
        self.__add('txt', 'icons/txt.png', ['txt'])
        self.__add('xls', 'icons/xls.png', ['xls', 'xlsx'])
        self.__add('ppt', 'icons/ppt.png', ['ppt', 'pptx', 'ppsx'])
        self.__add('unknown', 'icons/unknown.png')
        self.__add('image', 'icons/image.png', ['jpg', 'png', 'gif', 'tiff', 'bmp', 'psd', 'jpeg'])
        self.__add('audio', 'icons/audio.png', ['mp3', 'ogg', 'wav', 'flac', 'aac', 'wma'])
        self.__add('bmstu', 'icons/bmstu.png')
        self.__add('saved', 'icons/saved.png')
        self.__add('unsaved', 'icons/unsaved.png')
        self.__add('semisaved', 'icons/semiSaved.png')
        self.__add('return', 'icons/return.png')
        self.__add('settings', 'icons/settings.png')
        self.__add('courseSaved', 'icons/courseSaved')
        self.__add('courseSemiSaved', 'icons/courseSemiSaved.png')
        self.__add('courseUnsaved', 'icons/courseUnsaved.png')
        self.__add('bmstu_small', 'icons/BMSTU_cut.png')
        self.__add('lock', 'icons/lock.png')


