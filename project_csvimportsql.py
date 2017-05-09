# -*- coding: utf-8 -*-
"""
Created on Mon May 08 13:32:47 2017

@author: Tong LI
"""

import csv, sqlite3

con=sqlite3.connect(r"Hartford.db")
con.text_factory = str

cur=con.cursor()

cur.execute("DROP TABLE NODES")
cur.execute("DROP TABLE NODES_TAGS")
cur.execute("DROP TABLE WAYS")
cur.execute("DROP TABLE WAYS_TAGS")
cur.execute("DROP TABLE WAYS_NODES")


cur.executescript('''CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT
);

CREATE TABLE nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
);

CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT
);

CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
);

CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);''')

with open('nodes.csv', 'rb') as nd:
    ndf=csv.DictReader(nd)
    to_db1=[(i['id'], i['lat'], i['lon'], i['user'], i['uid'], i['version'], i['changeset'], i['timestamp']) for i in ndf]

cur.executemany('INSERT INTO nodes (id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?,?,?,?,?,?,?,?);', to_db1)


con.commit()


with open('nodes_tags.csv', 'rb') as ndt:
    ndtf=csv.DictReader(ndt)
    to_db2=[(i['id'], i['key'], i['value'], i['type']) for i in ndtf]

cur.executemany('INSERT INTO nodes_tags (id, key, value, type) VALUES (?,?,?,?);', to_db2)

con.commit()


with open('ways.csv', 'rb') as wy:
    wyf=csv.DictReader(wy)
    to_db3=[(i['id'], i['user'], i['uid'], i['version'], i['changeset'], i['timestamp']) for i in wyf]

cur.executemany('INSERT INTO ways (id, user, uid, version, changeset, timestamp) VALUES (?,?,?,?,?,?);', to_db3)

con.commit()


with open('ways_tags.csv', 'rb') as wyt:
    wytf=csv.DictReader(wyt)
    to_db4=[(i['id'], i['key'], i['value'], i['type']) for i in wytf]

cur.executemany('INSERT INTO ways_tags (id, key, value, type) VALUES (?,?,?,?);', to_db4)

con.commit()


with open('ways_nodes.csv', 'rb') as wyn:
    wynf=csv.DictReader(wyn)
    to_db5=[(i['id'], i['node_id'], i['position']) for i in wynf]

cur.executemany('INSERT INTO ways_nodes (id, node_id, position) VALUES (?,?,?);', to_db5)

con.commit()
con.close()

#=======================================================================================
con=sqlite3.connect(r"Hartford.db")

cur=con.cursor()

cur.execute("SELECT * FROM nodes;")
rows=cur.fetchall()
print rows