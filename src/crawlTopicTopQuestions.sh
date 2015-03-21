python ./printTopics.py 0.5 | xargs -n 1 -I{} -P 15 bash -c 'python ./crawlTopicTopQuestions.py "{}"'
