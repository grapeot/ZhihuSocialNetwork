#include <cstdlib>
#include <iostream>
#include <string>
#include <map>
#include <omp.h>
#include "mongo/client/dbclient.h" // for the driver

using namespace std;
using namespace mongo;

typedef int featureKeyType;

vector<pair<string, map<featureKeyType, float> > > getFeatures(DBClientConnection &c) {
    vector<pair<string, map<featureKeyType, float> > > result;
    int userCount = c.count("zhihu.users");
    result.reserve(userCount);
    auto_ptr<DBClientCursor> cursor = c.query("zhihu.users");
    int count = 0;
    while (cursor->more()) {
        BSONObj item = cursor->next();
        string name = item.getField("name").str();
        cout << count++ << '\t' << name << endl;
        BSONObj features = item.getField("topicFeature").Obj();
        set<string> fields;
        features.getFieldNames(fields);
        map<featureKeyType, float> featureMap;
        for (set<string>::const_iterator ci = fields.begin(); ci != fields.end(); ci++) {
            stringstream ss(*ci);
            int id = 0;
            ss >> id;
            featureMap[id] = features.getField(*ci).numberDouble();
        }
        result.push_back(make_pair(name, featureMap));
        //result[name] = featureMap;
    }
    return result;
}

// return the distance between two features
float Distance(const map<featureKeyType, float> &f1, const map<featureKeyType, float> &f2) {
    float dist = 0;
    // DEBUG
    //cerr << f1.size() << ", " << f2.size() << endl;
    map<featureKeyType, float>::const_iterator it1 = f1.begin(), it2 = f2.begin();
    while (it1 != f1.end() && it2 != f2.end()) {
        //cerr << it1->first << '\t' << it2->first << endl;
        if (it1->first == it2->first) {
            dist += min(it1->second, it2->second);
            it1++;
            it2++;
        }
        else if (it1->first > it2->first) {
            it2++;
        }
        else {
            it1++;
        }
    }
    return dist;
}

struct NameDist {
    string name;
    float dist;
    NameDist(string n, float d): name(n), dist(d) {}
    bool operator<(const NameDist &n) const { return this->dist > n.dist; }
};

void calculateInterestUsers(DBClientConnection &c, const vector<pair<string, map<featureKeyType, float> > > &features) {
    int featureCount = features.size();
    int count = 0;
    #pragma omp parallel for
    for (int i = 0; i < featureCount; i++) {
        vector<pair<string, map<featureKeyType, float> > >::const_iterator it = features.begin() + i;
        count++;
        string name = it->first;
        cout << count << ", " << name << endl;
        vector<NameDist> namedists;
        namedists.reserve(features.size());
        for (vector<pair<string, map<featureKeyType, float> > >::const_iterator it2 = features.begin();
            it2 != features.end(); it2++) {
            namedists.push_back(NameDist(it2->first, Distance(it->second, it2->second)));
        }
        sort(namedists.begin(), namedists.end());
        // DEBUG: print out the result
        //cerr << name << '\t';
        BSONArrayBuilder arr;
        for (int i = 1; i < 11; i++) {
            //cerr << namedists[i].name << '(' << namedists[i].dist <<  "), ";
            arr.append(namedists[i].name);
        }
        //cerr << endl;
        // update to the mongodb
        #pragma omp critical
        c.update("zhihu.users", BSON( "name" << name ), 
                BSON( "$set" << BSON( "interestedUsers" << arr.arr())));
    }
} 

int main() {
    cerr << client::initialize() << endl;
    DBClientConnection c;
    c.connect("localhost");
    vector<pair<string, map<featureKeyType, float> > > features = getFeatures(c);
    calculateInterestUsers(c, features);

    return EXIT_SUCCESS;
}
