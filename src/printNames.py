# -*- coding: utf-8 -*-

""" Print all the userids with crawling history more than the specified days """
from pymongo import MongoClient
import sys, time

def printNames(days=3):
    client = MongoClient()
    targetTimeStamp = int(time.time()) - days * 24 * 3600
    users = client['zhihu']['users'].find({ 'lastCrawlTimestamp': { '$lt': targetTimeStamp } })
    for user in users:
        print user['name']

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print """
Usage: {0} <days>
Print all the userids with crawling history more than the specified days.

Example: python {0} 3
""".format(sys.argv[0])
        sys.exit(-1)

    printNames(int(sys.argv[1]))
