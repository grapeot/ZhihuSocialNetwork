import urllib2
import credential

def getZhihu(url):
    req = urllib2.Request(url)
    req.add_header('Cookie', credential.cookies)
    res = urllib2.urlopen(req)
    return res.read()

def postZhihu(url, data):
    req = urllib2.Request(url, data=data)
    req.add_header('Cookie', credential.cookies)
    res = urllib2.urlopen(req)
    return res.read()
