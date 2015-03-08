# -*- coding: utf-8 -*-

import sys 
import re
import Queue
import util

def crawlAUser(userid):
    """ Crawl the followees page of the given userid, and return the crawled result """
    # first stage: get hash_id and total number
    content = util.getZhihu('http://www.zhihu.com/people/{0}/followees'.format(userid))
    hashid = re.search('hash_id&quot;: &quot;([^&]*)&quot;', content).group(1)
    totalNum = int(re.search('<strong>(\d+)</strong><label> 人</label>', content).group(1))
    # second stage: simulate scrolling down the page
    for i in range(20, totalNum, 20):
        contenttmp = util.postZhihu( 'http://www.zhihu.com/node/ProfileFolloweesListV2'.format(userid), 
            'method=next&params=%7B%22offset%22%3A{0}%2C%22order_by%22%3A%22created%22%2C%22hash_id%22%3A%22{1}%22%7D&_xsrf=c4b07884cfea379e46cdcb89fcf08cc4'.format(i, hashid))
        content = content + re.sub(r'\\', '', contenttmp)
    return content

def extractFollowees(userid):
    """ 
    Extract the followees of the given user, and output a set of the user ids of the followees.
    """
    content = crawlAUser(userid)
    return set(re.findall('/people/([^/"]*)"', content))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write("""
Usage: {0} <init user id> <expected num>
Crawl zhihu to get a user list, starting from the init user id, and end with the user number meets the expected num.
The credential will be read from credential.py, and the output will be written on stdout.

Example usage: {0} grapeot 100 | tee users.txt
""".format(sys.argv[0]))
        sys.exit(-1)

    userid = sys.argv[1]
    expectedNum = int(sys.argv[2])

    # a BFS framework
    userset = set()
    q = Queue.Queue()
    q.put(userid)
    while len(userset) < expectedNum:
        userid = q.get()
        crawlAUser(userid)
        followees = extractFollowees(userid)
        # output
        for f in followees - userset:
            sys.stdout.write(f + '\n')
            sys.stdout.flush()
            q.put(f)
        userset = userset | followees
