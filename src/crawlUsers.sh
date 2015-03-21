python ./printNames.py 3 > ../dat/usernames.txt
cat ../dat/usernames.txt | xargs -P 10 -I{} -n 1 bash -c 'python ./crawlTimeline.py "{}"'
