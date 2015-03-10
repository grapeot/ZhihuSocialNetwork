from pymongo import MongoClient

client = MongoClient()
users = client['zhihu']['users']
for user in users.find():
    print user['name']
