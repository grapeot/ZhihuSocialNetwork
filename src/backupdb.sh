\rm -rf /mnt/mongobackup
mongodump --out /mnt/mongobackup
cd ~/ZhihuSocialNetwork/dat
rm mongodb.zip
zip -r mongodb.zip /mnt/mongobackup
