#!/usr/bin/python
import cPickle #faster than pickle
import sqlite3
import time
import sys
from numpy import *
from util import *
from copy import deepcopy
from collections import defaultdict

conn = sqlite3.connect('sql_db')
db = conn.cursor();

def query(sql, printtime):
    if printtime:
        t = time.time()
    db.execute(sql);
    r = db.fetchall();
    if printtime:
        tn = str(round(time.time() - t, 2));
        print "Query done in " + tn + " seconds:";
    return r

#top publishers based on how many others they reference
# and by how often they are referenced by others
def topPubs(x):
    hub_dict = cPickle.load(open('hub_dict', 'rb'))
    auth_dict = cPickle.load(open('auth_dict', 'rb'))
    pub_dict = cPickle.load(open('pub_dict', 'rb'))
    ipub_dict = cPickle.load(open('ipub_dict', 'rb'))
    
    hubpub = defaultdict(int)
    authpub = defaultdict(int)
    for p,rl in hub_dict.iteritems():
        pub = pub_dict[p]
        if not pub=='': hubpub[pub] += 1
    shub = sorted([(value,key) for (key,value) in hubpub.items()])
    rhub = shub[: :-1]

    print "Top Hubs:"
    for i in range(0, x):
       print rhub[i][1]

    for p,rl in auth_dict.iteritems():
        pub = pub_dict[p]
        if not pub=='': authpub[pub] += 1
    sauth = sorted([(value,key) for (key,value) in authpub.items()])
    rauth = sauth[: :-1]

    print
    print "Top Authorities:"
    for i in range(0,x):
        print rauth[i][1]
    print

def saveTables(hubmin, authmin, trim):
    sprint("Executing SQL query:")
    sql = 'select id,ref_id,pub_venue from papers';
    qry = query(sql, False);
    sprint("...done.\n")
    pub_dict = {}
    ref_dict = {}
    hub_dict = defaultdict(int) #maps papers to the number of papers that it references
    auth_dict = defaultdict(int) #maps papers to the number of papers that reference it.
    k = 0;
    sprint("Creating Tables:")
    for row in qry:
        if(k%100000==0):
            sprint(".")
        k += 1
        ref_dict[row[0]] = row[1] #references{id:ref_id}
        pub_dict[row[0]] = row[2] #pub_venue{id:pub_venue}
        auth_dict[row[0]] = len(row[1].split(";"))
        for rx in row[1].split(";"):
            if not rx=='': hub_dict[int(rx)] += 1;
    ipub_dict = dictinvert(pub_dict)
    sprint("done.\n")
    sprint("Saving tables:")
    cPickle.dump(ref_dict, open('ref_dict', 'wb'))
    sprint(".")
    cPickle.dump(pub_dict, open('pub_dict', 'wb'))
    sprint(".")
    cPickle.dump(ipub_dict, open('ipub_dict', 'wb'))
    sprint(".")
    cPickle.dump(hub_dict, open('hub_dict', 'wb'))
    sprint(".")
    cPickle.dump(auth_dict, open('auth_dict', 'wb'))
    sprint("done.\n")
    #web table
    sprint("Create web table: ")
    k=0
    web_dict = defaultdict(set)
    for row in qry:
        if(k%100000==0):
            sprint(".")
        k += 1
        if len(row[1])>0:
            for r in row[1].split(";"):
                if hub_dict[int(r)]>=hubmin and auth_dict[int(r)]>=authmin:
		    #since it is a set, it will not add duplicates
                    web_dict[row[2]].add(pub_dict[int(r)])
    sprint("done\n")
    if trim:
        #Reduce web table
        k = 0
        sprint("Trimming web table:\n")
        tmp_dict = deepcopy(web_dict)
        for key,rset in tmp_dict.iteritems():
            if not refInDict(rset, web_dict, pub_dict, ipub_dict):
                web_dict.pop(key)
        sprint("done.\n")
    sprint("Saving Web Dict, size: " + str(len(web_dict)))
    cPickle.dump(web_dict, open('web_dict', 'wb'))
    sprint("...done.\n")

#returns true if one of the papers in rset is published
# by one of the publishers in web_dict
def refInDict(rset, web_dict, pub_dict, ipub_dict):
    for rx in rset:
        if pub_dict[ipub_dict[rx][0]] in web_dict:
            return True
    return False
        

def makeMatrix():
    print "Loading.."
    re = cPickle.load(open('web_dict', 'rb'))
    order = []
    for k,v in re.iteritems():
        order.append(k) #re[order[i]]
    size = len(re)
    sprint("Creating zeros matrix size " + str(size) + ":")
    web = []
    for i in range(0, size):
        if(i%100==0):
            sprint(".")
        web.append([0]*size)
    sprint("...done\n")
    sprint("Adding values:")
    for i in range(0, size):
        rset = re[order[i]]
        if i%100==0:
            sprint(".")
        for p in rset:
            if not p=='':
                if p in order:
                    web[i][order.index(p)] = 1
    sprint("done.\nSaving web:");
    cPickle.dump(web, open('web_matrix', 'wb'))
    sprint("..")
    cPickle.dump(order, open('web_order', 'wb'))
    sprint(".done\n");

if __name__=='__main__':
    saveTables(5, 5, True)
    makeMatrix()
    #topPubs(10)
