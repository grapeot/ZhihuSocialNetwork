# ZhihuSocialNetwork

A small project crawling data from [zhihu](http://zhihu.com/) and try to extract a social network from the users.

# Bootstrap

* `git clone`
* `deploy.sh` to install dependencies
* Begin from the [root topic](http://www.zhihu.com/topic/19776749). `src/crawlTopicTopQuestions.py 19776749`
* Extend the coverage by (can be repeated multiple times)
    src/crawlQuestions.sh
    src/extendAuthorsFromTopQuestions.sh
    src/crawlUsers.sh
    src/crawlQuestions.sh
* Create indices for the mongodb collections
