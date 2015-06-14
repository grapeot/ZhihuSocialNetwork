# -*- coding: utf-8 -*-

""" Print all the question ids which don't appear in the database """
import time, sys
from pymongo import MongoClient

def printQuestions(days):
    client = MongoClient()
    targetTimeStamp = int(time.time()) - days * 24 * 3600
    setQidsFromUsers = set( [ y['qid'] for x in client['zhihu']['users'].find({'likes': {'$exists': 1}}, {'likes': 1}) for y in x['likes'] ] )
    setQidsFromTopicTopQuestions = set( [ y for x in client['zhihu']['topics'].find({'topQuestionIds': {'$exists': 1}}, {'topQuestionIds': 1}) for y in x['topQuestionIds'] ] )
    setQidsFromQuestions = set( [x['id'] for x in client['zhihu']['questions'].find({'lastCrawlTimestamp': {'$gt': targetTimeStamp} })] )
    setQidsInvalid = set( [x['id'] for x in client['zhihu']['failedQuestions'].find()] )
    for qid in (setQidsFromUsers | setQidsFromTopicTopQuestions) - setQidsFromQuestions - setQidsInvalid:
        print qid

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print """
Usage: {0} <days>
Print ids of the questions that were crawled <days> days before.
Example: {0} 3
""".format(sys.argv[0])
        sys.exit(-1)

    printQuestions(float(sys.argv[1]))
