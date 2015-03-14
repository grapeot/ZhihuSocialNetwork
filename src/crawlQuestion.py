# -*- coding: utf-8 -*-

import util
import sys, time, re
from pymongo import MongoClient

def crawlQuestion(qid):
    """ Crawl the topics of the question, and store the result in the database. """
    print '[{0}] starts.'.format(qid)
    apiurl = 'http://www.zhihu.com/question/{0}'.format(qid)
    client = MongoClient()
    content = util.getZhihu(apiurl.format(qid), includeCookie=False)

    # process the question itself
    topicids = re.findall(r'"/topic/(\d+)"', content)
    timestamp = int(time.time())
    title = re.search('<h2 class="zm-item-title zm-editable-content">([^<]*)', content).group(1).strip()
    topAnswerIds = list(set(re.findall('"/question/{0}/answer/(\d+)"'.format(qid), content)))
    toInsert = { 'id': qid, 'title': title, 'topicIds': topicids, 'lastCrawlTimestamp': timestamp, 'topAnswerIds': topAnswerIds }
    client['zhihu']['questions'].update({ 'id': qid }, toInsert, upsert=True)

    # process the answers
    upvotes = [int(x) for x in re.findall(r'data-votecount="(\d+)"', content)]
    toInsert = [{ 'id': aid, 'qid': qid, 'lastQuestionCrawlTimestamp': timestamp, 'upvote': upvote }
        for aid, upvote in zip(topAnswerIds, upvotes)]
    for r in toInsert:
        client['zhihu']['answers'].update({ 'id': r['id'] }, r, upsert=True)
    print '[{0}] complete, {1} answers updated.'.format(qid, len(upvotes))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("""
Usage: {0} <qid>
Crawl zhihu to get the basic information of the question. The output will be written to mongodb.

Example usage: {0} 28339620
""".format(sys.argv[0]))
        sys.exit(-1)

    crawlQuestion(sys.argv[1])
