#encoding: utf-8

import multiprocessing as mp
from pymongo import MongoClient
import sys, re
import jieba  
import jieba.posseg as pseg  

client = MongoClient()
def cut(answer):
    sys.stdout.write('.')
    sys.stdout.flush()
    c = answer['content']
    c = re.sub(r'[\w<>/=\\\s\+-\?，。？（）]', '', c)
    newContent = ' '.join([x.word for x in pseg.cut(c)])
    aid = answer['id']
    return aid, newContent
    #bulk.update({'id': aid}, {'$set': {'segContent': newContent, 'segmented': True}})

# get the corpus
def segmentText():
    # serial version
    #for a in answers:
        #cut(a)
    # parallel version
    batchSize = 100
    answers = list(client['zhihu']['answers'].find({'content': {'$exists': 1}, 'segmented': False}, {'content': 1, 'id': 1}).limit(batchSize))
    while len(answers):
        bulk = client['zhihu']['answers'].initialize_ordered_bulk_op()
        pool = mp.Pool(processes=16)
        result = pool.map(cut, answers)
        for r in result:
            bulk.find({'id': r[0]}).update({'$set': {'segContent': r[1], 'segmented': True}})
        bulk.execute()
        print '*'
        answers = list(client['zhihu']['answers'].find({'content': {'$exists': 1}, 'segmented': False}, {'content': 1, 'id': 1}).limit(batchSize))

if __name__ == '__main__':
    segmentText()
