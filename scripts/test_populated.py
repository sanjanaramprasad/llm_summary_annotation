import math 
import string 
import re

import json 

import pandas as pd 
import sqlite3

db_path = "../data/summaries_test.db"  



def connect_to_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    return conn, c 

exec_str = "SELECT * FROM label"
conn, c = connect_to_db()
response = c.execute('''%s'''%(exec_str)).fetchall()
print(response)