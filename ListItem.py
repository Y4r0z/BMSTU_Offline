
class ListItem:
    def __init__(self, text='item_text', type='item_type', href='item_href', progress=0):
        self._text = text
        self._type = type
        self._href = href
        self._downloadProgress = progress
        self.parent = None
        self.signature = None
        #В списке хранятся имена, которые ассоциируются со свойством/переменной
        self._properties =\
        {
        ('name', 'text'): self._text,
        ('type'): self._type,
        ('href', 'link'): self._href,
        ('state', 'download', 'downloadState', 'downloadProgress'): self._downloadProgress,
        ('parent'): self.parent
        }

    @property
    def text(self):
        return self._text

    @property
    def type(self):
        return self._type

    @property
    def href(self):
        return self._href

    @property #0.0 - 100.0
    def downloadProgress(self):
        return self._downloadProgress

    @downloadProgress.setter
    def downloadProgress(self, new):
        if new < 0:
            new = 0
        if new > 100:
            new = 100
        self._downloadProgress = new
        self._properties[('state', 'download', 'downloadState', 'downloadProgress')] = self._downloadProgress

    def getProperty(self, key):
        ret = None
        for i in self._properties.keys():
            if key in i:
                ret = self._properties[i]
                break
        return ret
    def __getitem__(self, key):
        return self.getProperty(key)

    def contextAction(self):
        raise NotImplementedError("Context action is not implemented!")

    def onClickAction(self):
        raise NotImplementedError("Click action is not implemented!")

    def toDict(self):
        raise NotImplementedError("Dictionary transformation is not implemented!")

    def __str__(self):
        return self._text

    #
    # Добавить родителя в .parent
    #
    @staticmethod
    def FromDict(dict):
        item = None
        text = dict['text']
        type = dict['type']
        href = dict['href']
        download = dict['download']
        if dict['signature'] == 'file':
            item = ListFile(text, type, href)
            item.path = dict['path']
        else:
            item = ListStorage(text, type, href)
            item.set([ListItem.FromDict(i) for i in dict['storage']])
        item.downloadProgress = download
        return item
    
    @staticmethod
    def FindByHref(href, item):
        if item.href == href:
            return item
        if item.Signature == 'storage':
            for i in item.storage:
                find = ListItem.FindByHref(href, i)
                if find and find.href == href:
                    return find
        return None


class ListFile(ListItem):
    Signature = 'file'

    def __init__(self, text, type, href, progress=0):
        super().__init__(text, type, href, progress)
        self._path = []
        self.signature = self.Signature
        self._properties[('path')] = self._path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new):
        self._path.clear()
        if new is None or len(new) == 0:
            return
        for i in new:
            self._path.append(i)

    def contextAction(self):
        pass

    def onClickAction(self):
        pass

    def toDict(self):
        dict = {}
        dict['signature'] = self.Signature
        dict['text'] = self._text
        dict['type'] = self._type
        dict['href'] = self._href
        dict['download'] = self._downloadProgress
        dict['path'] = self._path
        return dict


class ListStorage(ListItem):
    Signature = 'storage'
    Types = ['assign', 'folder', 'course']

    def __init__(self, text, type, href, storage=None, progress=0):
        super().__init__(text, type, href, progress)
        if storage is None: self.storage = []
        else: self.storage = storage
        self.signature = self.Signature
        self._properties[('files', 'activities')] = self.storage

    def add(self, item):
        self.storage.append(item)

    def set(self, lst):
        self.storage.clear()
        if lst is None or len(lst) == 0:
            return
        for i in lst:
            self.storage.append(i)

    def contextAction(self):
        pass

    def onClickAction(self):
        pass

    def toDict(self):
        dict = {}
        dict['signature'] = self.Signature
        dict['text'] = self._text
        dict['type'] = self._type
        dict['href'] = self._href
        dict['download'] = self._downloadProgress
        dict['storage'] = [i.toDict() for i in self.storage]
        return dict
