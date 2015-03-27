python ./printQuestions.py 1 | xargs -P 10 -I{} -n 1 bash -c 'python ./crawlQuestion.py {}'
