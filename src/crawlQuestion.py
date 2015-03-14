# -*- coding: utf-8 -*-

import util
import sys, time, re
from pymongo import MongoClient

def crawlQuestion(qid):
    """ Crawl the topics of the question, and store the result in the database. """
    apiurl = 'http://www.zhihu.com/question/{0}'.format(qid)
    client = MongoClient()
    content = util.getZhihu(apiurl.format(qid), includeCookie=False)
    topicids = re.findall(r'"/topic/(\d+)"', content)
    timestamp = int(time.time())
    title = re.search('<h2 class="zm-item-title zm-editable-content">([^<]*)', content).group(1).strip()
    print { 'id': qid, 'title': title, 'topicids': topicids, 'lastCrawlTimestamp': timestamp }
    client['zhihu']['questions'].insert_one({ 'id': qid, 'title': title, 'topicids': topicids, 'lastCrawlTimestamp': timestamp })

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("""
Usage: {0} <qid>
Crawl zhihu to get the basic information of the question. The output will be written to mongodb.

Example usage: {0} 28339620
""".format(sys.argv[0]))
        sys.exit(-1)

    crawlQuestion(sys.argv[1])
