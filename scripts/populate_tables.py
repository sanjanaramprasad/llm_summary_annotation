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





def add_data(filename, origin_type = 'xsum'):
    df = pd.read_csv(filename)
    conn, c = connect_to_db()
    for idx, row in df.iterrows():
        summ_uuid = row['id']
        
        article = row['doc']
        generic_summary = row['Generic_summary']
        faithful_summary = row['Faithful_summary']
        c.execute("""INSERT INTO generated_summaries (summary_uuid, summ_id, system_id, summary, article) VALUES (?, ?, ?, ?, ?)""",
                                                        (summ_uuid, 
                                                        f'{origin_type}_generic',
                                                        'gpt3.5_turbo',
                                                        generic_summary,
                                                        article))


        c.execute("""INSERT INTO generated_summaries (summary_uuid, summ_id, system_id, summary, article) VALUES (?, ?, ?, ?, ?)""",
                                                        (summ_uuid, 
                                                        f'{origin_type}_faithful',
                                                        'gpt3.5_turbo',
                                                        faithful_summary,
                                                        article))

    print('Added %d generated summaries'%(idx))
    conn.commit()
    conn.close()
add_data('/Users/sanjana/factual_annotation_llm_summaries/generated_summaries/xsum_summaries_gpt-3.5-turbo-0301.csv', origin_type = 'xsum')
add_data('/Users/sanjana/factual_annotation_llm_summaries/generated_summaries/cnndm_summaries_gpt-3.5-turbo-0301.csv', origin_type = 'cnndm')