import credential
import requests
import urllib2

timeout = 30

def getZhihu(url, includeCookie=True):
    cookies = credential.cookie if includeCookie else ''
    r = requests.get(url, cookies=cookies)
    return r.content

def postZhihu(url, data, includeCookie=True):
    if not includeCookie:
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        return response.read()
    else:
        cookies = credential.cookie if includeCookie else ''
        r = requests.post(url, cookies=cookies, data=data)
        return r.content
