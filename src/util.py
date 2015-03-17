import urllib2
import credential

timeout = 10

def getZhihu(url, includeCookie=True):
    req = urllib2.Request(url)
    if includeCookie:
        req.add_header('Cookie', credential.cookies)
    res = urllib2.urlopen(req, timeout=timeout)
    return res.read()

def postZhihu(url, data, includeCookie=True):
    req = urllib2.Request(url, data=data)
    if includeCookie:
        req.add_header('Cookie', credential.cookies)
    res = urllib2.urlopen(req, timeout=timeout)
    return res.read()
