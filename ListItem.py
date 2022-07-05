

class ListItem:

    def __init__(self, text = 'item_text', type = 'item_type', href = 'item_href', progress = 0):
        self._text = text
        self._type = type
        self._href = href
        self._downloadProgress = progress
        #В списке хранятся именя, которые ассоциируются со свойством
        self._properties =\
        {
        ('name', 'text'): self._text,
        ('type'): self._type,
        ('href', 'link'): self._href,
        ('state', 'download', 'downloadState', 'downloadProgress'): self._downloadProgress,
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
        raise NotImplementedError("Context action not implemented!")

    def onClickAction(self):
        raise NotImplementedError("Click action not implemented!")


class ListFile(ListItem):
    def __init__(self, text, type, href, progress = 0.0):
        super().__init__(text, type, href, progress)
        self.path = "unknown_path"
        self._properties[('path')] = self.path

    def contextAction(self):
        pass

    def onClickAction(self):
        pass


class ListStorage(ListItem):

    def __init__(self, text, type, href, progress = 0):
        super().__init__(text, type, href, progress)
        self.storage = []

    def add(self, item):
        self.storage.append(item)

    def set(self, lst):
        self.storage = lst

    def contextAction(self):
        pass

    def onClickAction(self):
        pass
