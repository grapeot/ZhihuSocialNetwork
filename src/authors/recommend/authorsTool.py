from pymongo import MongoClient
from collections import Counter
from multiprocessing import Pool, Manager
import sys, os

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

# returns the distance between two topicFeatures, stored as dictionaries
def userDist(dict1, dict2):
    commonKeys = [k for k in dict1 if k in dict2]
    return sum([dict1[k] + dict2[k] for k in commonKeys])

def updateSimilarUserParallel(f, features):
    if 'interestedUsers' in client['zhihu']['users'].find_one({'name': f['name']}):
        return
    distances = [{'name': x['name'], 
        'dist': userDist(f['feature'], x['feature'])
        } for x in features]
    distances = sorted(distances, key=lambda x: x['dist'], reverse=True)
    client['zhihu']['users'].update({'name': f['name']}, {'$set': {'interestedUsers': [x['name'] for x in distances[1:11]]}})
    print f['name'].encode('utf-8')

def updateSimilarUsers():
    # check whether topic features have been extracted for all the users
    client = MongoClient()
    manager = Manager()
    features = manager.list([{
        'name': x['name'],
        'feature': x['topicFeature'] 
        } for x in client['zhihu']['users'].find({}, {'topicFeature': 1, 'name': 1})])
    p = Pool(4)
    for f in features:
        if 'interestedUsers' in client['zhihu']['users'].find_one({'name': f['name']}):
            continue
        p.apply_async(updateSimilarUserParallel, args=(f, features))

def updateSimilarUser(userid):
    # check whether topic features have been extracted for all the users
    client = MongoClient()
    features = [{
        'name': x['name'],
        'feature': x['topicFeature'] 
        } for x in client['zhihu']['users'].find({}, {'topicFeature': 1, 'name': 1})]
    f = client['zhihu']['users'].find_one({'name': userid},{'topicFeature': 1, 'name': 1})
    f = {'name': f['name'], 'feature': f['topicFeature']}
    distances = [{'name': x['name'], 
        'dist': userDist(f['feature'], x['feature'])
        } for x in features]
    distances = sorted(distances, key=lambda x: x['dist'], reverse=True)
    client['zhihu']['users'].update({'name': f['name']}, {'$set': {'interestedUsers': [x['name'] for x in distances[1:11]]}})

# extract the topic feature for a user
def extractAndStoreTopicFeature(userid):
    client = MongoClient()
    user = client['zhihu']['users'].find_one({'name': userid}, {'likes': 1})
    # assume we already find a user
    qids = set([x['qid'] for x in user['likes']])
    topicIdLists = [client['zhihu']['questions'].find_one({'id': qid}) for qid in qids]
    tmpList = [x['topicIds'] for x in topicIdLists if x is not None]
    topicIds = [y for x in tmpList for y in x]
    hist = Counter(topicIds)
    # normalize 
    #topicIdTitleDict = {x['id']: x['title'] for x in client['zhihu']['topics'].find({}, {'id': 1, 'title': 1})}
    sumCount = float(sum([hist[x] for x in hist]))
    hist2 = {str(x): hist[x] / sumCount for x in hist}
    client['zhihu']['users'].update({'name': userid}, {'$set': {'topicFeature': hist2}})
    return hist2

def findFavTopics(userid):
    client = MongoClient()
    user = client['zhihu']['users'].find_one({'name': userid}, {'likes': 1})
    # assume we already find a user
    qids = set([x['qid'] for x in user['likes']])
    topicIdLists = [client['zhihu']['questions'].find_one({'id': qid}) for qid in qids]
    tmpList = [x['topicIds'] for x in topicIdLists if x is not None]
    topicIds = [y for x in tmpList for y in x]
    hist = Counter(topicIds)
    topicIds = hist.most_common(5)
    return [{'id': x[0], 'count': x[1], 'title': client['zhihu']['topics'].find_one({'id': x[0]})['title']} for x in topicIds]

def findTopAnswerIdsInTopics(topicids):
    client = MongoClient()
    topQuestionIds = [client['zhihu']['topics'].find_one({'id': topicid})['topQuestionIds'] for topicid in topicids]
    topQuestionIds = [x if len(x) < 50 else x[0:50] for x in topQuestionIds]
    topQuestionIds = [y for x in topQuestionIds for y in x]  # flatten the data structure. now it becomes a list
    topQuestionIds = list(set(topQuestionIds))  # deduplication
    topAnswerIds = [client['zhihu']['questions'].find_one({'id': qid})['topAnswerIds'] for qid in topQuestionIds]
    topAnswerIds = [x if len(x) < 2 else x[0:2] for x in topAnswerIds]
    topAnswerIds = [y for x in topAnswerIds for y in x]
    return topAnswerIds

