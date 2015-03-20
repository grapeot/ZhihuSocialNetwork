# -*- coding: utf-8 -*-

import util
import sys, re
from pymongo import MongoClient

def crawlTopicTopQuestions(tid):
    """ Crawl the topic for the top questions """
    print '[{0}] starts.'.format(tid)
    apiurl = 'http://www.zhihu.com/topic/{0}/top-answers'.format(tid)
    content = util.getZhihu(apiurl.format(tid), includeCookie=False)
    client = MongoClient()

    # initialize the processing
    qidsToWrite = []
    questionIds = [int(x) for x in re.findall(r'target="_blank" href="/question/(\d+)"', content)]
    def upsertQuestions(qids):
        for qid in qids:
            c = client['zhihu']['questions'].find({'id': qid}).count()
            if 0 == c:
                qidsToWrite.append(qid)
    totalQidNum = upsertQuestions(questionIds)

    match = re.search(r'>(\d+)</a></span>\s*<span><a href="\?page=2">下一页</a></span>', content)
    lastPage = int(match.group(1)) if match else 0
    sys.stdout.write('.')
    # crawl page by page
    for p in range(2, lastPage + 1):
        content = util.getZhihu(apiurl + '?page={0}'.format(p), includeCookie=False)
        questionIds = [int(x) for x in re.findall(r'target="_blank" href="/question/(\d+)"', content)]
        totalQidNum += upsertQuestions(questionIds)
        sys.stdout.write('.')
        sys.stdout.flush()
    topic = client['zhihu']['topics'].find({'id': tid})
    topic['topQuestionIds'] = qidsToWrite
    client['zhihu']['topics'].update({'id': tid}, topic)
    print '[{0}] finishes. {1} questions updated.'.format(tid, len(qidsToWrite))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("""
Usage: {0} <qid>
Crawl zhihu to get the basic information of the question. The output will be written to mongodb.

Example usage: {0} 28339620
""".format(sys.argv[0]))
        sys.exit(-1)

    crawlTopicTopQuestions(sys.argv[1])
