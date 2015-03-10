# -*- coding: utf-8 -*-

import util
import sys, time, re, json
from pymongo import MongoClient

def crawlTimeline(userid):
    """ Crawl the timeline of the user, and return the string. """
    apiurl = 'http://www.zhihu.com/people/{0}/activities'.format(userid)
    params = 'start={0}&_xsrf=c4b07884cfea379e46cdcb89fcf08cc4'
    timestamp = int(time.time())
    mongoToWrite = []

    # determine the latest timestamp.
    # we don't need to crawl after reaching the this one
    client = MongoClient()
    users = client['zhihu']['users']
    user = users.find_one({'name': userid})
    if 'likes' not in user:
        user.update({'likes': []})
    latestTimestamp = max([int(x['timestamp']) for x in user['likes']])

    while True:
        content = util.postZhihu(apiurl, params.format(timestamp))
        content = json.loads(content)
        answers = re.findall(r'data-time="(\d+)"[^>]*>\s<span[^>]*>[^<]*</span>\s<div[^>]*>\s<a[^>]*>[^<]*</a>[^<]*<a class="question_link" target="_blank" href="/question/(\d+)/answer/(\d+)">', content['msg'][1])
        mongoToWrite += [{'timestamp': x[0], 'qid': x[1], 'aid': x[2]} for x in answers] 
        # whether to terminate the crawling
        remainingMsgNum = int(content['msg'][0])
        earliestTimestamp = min([int(x['timestamp']) for x in mongoToWrite])
        if remainingMsgNum < 20 or earliestTimestamp < latestTimestamp:
            break
        timestamp = int(re.findall('data-time="([^"]*)"', content['msg'][1])[-1])

    # update the database
    # do deduplication
    oldTimestamps = set([x['timestamp'] for x in user['likes']])
    mongoToWrite = [x for x in mongoToWrite if x['timestamp'] not in oldTimestamps]
    user['likes'] += mongoToWrite
    users.update({'name': userid}, user)
    sys.stdout.write('[{1}] {0} new entries written to the database.\n'.format(len(mongoToWrite), userid))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("""
Usage: {0} <user id> 
Crawl zhihu to get the user's activities. The credential will be read from credential.py, and the output will be written on stdout.

Example usage: {0} grapeot | tee grapeot.txt
""".format(sys.argv[0]))
        sys.exit(-1)

    crawlTimeline(sys.argv[1])
