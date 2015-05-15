python ./printNames.py 3 | grep -v '`' > ../dat/usernames.txt
cat ../dat/usernames.txt | xargs -P 20 -I{} -n 1 bash -c 'python ./crawlTimeline.py "{}"'
