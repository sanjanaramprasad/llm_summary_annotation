import math 
import string 
import re

import json 

import pandas as pd 
import sqlite3

db_path = "../data/summaries_test.db"  

create_cmds = ['''CREATE TABLE generated_summaries (
    uuid INTEGER PRIMARY KEY AUTOINCREMENT, 
    summary_uuid TEXT NOT NULL ,
    summ_id TEXT NOT NULL, 
    system_id TEXT NOT NULL, 
    summary TEXT NOT NULL,
    article TEXT
);''',

'''CREATE TABLE label (
    uuid INTEGER PRIMARY KEY AUTOINCREMENT, 
    summary_uuid TEXT NOT NULL,
    label_type TEXT NOT NULL,
    score INTEGER NOT NULL
);''']


def connect_to_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    return conn, c 

def create_table(create_str):
    conn, c = connect_to_db()
    c.execute('''%s'''%(create_str))
    conn.commit()
    conn.close()


for create_str in create_cmds:
    create_table(create_str)