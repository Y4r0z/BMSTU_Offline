import lxml.html
import urllib.parse
import os
from Debugger import Debugger

PostUrl = 'https://proxy.bmstu.ru:8443/cas/login?service=https%3A%2F%2Fe-learning.bmstu.ru%2Fkaluga%2Flogin%2Findex.php%3FauthCAS%3DCAS'
GetUrl = 'https://proxy.bmstu.ru:8443/cas/login?service=https://e-learning.bmstu.ru/kaluga/login/index.php?authCAS=CAS'


def getCookie(session):
    cookiePath = '//*[@id="fm1"]/section[4]/input[1]'
    with session.get(GetUrl) as response:
        tree = lxml.html.fromstring(response.text)
        cookieElement = tree.xpath(cookiePath)[0]
        cookieValue = cookieElement.value
    return cookieValue


def loginOnline(login, password, session):
    payload = {
    'username' : login,
    'password' : password,
    'execution' : getCookie(session),
    '_eventId' : 'submit'
    }
    return session.post(PostUrl, data = payload, stream = True)


def endSession(session):
    with session.get('https://e-learning.bmstu.ru/kaluga/') as page:
        if page.status_code == 200:
            tree = lxml.html.fromstring(page.text)
            exit = tree.xpath('//*[@id="action-menu-1-menu"]/a[5]')
            if(len(exit) == 0):
                return
            href = exit[0].values()[0]
            session.get(href)

def getSessKey(session):
    mainPage = session.get('https://e-learning.bmstu.ru/kaluga/')
    tree = lxml.html.fromstring(mainPage.text)
    key = tree.xpath('//*[@id="action-menu-1-menu"]/a[5]')[0].get('href').split('=')[-1]
    return key

def getFiles(session, assign):
    try:
        with session.get(assign['href']) as page:
            if page.status_code != 200:
                Debugger().throw('NF.getFiles() response error')
                return []
            filesList = []
            tree = lxml.html.fromstring(page.text)
            if assign['type'] != 'folder':
                description = None
                try:
                    task = tree.xpath('//*[@id="intro"]/div[1]')
                    if len(task) != 0:
                        linesList = []
                        lines = task[0].xpath('p')
                        for i in lines:
                            if i.text is None or len(i.text) < 2:
                                temp = i.xpath('string()')
                                linesList.append(temp)
            
                            else:
                                linesList.append(i.text)

                        description = '\n'.join([i for i in linesList])
                        if len(description) < 5:
                            description = None
                        assign.description = description
                except Exception as e:
                    Debugger().throw("GetFiles, can't get description(task):\n"+str(e))

                files = tree.xpath("//div[@class='fileuploadsubmission']")
                if len(files) == 0:
                    return None
                for i in files:
                    name, type = os.path.splitext(i.xpath('img')[0].get('title'))
                    type = type[1::]
                    href = i.xpath('a')[0].values()[1]
                    filesList.append({'text':name, 'href':href, 'type':type,
                    'state':{}, 'parent':assign['href'], 'description':description
                    })
            else:
                files = tree.xpath("//span[@class='fp-filename-icon']")
                if len(files) == 0:
                    return None
                for i in files:
                    href = i.xpath('a')[0].get('href')
                    splitted = href.split('/')[-1].split('?')[0].split('.')
                    name = ''.join(splitted[:-1])
                    type = splitted[-1]
                    name = urllib.parse.unquote(name)
                    filesList.append({'text':name, 'href':href, 'type':type,
                    'state':{}, 'parent':assign['href'], 'description':None
                    })
            return filesList
    except Exception as e:
        Debugger().throw('NF.getFiles() error:\n' + str(e))


def getSubjects(session, loginResult):
    subjects = []
    mainPage = loginResult
    coursesPath = '//*[@id="frontpage-course-list"]/div/div'
    if mainPage.status_code == 200:
        mainPage.raw.decode_content = True
        tree = lxml.html.parse(mainPage.raw)
        for i in tree.xpath(coursesPath):
            course = i.xpath('div[1]/h3/a')
            teachers = i.xpath("div[2]/ul/li")
            teacherNames = ['Преподаватели:']
            for t in teachers:
                teacherNames.append(t.xpath('a/text()')[0])
            if len(course) > 0:
                courseID = i.values()[1]
                subjects.append(
                {
                'text': course[0].text,
                'href': course[0].values()[1],
                'id': courseID,
                'activities': [],
                'description': ('\n'.join(teacherNames) if len(teacherNames) > 1 else None)
                }
                )

        mainPage.close()
    else:
        Debugger().throw('Main page response error!')
    return subjects

