# -*- coding: utf-8 -*-

""" Print all the question ids which don't appear in the database """
import time, sys
from pymongo import MongoClient

def printQuestions(days):
    client = MongoClient()
    targetTimeStamp = int(time.time()) - days * 24 * 3600
    setQidsFromUsers = set( [ y['qid'] for x in client['zhihu']['users'].find() for y in x['likes'] ] )
    setQidsFromQuestions = set( [x['id'] for x in client['zhihu']['questions'].find() if x['lastCrawlTimestamp'] < targetTimeStamp ] )
    for qid in setQidsFromUsers - setQidsFromQuestions:
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
