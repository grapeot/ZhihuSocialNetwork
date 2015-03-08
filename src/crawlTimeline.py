# -*- coding: utf-8 -*-

import util
import sys, time, re, json

def crawlTimeline(userid):
    """ Crawl the timeline of the user, and return the string. """
    apiurl = 'http://www.zhihu.com/people/{0}/activities'.format(userid)
    params = 'start={0}&_xsrf=c4b07884cfea379e46cdcb89fcf08cc4'
    timestamp = int(time.time())
    isContinue = True

    while isContinue:
        content = util.postZhihu(apiurl, params.format(timestamp))
        content = json.loads(content)
        for qa in set(re.findall('/question/([0-9]*)/answer/([0-9]*)', content['msg'][1])):
            sys.stdout.write('{0} {1}\n'.format(qa[0], qa[1]))
        sys.stdout.flush()
        # analyze the last timestamp
        remainingMsgNum = int(content['msg'][0])
        if remainingMsgNum < 20:
            break
        timestamp = int(re.findall('data-time="([^"]*)"', content['msg'][1])[-1])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("""
Usage: {0} <user id> 
Crawl zhihu to get the user's activities. The credential will be read from credential.py, and the output will be written on stdout.

Example usage: {0} grapeot | tee grapeot.txt
""".format(sys.argv[0]))
        sys.exit(-1)

    crawlTimeline(sys.argv[1])
