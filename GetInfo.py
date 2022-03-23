# This Python file uses the following encoding: utf-8
if __name__ == "__main__":
    pass

import requests
from bs4 import BeautifulSoup as bs
import lxml.html

from data import PostUrl
from data import BMSTULogin
from data import BMSTUPassword
from data import GetUrl

def getCookie(session):
    cookiePath = '//*[@id="fm1"]/section[4]/input[1]'
    with session.get(GetUrl, stream = True) as response:
        response.raw.decode_content = True
        tree = lxml.html.parse(response.raw)
        cookieElement = tree.xpath(cookiePath)[0]
        cookieValue = cookieElement.value
    return cookieValue

def login(session):
    payload = {
        'username' : BMSTULogin,
        'password' : BMSTUPassword,
        'execution' : getCookie(session),
        '_eventId' : 'submit'
    }

    response = session.post(PostUrl, data = payload)
    return response


