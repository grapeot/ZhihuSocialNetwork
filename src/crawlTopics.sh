python printTopics.py 30 | xargs -I{} -n 1 -P 15 bash -c 'python ./crawlTopic.py "{}"'
