# -*- coding: utf-8 -*-

""" Print all the question ids which don't appear in the database """
from pymongo import MongoClient

def printQuestions():
    client = MongoClient()
    setQidsFromUsers = set( [ y['qid'] for x in client['zhihu']['users'].find() for y in x['likes'] ] )
    setQidsFromQuestions = set( [x['id'] for x in client['zhihu']['questions'].find() ] )
    for qid in setQidsFromUsers - setQidsFromQuestions:
        print qid

if __name__ == '__main__':
    printQuestions()
