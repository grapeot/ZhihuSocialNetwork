# -*- coding: utf-8 -*-

import util
import re
import sys
from pymongo import MongoClient

def filterUserId(id):
    content = util.getZhihu('http://www.zhihu.com/people/{0}'.format(id))
    if re.search('<strong>你似乎来到了没有知识存在的荒原...</strong>', content) is None:
        print id
        # add it to mongodb
        client = MongoClient()
        client['zhihu']['users'].update({'name': id}, {'$set': {'id': id, 'lastCrawlTimestamp': 0}}, upsert=True)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("""{0} <userid>
Print the userid if the user exists in Zhihu. Otherwise return directly.
If the user exists, we also add it into mongodb.
""".format(sys.argv[0]))
        sys.exit(-1)

    filterUserId(sys.argv[1])
