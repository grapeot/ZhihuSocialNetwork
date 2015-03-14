# -*- coding: utf-8 -*-

""" Print all the userids with crawling history more than the specified days """
from pymongo import MongoClient
import sys, time

def printNames(days=3):
    client = MongoClient()
    users = client['zhihu']['users'].find()
    userstmp = [ {
        'name': x['name'], 
        'mtimestamp': 0 if 'likes' not in x else
            0 if len(x['likes']) == 0 else
                max([int(y['timestamp']) for y in x['likes']])
        } for x in users]
    currentTime = int(time.time())
    users = [x['name'] for x in userstmp if currentTime - x['mtimestamp'] > days * 24 * 3600]
    for user in users:
        print user

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print """
Usage: {0} <days>
Print all the userids with crawling history more than the specified days.

Example: python {0} 3
""".format(sys.argv[0])
        sys.exit(-1)

    printNames(int(sys.argv[1]))
