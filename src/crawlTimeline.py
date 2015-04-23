# -*- coding: utf-8 -*-

import util
import sys, time, re, json
from pymongo import MongoClient

def crawlTimeline(userid):
    """ Crawl the timeline of the user, and store the result in mongodb. """
    apiurl = 'http://www.zhihu.com/people/{0}/activities'.format(userid)
    params = 'start={0}&_xsrf=acbf6400c44e8fd76b2695ab83e36145'
    timestamp = int(time.time())
    mongoToWrite = []

    # determine the latest timestamp.
    # we don't need to crawl after reaching the this one
    client = MongoClient()
    users = client['zhihu']['users']
    user = users.find_one({'name': userid})
    if 'likes' not in user:
        user.update({'likes': []})
    latestTimestamp = max([int(x['timestamp']) for x in user['likes']]) if len(user['likes']) != 0 else 0
    latestTimestamp2 = min([int(x['timestamp']) for x in user['likes']]) if len(user['likes']) != 0 else 0

    oldTimestamp = 0
    answers = None
    while True:
        content = ''
        try:
            thisParam = params.format(timestamp)
            content = util.postZhihu(apiurl, thisParam, False)
        except:
            break
        if re.search('<title>403: Forbidden', content):
            sys.stderr.write('Error: 403')
            sys.exit(-1)
        content = json.loads(content)
        content['msg'][1] = content['msg'][1].encode('utf-8')
        answers = ''
        answers = re.findall(r'data-time="(\d+)"[^>]*>\s*<span[^>]*>[^<]*</span>\s*<div[^>]*>[^<]*<a[^>]*>[^<]*</a>[^<]*<a class="question_link" target="_blank" href="/question/(\d+)/answer/(\d+)">', content['msg'][1])
        if len(answers) == 0:
            # the "not shown to users outside zhihu" has been toggled
            answers = re.findall(r'data-time="(\d+)"[^>]*>\s*<span[^>]*>[^<]*</span>\s*<div[^>]*>[^<]*知乎用户[^<]*\s*<a class="question_link" target="_blank" href="/question/(\d+)/answer/(\d+)">', content['msg'][1])
        mongoToWrite += [{'timestamp': int(x[0]), 'qid': int(x[1]), 'aid': int(x[2])} for x in answers] 
        #print mongoToWrite
        # whether to terminate the crawling
        remainingMsgNum = int(content['msg'][0])
        earliestTimestamp = min([int(x['timestamp']) for x in mongoToWrite]) if len(mongoToWrite) > 0 else 0
        #print 'ts = ', timestamp, ' oldts = ', oldTimestamp, ' latest = ', latestTimestamp, ' earlest = ', earliestTimestamp
        if remainingMsgNum == 0:
            #print 'break because of remainingMsgNum = 0'
            break
        if earliestTimestamp < latestTimestamp:
            print '[{0}] early termination at {1}'.format(userid, latestTimestamp)
            print '[{0}] checking before {1}...'.format(userid, latestTimestamp2)
            oldTimestamp = timestamp
            timestamp = latestTimestamp2
            latestTimestamp = 0
            if oldTimestamp == timestamp:
                #print 'break because oldTimestamp == timestamp (== {0})'.format(timestamp)
                break
            continue
        oldTimestamp = timestamp
        timestamp = int(re.findall('data-time="([^"]*)"', content['msg'][1])[-1])
        if oldTimestamp == timestamp:
            #print 'break because oldTimestamp == timestamp (== {0})'.format(timestamp)
            break
        sys.stdout.write('.')
        sys.stdout.flush()

    # update the database
    # do deduplication
    oldTimestamps = set([x['timestamp'] for x in user['likes']])
    mongoToWrite = [x for x in mongoToWrite if x['timestamp'] not in oldTimestamps]
    user['likes'] += mongoToWrite
    user['lastCrawlTimestamp'] = int(time.time())
    users.update({'name': userid}, user)
    sys.stdout.write('[{1}] {0} new entries written to the database.\n'.format(len(mongoToWrite), userid))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("""
Usage: {0} <user id> 
Crawl zhihu to get the user's activities. The credential will be read from credential.py, and the output will be written to mongodb.

Example usage: {0} grapeot 
""".format(sys.argv[0]))
        sys.exit(-1)

    crawlTimeline(sys.argv[1])
