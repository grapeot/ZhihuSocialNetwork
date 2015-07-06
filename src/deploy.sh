# general dependencies
# mongodb
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo apt-get install -y python-bs4 python-numpy python-scipy python-requests python-lxml python-cssselect python-pymongo speedometer

# mongodb c++ driver
sudo apt-get install -y -q libboost-all-dev scons
git clone https://github.com/mongodb/mongo-cxx-driver.git
cd mongo-cxx-driver
git checkout legacy
sudo scons --sharedclient -j4 --dbg=on --opt=on install
sudo cp -ar build/install/include/mongo /usr/include
sudo cp -ar build/install/lib/* /usr/lib/

# other python dependencies
sudo pip install jinja2

# install scikit-learn
sudo apt-get install -y build-essential python-dev python-setuptools python-numpy python-scipy python-matplotlib libatlas-dev libatlas3gf-base
sudo update-alternatives --set libblas.so.3 /usr/lib/atlas-base/atlas/libblas.so.3
sudo update-alternatives --set liblapack.so.3 /usr/lib/atlas-base/atlas/liblapack.so.3
sudo pip install jieba ipython
pip install --user --install-option="--prefix=" -U scikit-learn
