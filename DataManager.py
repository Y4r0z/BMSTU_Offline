import lxml.html
import requests
from data import PostUrl
from data import GetUrl
import os


def getCookie(session):
    cookiePath = '//*[@id="fm1"]/section[4]/input[1]'
    with session.get(GetUrl) as response:
        tree = lxml.html.fromstring(response.text)
        cookieElement = tree.xpath(cookiePath)[0]
        cookieValue = cookieElement.value
    return cookieValue

def getFiles(session, assign):
    try:
        with session.get(assign['href']) as page:
            if page.status_code == 200:
                filesList = []
                tree = lxml.html.fromstring(page.text)
                files = tree.xpath("//div[@class='fileuploadsubmission']")
                if len(files) == 0:
                    return None
                for i in files:
                    name, type = os.path.splitext(i.xpath('img')[0].get('title'))
                    type = type[1::]
                    href = i.xpath('a')[0].values()[1]
                    filesList.append({'text':name, 'href':href, 'type':type,
                    'state':{}, 'parent':assign['href']
                    })
                return filesList
            else:
                return []
    except Exception as e:
        print('getFiles() error:')
        print(e)



class DataManager():
    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(DataManager, cls).__new__(cls)
            cls.session = requests.Session()
            cls.subjects = []
            cls.downloads = []
            cls.loadedFiles = []
            cls.username = None
            cls.password = None
            cls.settings = {
            'filter': '',
            'mainWindow': None,
            'courseWindow': None,
            'assignWindow': None
            }


            cls.loginResult = None
            cls.isOnline = False
            cls.dataInitiated = False
        return cls.__instance

    def getSubjects(self):
        if len(self.subjects) > 0:
            return self.subjects
        if self.loginResult is None:
            return []
        mainPage = self.loginResult
        coursesPath = '//*[@id="frontpage-course-list"]/div/div'
        if mainPage.status_code == 200:
            mainPage.raw.decode_content = True
            tree = lxml.html.parse(mainPage.raw)
            for i in tree.xpath(coursesPath):
                course = i.xpath('div[1]/h3/a')
                if (len(course) > 0):
                    courseID = i.values()[1]
                    self.subjects.append(
                    {'text':course[0].text,
                    'href':course[0].values()[1],
                    'id':courseID,
                    'activities':[]})

            mainPage.close()
        else:
            print('Main page response error!')
        return self.subjects

    def getActivities(self, id, asyncMode = False):
        subjects = self.getSubjects()
        asyncArray = []
        s = None
        for i in subjects:
            if i['id'] == id:
                s = i
        if s is None:
            print(f"getActivities() can't find ID {id}!")
            return []
        if len(s['activities']) > 0:
            return s['activities']

        with self.session.get(s['href']) as coursePage:
            if coursePage.status_code == 200:
                #coursePage.raw.decode_content = True
                #tree = lxml.html.parse(coursePage.raw)
                tree = lxml.html.fromstring(coursePage.text)
                topics = tree.xpath('//*[@id="region-main"]/div/div/div/div/ul')
                if len(topics) == 0:
                    return []
                acts = topics[0].xpath('//*[starts-with(@id,"module")]')
                for i in acts:
                    try:
                        #get type
                        type = i.get('class').split(' ')[1].lower()
                        if type in ['assign', 'resource']:
                            #get name
                            textraw = i.xpath('div/div/div[2]/div[1]/a/span/text()')
                            if len(textraw) == 0:
                                continue
                            text = textraw[0]
                            #Get href
                            activityLink = i.xpath('div/div/div[2]/div[1]/a')[0].get('href')
                            #get type for resource
                            if type == 'resource':
                                downloadLink = self.session.get(activityLink, allow_redirects=False)
                                tree2 = lxml.html.fromstring(downloadLink.text)
                                t = tree2.xpath('//*[@id="region-main"]/div/a')
                                tempHref = t[0].get('href')
                                type = tempHref.split('.')[-1].split('?')[0]
                            files = None
                            if type == 'assign':
                                files = []
                            if not asyncMode:
                                s['activities'].append({'text':text, 'type':type, 'href':activityLink, 'files':files, 'parent':s['href']})
                            else:
                                asyncArray.append( {'text':text, 'type':type, 'href':activityLink, 'files':files, 'parent':s['href']})
                    except Exception as e:
                        print('getActivities() error:')
                        print(e)

                        continue
            else:
                print('Course page response error!')
        if asyncMode:
            return asyncArray
        return s['activities']

    def getFiles(self, assign):
        files = getFiles(self.session, assign)
        if files is None:
            return None
        for i in files:
            self.loadedFiles.append(i)
        return files

    def endSession(self):
        if not self.isOnline:
            return
        with self.session.get('https://e-learning.bmstu.ru/kaluga/') as page:
            if page.status_code == 200:     
                tree = lxml.html.fromstring(page.text)
                exit = tree.xpath('//*[@id="action-menu-1-menu"]/a[5]')
                if(len(exit) == 0):
                    return
                href = exit[0].values()[0]
                end = self.session.get(href)

    def initiateData(self):
        subs = self.getSubjects()
        for i in subs:
            acts = self.getActivities(i['id'])
            for j in acts:
                if j['files'] is None:
                    continue
                if len(j['files']) == 0 and j['type'] == 'assign':
                    j['files'] = self.getFiles(j)
        self.dataInitiated = True

    def setSubjects(self, data):
        if len(self.subjects) == 0:
            self.subjects = data
        else:
            print("DataManaget().setSubjects(data): self.subjects isn't empty")

    def setUser(self, l, p):
        if l is None or p is None:
            print('DataManager().setUser(log, pas): log or pas is None')
        else:
            self.username = l
            self.password = p

    def reloadOnline(self):
        self.subjects = []
        self.initiateData()


    def login(self, login, password):
        payload = {
        'username' : login,
        'password' : password,
        'execution' : getCookie(self.session),
        '_eventId' : 'submit'
        }
        response = self.session.post(PostUrl, data = payload, stream = True)
        self.loginResult = response
        if response.status_code == 200:
            return True
        else:
            return False

    def getSettings(self):
        return self.settings

    def setSettings(self, sets):
        self.settings = sets

    def getFileParent(self, file, path):
        subs = self.getSubjects()
        for i in subs:
            if i['text'] != path[0]:
                continue
            acts = self.getActivities(i['id'])
            for j in acts:
                if j['text'] == path[1] and j['href'] == file['parent']:
                    return j
        return None


    def getRawPath(self, text, path):
        file = None
        subs = self.getSubjects()
        for i in subs:
            if i['text'] != path[0]:
                continue        
            acts = self.getActivities(i['id'])
            for j in acts:
                if j['text'] == text and len(path) == 1:
                    file = j
                    #filename, fileext = os.path.splitext(file['text'])
                    filename = text
                    fileext = '.' + file['type']
                    rawPath = ['repository', path[0], filename]
                    return (rawPath, file, fileext)
                elif len(path) == 1:
                    continue
                if j['text'] != path[1]:
                    continue
                for k in j['files']:
                    if k['text'] == text:
                        file = k

        filename, fileext = file['text'], '.' + file['type']
        rawPath = ['repository', path[0], path[1], filename]
        return (rawPath, file, fileext)


    def getFilePath(self, text, path):
        rawPath, file, fileext = self.getRawPath(text, path)
        if file is None or len(rawPath) == 0:
            print('DM().getFilePath() cant get path.')
            return ([], None)
        chars = [i for i in(' -./<>:"\|?*#%&{}$!@=+`,()' + "'")]
        path = []
        for i in rawPath:
            temp = ''
            for j in i:
                if not j in chars:
                    temp += j
            path.append(temp)
        #print(1, rawPath, '|', fileext)
        path[-1] = path[-1]+fileext
        return (path, file)


    def getDownloadData(self, href):
        r = self.session.get(href)
        return r.content

    def isDownloaded(self, href):
        for i in self.downloads:
            if i['href'] == href:
                return True
        return False

    def getDownload(self, href):
        for i in self.downloads:
            if i['href'] == href:
                return i
        return {'href':None, 'progress':0}

    def addDownload(self, href, progress = 100):
        if not self.isDownloaded(href):
            self.downloads.append({'href':href, 'progress':progress})
        else:
            self.getDownload(href)['progress'] = progress
        if type is None:
            return

    def removeDownload(self, href):
        self.downloads = [i for i in self.downloads if i['href'] != href]


    def getDownloads(self):
        return self.downloads

    def setDownloads(self, downloads):
        self.downloads = downloads






