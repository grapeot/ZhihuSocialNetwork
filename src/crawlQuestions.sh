python ./printQuestions.py 10 | xargs -P 15 -I{} -n 1 bash -c 'python ./crawlQuestion.py {}'
