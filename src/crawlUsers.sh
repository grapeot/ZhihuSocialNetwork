python ./printNames.py 3 > usernames.txt
cat usernames.txt | xargs -P 10 -I{} -n 1 bash -c 'python ./crawlTimeline.py "{}"'
