python ./printQuestions.py 30 | xargs -P 20 -I{} -n 1 bash -c 'python ./crawlQuestion.py {}'
