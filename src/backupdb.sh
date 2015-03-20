mongodump --out ../dat/mongodb
cd ../dat
rm mongodb.zip
zip -r mongodb.zip mongodb
rm -rf mongodb
