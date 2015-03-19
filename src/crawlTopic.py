# -*- coding: utf-8 -*-

import util
import sys, time, re
from pymongo import MongoClient

def crawlTopic(tid):
    """ Crawl the topics of the question, and store the result in the database. """
    print '[{0}] starts.'.format(tid)
    apiurl = 'http://www.zhihu.com/topic/{0}'.format(tid)
    client = MongoClient()
    content = util.getZhihu(apiurl.format(tid), includeCookie=False)

    title = re.search(r'id="zh-topic-title">\s*<h1[^>]*>(.*?)</h1>', content).group(1)
    followerNumber = int(re.search(r'<strong>(\d+)</strong> 人关注了该话题', content).group(1))
    match = re.search(r'<div class="zm-editable-content"[^>]*>(.*?)</div>', content)
    description = match.group(1) if match else ''
    timestamp = int(time.time())
    toInsert = {
        'id': int(tid),
        'title': title,
        'lastCrawlTimestamp': timestamp,
        'followerNumber': followerNumber,
        'description': description
    }
    #print 'toInsert = ', toInsert
    client['zhihu']['topics'].insert(toInsert)
    print '[{0}] finishes.'.format(tid)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("""
Usage: {0} <tid>
Crawl zhihu to get the basic information of the topic. The output will be written to mongodb.

Example usage: {0} 19554298
""".format(sys.argv[0]))
        sys.exit(-1)

    crawlTopic(sys.argv[1])
