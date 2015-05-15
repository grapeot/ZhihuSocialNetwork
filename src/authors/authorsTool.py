from pymongo import MongoClient
from collections import Counter
import sys

def generateHoursFigure(user):
    import pytz
    import numpy as np
    import matplotlib.pyplot as pp
    import scipy.stats
    from datetime import datetime
    # fetch information from the mongodb
    client = MongoClient()
    likes = client['zhihu']['users'].find_one({'name': user}, {'likes': 1})
    # kernel density estimation
    tz = pytz.timezone('Asia/Hong_Kong')
    timestamps = [datetime.fromtimestamp(x['timestamp'], tz) for x in likes['likes']]
    hours = [x.hour + float(x.minute) / 60 for x in timestamps]
    xs = np.asarray([float(x) / 100 for x in xrange(0, 2400)])
    ys = np.zeros(xs.shape)
    for h in hours:
        kernel = scipy.stats.norm(h, 0.5)
        ys += kernel.pdf(xs)
    ys /= max(ys)
    pp.figure()
    pp.bar(xs, ys, width=0.01, edgecolor='none', color='#8888ff')
    pp.xlim((0, 24))
    pp.xticks(np.arange(min(xs), max(xs) + 1, 2.0))
    pp.xlabel('Time')
    pp.ylabel('Relative Frequency')
    pp.savefig('{0}_timeline.png'.format(user), bbox='tight')
    return xs, ys

def findFavTopics(userid):
    client = MongoClient()
    user = client['zhihu']['users'].find_one({'name': userid}, {'likes': 1})
    # assume we already find a user
    qids = set([x['qid'] for x in user['likes']])
    topicIds = [x for qid in qids for x in client['zhihu']['questions'].find_one({'id': qid})['topicIds']]
    hist = Counter(topicIds)
    topicIds = hist.most_common(5)
    return [(x[0], x[1], client['zhihu']['topics'].find_one({'id': x[0]})['title']) for x in topicIds]

if __name__ == '__main__':
    if 2 != len(sys.argv):
        sys.stderr.write("""Usage: {0} <userid>
Output the title of favorite topics of the users.
""".format(sys.argv[0]))
        sys.exit(-1)

    for topic in findFavTopics(sys.argv[1]):
        print topic[0], topic[1], topic[2].encode('utf-8')
