\rm -rf ~/instance/mongobackup
mongodump --out ~/instance/mongobackup
cd ../dat
rm mongodb.zip
zip -r mongodb.zip ~/instance/mongobackup
