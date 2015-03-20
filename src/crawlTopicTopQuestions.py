# -*- coding: utf-8 -*-

import util
import sys, re, time
from pymongo import MongoClient

def crawlTopicTopQuestions(tid):
    """ Crawl the topic for the top questions """
    print '[{0}] starts.'.format(tid)
    apiurl = 'http://www.zhihu.com/topic/{0}/top-answers'.format(tid)
    content = util.getZhihu(apiurl.format(tid), includeCookie=False)
    client = MongoClient()

    # regular processing
    title = re.search(r'id="zh-topic-title">\s*<h1[^>]*>(.*?)</h1>', content).group(1)
    followerNumber = 0 if re.search('还没有人关注该话题', content) else int(re.search(r'<strong>(\d+)</strong> 人关注了该话题', content).group(1))
    match = re.search(r'<div class="zm-editable-content"[^>]*>(.*?)</div>', content)
    description = match.group(1) if match else ''
    timestamp = int(time.time())

    # initialize the top-question crawling
    questionIds = [int(x) for x in re.findall(r'target="_blank" href="/question/(\d+)"', content)]
    qidsToWrite = questionIds

    match = re.search(r'>(\d+)</a></span>\s*<span><a href="\?page=2">下一页</a></span>', content)
    lastPage = int(match.group(1)) if match else 0
    sys.stdout.write('.')
    sys.stdout.flush()
    # crawl page by page
    for p in range(2, lastPage + 1):
        content = util.getZhihu(apiurl + '?page={0}'.format(p), includeCookie=False)
        questionIds = [int(x) for x in re.findall(r'target="_blank" href="/question/(\d+)"', content)]
        qidsToWrite += questionIds
        sys.stdout.write('.')
        sys.stdout.flush()
    toInsert = {
        'id': int(tid),
        'title': title,
        'lastCrawlTimestamp': timestamp,
        'followerNumber': followerNumber,
        'description': description,
        'topQuestionIds': qidsToWrite
    }
    print '[{0}] finishes. {1} questions updated.'.format(tid, len(qidsToWrite))
    client['zhihu']['topics'].insert(toInsert)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("""
Usage: {0} <qid>
Crawl zhihu to get the basic information of the question. The output will be written to mongodb.

Example usage: {0} 28339620
""".format(sys.argv[0]))
        sys.exit(-1)

    crawlTopicTopQuestions(sys.argv[1])