def iterActivities(session, subject):
    """
    Итератор для getActivities().
    """
    with session.get(subject['href']) as coursePage:
        if coursePage.status_code != 200:
            Debugger().throw('Course page response error!')
            return None
        tree = lxml.html.fromstring(coursePage.text)
        topics = tree.xpath('//*[@id="region-main"]/div/div/div/div/ul')
        if len(topics) == 0:
            return None
        acts = topics[0].xpath('//*[starts-with(@id,"module")]')
        for i in acts:
            try:
                parsedActivity = parseActivity(i, session)
                if not parsedActivity:
                    yield None
                else:
                    parsedActivity['parent'] = subject['href']
                    yield parsedActivity
            except Exception as e:
                Debugger().throw("iterActivites(). Some activites was passed because of:\n" + str(e))

def getActivities(session, s):
    """
        session - авторизированная сессия requests
        s - subject, курс
    """
    if len(s['activities']) > 0:
        return s['activities']
    with session.get(s['href']) as coursePage:
        activities = []
        if coursePage.status_code != 200:
            Debugger().throw('Course page response error!')
            return s['activities']
        tree = lxml.html.fromstring(coursePage.text)
        topics = tree.xpath('//*[@id="region-main"]/div/div/div/div/ul')
        if len(topics) == 0:
            return []
        acts = topics[0].xpath('//*[starts-with(@id,"module")]')
        for i in acts:
            try:
                parsedActivity = parseActivity(i, session)
                if parsedActivity:
                    parsedActivity['parent'] = s['href']
                    activities.append(parsedActivity)
            except Exception as e:
                Debugger().throw("getActivites(). Some acts was passed because of:\n" + str(e))
    return activities

def parseActivity(rawActivity, session):
    """
    На вход подается список html объектов activity
    Формат вывода:
    {'text': text, 'type': type, 'href': activityLink, 'files': files}
    """
    #get type
    type = rawActivity.get('class').split(' ')[1].lower()
    if type not in ['assign', 'resource', 'folder']:
        return
    #get name
    textraw = rawActivity.xpath('div/div/div[2]/div[1]/a/span/text()')
    if len(textraw) == 0:
        return
    text = textraw[0]
    #Get href
    activity = rawActivity.xpath('div/div/div[2]/div[1]/a')[0]
    activityLink = activity.get('href')
    #get type for resource
    if type == 'resource':
        source = activity.xpath('img')[0].get('src')
        type = source.split('/')[-1].split('-')[0]
        if type != 'pdf':
            downloadLink = session.get(activityLink, allow_redirects=False)
            tree2 = lxml.html.fromstring(downloadLink.text)
            if type == 'mp3':
                t = tree2.xpath('/html/body/div[1]/div[2]/div/div/section/div/div/div/div/div/div/div/div/audio/source')
                tempHref = t[0].get('src')
                type = tempHref.split('/')[-1].split('.')[-1]
                activityLink = tempHref
                text += ' аудио'
            elif type in ['jpg', 'png', 'gif', 'tiff', 'bmp', 'psd', 'jpeg']:
                t = tree2.xpath('//*[@id="region-main"]/div/div/div/div/img')[0]
                text = t.get('title')
                activityLink = t.get('src')
                type = activityLink.split('.')[-1]
            else:
                t = tree2.xpath('//*[@id="region-main"]/div/a')
                if len(t) == 0:
                    Debugger().throw("Undefined activity type!")
                    return
                tempHref = t[0].get('href')
                type = tempHref.split('.')[-1].split('?')[0]
    files = None
    if type in ['assign', 'folder']:
        files = []
    return {'text': text, 'type': type, 'href': activityLink, 'files': files}