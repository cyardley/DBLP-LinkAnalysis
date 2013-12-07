import sqlite3
import cPickle
import re
import time
import cgi
import urllib
from util import sprint, sortReverse
from os import path
from flask import request

scriptpath = "{}/".format(path.dirname(path.realpath(__file__)))
searchurl = "http://dblp.isearch-it-solutions.net/dblp/Search.action?q="

def query(db, table, columns, pub, minref):
    sql = 'select ' + columns + ' from ' + table + ' where pub_venue=\'' + \
          pub + '\' and ref_num>=' + str(minref)
    db.execute(sql);
    r = db.fetchall();
    return r

def do_search(db, searchTerm, resultGoal, minRef, timeout):
    r = cPickle.load(open(scriptpath + 'top_pub', 'rb'))
    cache_num = cPickle.load(open(scriptpath + 'num_pubs', 'rb'))
    print cache_num
    results = []
    i = 0
    t = time.time()
    pubs = 0
    table_name = 'cache'
    for rank,pub in r:
        pubs += 1
        if pubs == int(cache_num):
            table_name = 'papers'
        qry = query(db, table_name, 'ref_num,title,authors,year,pub_venue,abstract', pub, minRef)
        sqry = sortReverse(qry) #sort by ref_num, descending
        for row in sqry:
            if not re.search(searchTerm, row[5])==None:
                results.append(row)
                i += 1
            if i>=int(resultGoal):
                return (pubs, results)
        print str(round((time.time() - t),2)) + ", " + str(timeout) 
        if  (time.time() - t) > float(timeout):
            return (pubs, results)
    return (pubs, results)

if __name__=='__main__':
    t = time.time()
    conn = sqlite3.connect(scriptpath + 'sql_db')
    db = conn.cursor();
    minRef = 1
    resultGoal = 100
    timeout = 20
    searchTerm = raw_input("Search: ")
    (pubs, results) = do_search(db, searchTerm, resultGoal, minRef, timeout)
    print "Results:"
    for row in results:
        print row[1]
        print "  referenced by " + str(row[0]) + " papers."
        print "  by: " + row[2]
        print "  " + row[4]  + " - " + row[3]
        print
    print str(len(results)) + " results from top " \
         + str(pubs) + " publications in top " \
         + str(round(time.time()-t, 2)) + " seconds." 
    db.close()
