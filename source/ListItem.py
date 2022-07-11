
class ListItem:
    def __init__(self, text='item_text', type='item_type', href='item_href', progress=0):
        self._text = text
        self._type = type.lower()
        self._href = href
        self._downloadProgress = progress
        self.parent = None
        self._locked = False
        #В списке хранятся имена, которые ассоциируются со свойством/переменной
        self._properties =\
        {
        ('name', 'text'): self._text,
        ('type'): self._type,
        ('href', 'link'): self._href,
        ('state', 'download', 'downloadState', 'downloadProgress'): self._downloadProgress,
        ('parent'): self.parent,
        ('lock', 'locked'): self._locked
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
    
    @property
    def locked(self):
        return self._locked
    @locked.setter
    def locked(self, new):
        self._locked = new

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
        if self.parent is not None and len(self.parent.storage) > 0:
            n = len(self.parent.storage)
            k = 0
            for i in self.parent.storage:
                k += i.downloadProgress
            self.parent.downloadProgress = (k/n)

    def getProperty(self, key):
        ret = None
        for i in self._properties.keys():
            if key in i:
                ret = self._properties[i]
                break
        return ret
    def __getitem__(self, key):
        return self.getProperty(key)

    def __str__(self):
        return self._text

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
            items = []
            for i in dict['storage']:
                tmp = ListItem.FromDict(i)
                tmp.parent = item
                items.append(tmp)
            item.set(items)
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

    @staticmethod
    def StorageDepth(item):
        if item.Signature == 'file' or len(item.storage) == 0:
            return 0
        summ = 0
        for i in item.storage:
            summ += ListItem.StorageDepth(i)
        return len(item.storage) + summ

    @staticmethod
    def Merge(primary, secondary):
        if primary.href != secondary.href: return primary
        if primary.Signature == 'file':
            return primary
        if primary.Signature == 'storage':
            if len(primary.storage) == 0 and len(secondary.storage) == 0: return primary
            if len(primary.storage) == 0:
                return secondary
            elif len(secondary.storage) == 0:
                return primary
            elif len(primary.storage) != len(secondary.storage):
                return primary
            else:
                store = [ListItem.Merge(primary.storage[i], secondary.storage[i]) for i in range(len(primary.storage))]
                primary.set(store)
                return primary

    @staticmethod
    def GetFiles(item, itemsList):
        if item.Signature == 'file':
            itemsList.append(item)
            return
        else:
            for i in item['files']:
                ListItem.GetFiles(i, itemsList)
        

          


class ListFile(ListItem):
    Signature = 'file'

    def __init__(self, text, type, href, progress=0):
        super().__init__(text, type, href, progress)
        self._path = []
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
        self._properties[('files', 'activities')] = self.storage

    def add(self, item):
        self.storage.append(item)

    def set(self, lst):
        self.storage.clear()
        if lst is None or len(lst) == 0:
            return
        for i in lst:
            self.storage.append(i)


    def toDict(self):
        dict = {}
        dict['signature'] = self.Signature
        dict['text'] = self._text
        dict['type'] = self._type
        dict['href'] = self._href
        dict['download'] = self._downloadProgress
        dict['storage'] = [i.toDict() for i in self.storage]
        return dict
