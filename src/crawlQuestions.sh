python ./printQuestions.py 3 | xargs -P 10 -I{} -n 1 bash -c 'python ./crawlQuestion.py {}'
