#!/usr/bin/python 
import sqlite3
import time
import cPickle
from util import *



#Create Table
def createTable(db, tableName):
    db.execute('CREATE TABLE if not exists ' + tableName + '(id integer, title text, authors text, \
                    year text, pub_venue text, ref_id text, ref_num integer, abstract text)')
    print str(tableName) + " created."

#cache
def cache(db, numPubs):
    r = cPickle.load(open('top_pub', 'rb'))
    i = 0
    sprint("Saving Cache:")
    for rank,pub in r:
        db.execute('insert into cache select * from papers where pub_venue=\'' + pub + '\'')
        i += 1
        sprint(".")
        if i>int(numPubs):
            cPickle.dump(numPubs, open('num_pubs', 'wb'))
            sprint("done. Remember to commit!\n")
            return;

#Drop Table
def dropTable(db, tableName):
    if raw_input("Really drop table? (y/n)")=='y':
        db.execute('drop table if exists ' + tableName)
        print "Table Dropped"
    else:
        print "Did not drop table"

#Populate Table
def populateTable(db, ):
    f = open('DBLPOnlyCitationOct19.txt')
    INDEX = "";
    TITLE = "";
    AUTHORS = "";
    YEAR = "";
    PUB_VENUE = "";
    REF_ID = "";
    REF_NUM = 0;
    ABSTRACT = "";
    i = 0;
    sprint("Adding papers:")
    for rline in f:
        line = rline.decode("utf-8").rstrip();
        if line.startswith('#index'):
            INDEX += line.lstrip('#index');
        if line.startswith('#*'):
            TITLE += line.lstrip('#*');
        if line.startswith('#@'):
            AUTHORS += line.lstrip('#@');
        if line.startswith('#t'):
            YEAR += line.lstrip('#t');
        if line.startswith('#c'):
            PUB_VENUE += line.lstrip('#c');
        if line.startswith('#%'):
            REF_ID += line.lstrip('#%') + ";";
            REF_NUM = REF_NUM+1;
        if line.startswith('#!'):
            ABSTRACT += line.lstrip('#!');
        if line=="":
            REF_ID = REF_ID[:-1] #remove trailing ;
            print INDEX + ", " + TITLE;
            db.execute('insert into papers values (?,?,?,?,?,?,?,?)' \
            , (INDEX, TITLE, AUTHORS, YEAR, PUB_VENUE, REF_ID, REF_NUM, ABSTRACT));
            INDEX = "";
            TITLE = "";
            AUTHORS = "";
            YEAR = "";
            PUB_VENUE = "";
            REF_ID = "";
            REF_NUM = 0;
            ABSTRACT = "";
        i += 1
        if i%1000==0:
            sprint(".")
    f.close()
    sprint("Done. Remember to commit!\n")

if __name__=='__main__':
    conn = sqlite3.connect('sql_db')
    db = conn.cursor();
    instr = "";
    print "Type 'help' for options.\n";
    while True:
        instr = raw_input("> ")
        if instr=="create":
            createTable(db, 'papers')
            createTable(db, 'cache')
        elif instr=="drop":
            name = raw_input("Table to drop: ")
            dropTable(db, name)
        elif instr=="cache":
            n = raw_input("Number of publishers to cache: ")
            cache(db, n)
        elif instr=="pop":
            populateTable(db)
        elif instr=="query":
            inc = raw_input("> ");
            inq = (inc,)
            t = time.time()
            db.execute(inc);
            r = db.fetchall();
            tn = str(round(time.time() - t, 2));
            print r;
            print "done in " + tn + " seconds.\n";
        elif instr=="commit":
            conn.commit();
            print "done.\n";
        elif instr=="help":
            print "'create' - creates new table";
            print "'drop' - drops the tabe";
            print "'pop' - populates table with data";
            print "'query x' - query index x";
            print "'commit' - commit to db";
            print "'exit' - exit program";
        elif instr=="exit":
            break;
        else:
            print "Invalid Command!\n";
    db.close()

