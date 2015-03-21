from pymongo import MongoClient

client = MongoClient()
questions = client['zhihu']['questions']

# find all top questions
topQuestions = [y for x in client['zhihu']['topics'].find({ 'topQuestionIds': { '$exists': 1 } }, { 'topQuestionIds': 1 }) for y in x['topQuestionIds'] ]
print len(topQuestions), ' top questions are found.'
topQuestions = set(topQuestions)
print len(topQuestions), ' top questions are found after deduplication.'
# find authors 
def findAuthor(qid):
    q = client['zhihu']['questions'].find_one({ 'id': qid, 'topAnswerIds': { '$exists' : 1 } })
    answerId = int(q['topAnswerIds'][0]) if (q and 0 != len(q['topAnswerIds'])) else None
    if answerId is None:
        return []
    answer = client['zhihu']['answers'].find_one({'id': answerId})
    return [] if answer is None else [answer['author']]
authors = [y for qid in topQuestions for y in findAuthor(qid)]
print len(authors), ' authors are found.'

# figure out the authors to be added to the database
oldAuthors = [y['name'] for y in client['zhihu']['users'].find()]
authorsToAdd = set(authors) - set(oldAuthors)
print len(authorsToAdd), ' authors will be added.'
file('../dat/authors.txt', 'w').write('\n'.join([x for x in authorsToAdd]).encode('utf-8'))
print len(authorsToAdd), 'authors has been serialized to ../dat/authors.txt'

# add the authors to the database
print 'Add to the database? (y/n)',
choice = raw_input()
if 'y' == choice or 'Y' == choice:
    for a in authorsToAdd:
        client['zhihu']['users'].insert({
            'name': a,
            'lastCrawlTimestamp': 0,
            'likes': []
        });
    print 'done.'
