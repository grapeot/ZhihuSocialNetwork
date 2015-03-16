# ZhihuSocialNetwork

A small project crawling data from [zhihu](http://zhihu.com/) and try to extract a social network from the users.

# Bootstrap

* `git clone`
* `deploy.sh` to install dependencies
* `python crawlTimeline.py <some user>` then `crawlQuestions.sh` to bootstrap
* Create indices for the mongodb collections
* Extend users by collecting authors of the answers, and repeat this process.
