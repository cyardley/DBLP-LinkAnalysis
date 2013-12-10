from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from search import *
from os import path
import time
import sqlite3
import cgi
import re

scriptpath = "{}/".format(path.dirname(path.realpath(__file__)))

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def index():
    with open("{}README".format(scriptpath)) as rf:
      readme = rf.readlines()
    return render_template("index.html", readme=readme)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return redirect('/')
    t = time.time()
    conn = sqlite3.connect(scriptpath + 'sql_db')
    db = conn.cursor();
    resultGoal = cgi.escape(request.form['goal'])
    timeout = cgi.escape(request.form['timeout'])
    minRef = cgi.escape(request.form['minref'])
    searchTerm = re.compile(r"(" + cgi.escape(request.form['search']) + ")", re.IGNORECASE)
    (pubs, results) = do_search(db, searchTerm, resultGoal, minRef, timeout)
    r_html = ""
    for row in results:
        r_html += "<h3>%s <a target=_blank href=%s>(search)</a></h3> \
                <table border=\"1\" width=\"100%%\"><tr><th width=20%%><small>Publisher</small></th> \
                <th width=10%%><small>Year</small></th><th width=50%%><small>Authors</small></th> \
                <th width=20%%><small>#Papers referenced by</small></th></tr> \
                <tr><td><small><center>%s</center></small></td><td><small><center>%s</center></td> \
                <td><small><center>%s</center></td><td><small><center>%s</center></td></tr></table> \
                <p><small>%s</small></p> \
                <br>" % (cgi.escape(row[1]), \
                           searchurl + "title:\""+urllib.quote(row[1]) + '\"+year:\"' + row[3] + "\"", \
                           cgi.escape(row[4]), cgi.escape(row[3]), cgi.escape(row[2].replace(',', ', ')), \
                           row[0], re.sub(searchTerm, r"<b>\1</b>", cgi.escape(row[5])))
    return render_template("search.html", result_html=r_html, search=searchTerm, results=results, pubs=pubs, time=str(round(time.time()-t, 2)))

if __name__ == '__main__':
    app.run()
    #app.run(debug=True)
#    app.run(port=5001, host='0.0.0.0')
