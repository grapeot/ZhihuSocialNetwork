python ./printTopics.py 30 | xargs -n 1 -I{} -P 15 bash -c 'python ./crawlTopicTopQuestions.py "{}"'
