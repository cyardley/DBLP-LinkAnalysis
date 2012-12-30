import sqlite3
from manage_db import *
from web import *
from PageRank import *

conn = sqlite3.connect('sql_db')
db = conn.cursor();

#database
dropTable(db, 'papers')
dropTable(db, 'cache')
createTable(db, 'papers')
createTable(db, 'cache')
populateTable(db)
conn.commit()

#web
saveTables(5, 5, True)
makeMatrix()

#PageRank
doRank()

#cache
cache(db, 5)
conn.commit()
db.close()

print "Done. Run search."

