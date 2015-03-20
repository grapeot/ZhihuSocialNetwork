import credential
import requests

timeout = 30

def getZhihu(url, includeCookie=True):
    cookies = credential.cookies if includeCookie else ''
    r = requests.get(url, cookies=cookies)
    return r.content

def postZhihu(url, data, includeCookie=True):
    cookies = credential.cookies if includeCookie else ''
    r = requests.post(url, cookies=cookies, data=data)
    return r.content
