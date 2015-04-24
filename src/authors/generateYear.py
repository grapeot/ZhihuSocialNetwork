from pymongo import MongoClient
import pytz
import numpy as np
import matplotlib.pyplot as pp
import scipy.stats
from datetime import datetime
import sys

def generateJadeForTimeline(user, year):
    # fetch information from the mongodb
    client = MongoClient()
    likes = client['zhihu']['users'].find_one({'name': user}, {'likes': 1})
    # kernel density estimation
    tz = pytz.timezone('Asia/Hong_Kong')
    timestamps = [datetime.fromtimestamp(x['timestamp'], tz) for x in likes['likes']]
    hours = [x.hour + float(x.minute) / 60 for x in timestamps if x.year == year]
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
    pp.savefig('{0}_{1}.png'.format(user, year), bbox='tight')
    return xs, ys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print """Usage: {0} <userid>
Generate a jade file for the basic information of the given zhihu user id, and print it to stdout
Example: python {0} grapeot
""".format(sys.argv[0])
        sys.exit(-1)

    xs, ys = generateJadeForTimeline(sys.argv[1], int(sys.argv[2]))
    sys.stdout.write('.')
