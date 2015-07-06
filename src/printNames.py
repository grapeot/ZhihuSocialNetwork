# -*- coding: utf-8 -*-

""" Print all the userids with crawling history more than the specified days """
from pymongo import MongoClient
import sys, time

def printNamesForFeature():
    client = MongoClient()
    users = client['zhihu']['users'].find({'topicFeature': {'$exists': 0}})
    for user in users:
        print user['name'].encode('utf-8')

def printNamesForTopic():
    client = MongoClient()
    users = client['zhihu']['users'].find({'interestedTopics': {'$exists': 0}})
    for user in users:
        print user['name'].encode('utf-8')

def printNamesForAnswer():
    client = MongoClient()
    users = client['zhihu']['users'].find({'interestedAnswers': {'$exists': 0}})
    for user in users:
        print user['name'].encode('utf-8')

def printNames(days=3):
    client = MongoClient()
    targetTimeStamp = int(time.time()) - days * 24 * 3600
    users = client['zhihu']['users'].find({ 'lastCrawlTimestamp': { '$lt': targetTimeStamp } })
    for user in users:
        print user['name'].encode('utf-8')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print """
Usage: {0} <-feature|-answer|days> 
Print all the userids with crawling history more than the specified days.
When -feature is specified, will print all the names without a topicFeature
When -answer is specified, will print all the names without an interestedAnswers
When -topic is specified, will print all the names without an interestedTopics

Example: python {0} 3
Example: python {0} -feature
Example: python {0} -answer
Example: python {0} -topic
""".format(sys.argv[0])
        sys.exit(-1)

    if sys.argv[1] == '-feature':
        printNamesForFeature()
    elif sys.argv[1] == '-answer':
        printNamesForAnswer()
    elif sys.argv[1] == '-topic':
        printNamesForTopic()
    else:
        printNames(int(sys.argv[1]))
