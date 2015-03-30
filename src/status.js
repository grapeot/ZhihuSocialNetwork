conn = new Mongo();
db = conn.getDB('zhihu');
print('authors: ' + db.users.count() +
        ' questions: ' + db.questions.count() + 
        ' answers: ' + db.answers.count() + 
        ' topic: ' + db.topics.count() +
        //'\ncrawledAnswers: ' + db.answers.find({'content': {'$exists': 1}}).count());// +
        ' segmentedAnswers: ' + db.answers.count({'segmented':true}));
