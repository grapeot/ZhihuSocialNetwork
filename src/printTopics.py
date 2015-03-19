# -*- coding: utf-8 -*-

""" Print all the question ids which don't appear in the database """
import time, sys
from pymongo import MongoClient

def printQuestions(days):
    client = MongoClient()
    targetTimeStamp = int(time.time()) - days * 24 * 3600
    setTidsFromQuestions = set( [ y for x in client['zhihu']['questions'].find({}, {'topicIds': 1}) for y in x['topicIds'] ] )
    setTidsFromTopics = set( [x['id'] for x in client['zhihu']['topics'].find({}, {'id': 1, 'lastCrawlTimestamp': 1}) if x['lastCrawlTimestamp'] > targetTimeStamp ] )
    for tid in setTidsFromQuestions - setTidsFromTopics:
        print tid

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print """
Usage: {0} <days>
Print ids of the topics that were crawled <days> days before.
Example: {0} 3
""".format(sys.argv[0])
        sys.exit(-1)

    printQuestions(float(sys.argv[1]))
