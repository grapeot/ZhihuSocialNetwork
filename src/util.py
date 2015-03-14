import urllib2
import credential

def getZhihu(url, includeCookie=True):
    req = urllib2.Request(url)
    if includeCookie:
        req.add_header('Cookie', credential.cookies)
    res = urllib2.urlopen(req)
    return res.read()

def postZhihu(url, data, includeCookie=True):
    req = urllib2.Request(url, data=data)
    if includeCookie:
        req.add_header('Cookie', credential.cookies)
    res = urllib2.urlopen(req, timeout=10)
    return res.read()