def findInterestedAnswers(userid):
    topicids = [x['id'] for x in findFavTopics(userid)]
    topAnswerIdSet = set(findTopAnswerIdsInTopics(topicids))
    # filter out the answers that has already been liked
    client = MongoClient()
    user = client['zhihu']['users'].find_one({'name': userid}, {'likes': 1})
    likedAnswerIdSet = set([x['aid'] for x in user['likes']])
    candidateAnswerIds = list(topAnswerIdSet - likedAnswerIdSet)
    # sort 
    candidateAnswers = [{'id': x, 'upvote': client['zhihu']['answers'].find_one({'id': x})['upvote']} for x in candidateAnswerIds]
    sortedAnswers = sorted(candidateAnswers, key=lambda x: x['upvote'], reverse=True)
    interestedAnswers = sortedAnswers[0:10];
    # store in mongodb
    client['zhihu']['users'].update({'name': userid}, {'$set': {'interestedAnswers': interestedAnswers}})
    return interestedAnswers

# generate html files at the given folder
def generateHtmlFiles(folder):
    # get users that don't have an html file in the folder
    client = MongoClient()
    names = [x for x in client['zhihu']['users'].find({
        'interestedTopics': { '$exists': 1 },
        'interestedAnswers': { '$exists': 1 },
        'interestedUsers': { '$exists': 1 }
    }, 
    {
        'interestedTopics': 1,
        'interestedAnswers': 1,
        'interestedUsers': 1,
        'name': 1
    })]
    existingFiles = set([x.replace('.html', '') for x in os.listdir(folder)])
    names = [x for x in names if x['name'] not in existingFiles]
    # generate the files in parallel
    for x in names:
        generateHtmlFile(folder, x)
    #p = Pool(4)
    #for x in names:
        #p.apply(generateHtmlFile, (folder, x))
    pass

# userid is a dictionary with name, interestedTopics, interestedAnswers as fields
templateText = file('template.jinja').read().decode('utf-8')
def generateHtmlFile(folder, user):
    client = MongoClient()
    name = user['name']
    interestedTopics = user['interestedTopics']
    interestedAnswers = user['interestedAnswers']
    interestedUsers = user['interestedUsers']
    # topics
    topicNames = [{
        'title': x['title'],
        'id': x['id']
        } for x in interestedTopics]
    # answers
    answerIds = [{
        'aid': x['id'],
        'qid': client['zhihu']['answers'].find_one({'id': x['id']})['qid']
        } for x in interestedAnswers]
    answerIds = [{'aid': x['aid'], 'qid': x['qid'],
        'qtitle': client['zhihu']['questions'].find_one({'id': x['qid']})['title']
        } for x in answerIds]
    # users
    # invoke jinja
    from jinja2 import Template
    template = Template(templateText)
    renderedText = template.render({'topics': topicNames, 'answerIds': answerIds, 'users': interestedUsers})
    with file('{0}/{1}.html'.format(folder, name.encode('utf-8')), 'w') as fp:
        fp.write(renderedText.encode('utf-8'))
    print name.encode('utf-8')

if __name__ == '__main__':
    if 3 != len(sys.argv):
        sys.stderr.write("""Usage: {0} <op> <userid>
Perform certain operations on userid.

op can be:
* feature: extract the topic feature for the given userid, and store the result in mongodb.
* answer: extract the possibly interested answers and store the result in mongodb.
* topic: extract the possibly interested topics and store the result in mongodb.
* user: extract the possibly interested users and store the result in mongodb.
* html: generate html files at the given folder.
""".format(sys.argv[0]))
        sys.exit(-1)

    if (sys.argv[1] == 'feature'):
        extractAndStoreTopicFeature(sys.argv[2])
        print sys.argv[2]
    elif (sys.argv[1] == 'answer'):
        findInterestedAnswers(sys.argv[2])
        print sys.argv[2]
    elif (sys.argv[1] == 'topic'):
        interestedTopics = findFavTopics(sys.argv[2])
        # store in mongodb
        client = MongoClient()
        client['zhihu']['users'].update({'name': sys.argv[2]}, {'$set': {'interestedTopics': interestedTopics}})
        print sys.argv[2]
    elif (sys.argv[1] == 'user'):
        updateSimilarUsers()
    elif sys.argv[1] == 'html':
        generateHtmlFiles(sys.argv[2])
