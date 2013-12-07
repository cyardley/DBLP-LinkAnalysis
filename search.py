import sqlite3
import cPickle
import re
import time
import cgi
import urllib
from util import sprint, sortReverse
from os import path

scriptpath = "{}/".format(path.dirname(path.realpath(__file__)))
searchurl = "http://dblp.isearch-it-solutions.net/dblp/Search.action?q="

def query(db, table, columns, pub, minref):
    sql = 'select ' + columns + ' from ' + table + ' where pub_venue=\'' + \
          pub + '\' and ref_num>=' + str(minref)
    db.execute(sql);
    r = db.fetchall();
    return r

def search(db, searchTerm, resultGoal, minRef, timeout):
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
    (pubs, results) = search(db, searchTerm, resultGoal, minRef, timeout)
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

def index(req):
    t = time.time()
    conn = sqlite3.connect(scriptpath + 'sql_db')
    db = conn.cursor();
    resultGoal = cgi.escape(req.form.getfirst('goal', ''))
    timeout = cgi.escape(req.form.getfirst('timeout', ''))
    minRef = cgi.escape(req.form.getfirst('minref', ''))
    searchTerm = re.compile(r"(" + cgi.escape(req.form.getfirst('search', '')) + ")", re.IGNORECASE)
    (pubs, results) = search(db, searchTerm, resultGoal, minRef, timeout)
    s = '''<html><head><title>Search Results: %s</title><body>
           <h2>Results for: %s</h2>''' % (searchTerm.pattern, searchTerm.pattern)
    s += "<p><a href=index.html>Search Again</a></p>"
    s += "<p><b>" + str(len(results)) + "</b> results in <b>" \
         + str(round(time.time()-t, 2)) + "</b> seconds,<b>" \
         + "</b> from <b>" + str(pubs) + "</b> publications.</p> <hr>"
    for row in results:
        s += '''<h3>%s <a target=_blank href=%s>(search)</a></h3>
                <table border="1" width="100%%"><tr><th width=20%%><small>Publisher</small></th>
                <th width=10%%><small>Year</small></th><th width=50%%><small>Authors</small></th>
                <th width=20%%><small>#Papers referenced by</small></th></tr>
                <tr><td><small><center>%s</center></small></td><td><small><center>%s</center></td>
                <td><small><center>%s</center></td><td><small><center>%s</center></td></tr></table>
                <p><small>%s</small></p>
                <br>''' % (cgi.escape(row[1]), \
                           searchurl + "title:\""+urllib.quote(row[1]) + '\"+year:\"' + row[3] + "\"", \
                           cgi.escape(row[4]), cgi.escape(row[3]), cgi.escape(row[2].replace(',', ', ')), \
                           row[0], re.sub(searchTerm, r"<b>\1</b>", cgi.escape(row[5])))
    s += "<hr><p><a href=index.html>Search Again</a></p>"
    s += '''</body></html>'''
    db.close()
    return s
