from typing import Dict, Tuple, Sequence

from flask import Flask, jsonify, request, render_template, url_for, redirect, send_from_directory
import json 
import sqlite3
from random import shuffle
app = Flask(__name__)
import math

directory = 'data'
database_name = 'summaries_test.db'
db_path = '%s/%s'%(directory, database_name)
n_labels_per_doc = 6
n_docs = 5

@app.route('/')
def hello():
    return next()


@app.route("/download")
def download_file():
    return send_from_directory(
        directory, database_name, as_attachment=True
    )


def get_summary_article_for_uid(summary_uuid) -> Tuple[str]:
    # return (target, title, predicted) summary for this *prediction* uid.
    with sqlite3.connect(db_path) as con:
        article, summary = c.execute("""SELECT article, summary FROM generated_summaries where summary_uuid='{}';""".format(summary_uuid[0])).fetchone()
        return article, summary


@app.route('/annotate/<uid>')
def annotate(summary_uuid, con):
    # uid is a unique identifier for a *generated*
    # summary. 
    article, summary = get_summary_article_for_uid(uid)

#     # this is terrible but right now we collect 3 annotations per doc, so... yeah
#     print(get_n_labels(), uuids)
#     n_done = str(math.floor(int(get_n_labels()/(n_labels_per_doc * n_docs))))


#     label_uids, label_idx = get_label_ordered_uids(uuids, con)
#     label_idx = [label_uids.index(each) for each in uuids]
    
#     print(uuids, label_uids, sort_idx(label_idx, uuids))
    
#     labels = get_num_annotated(uuids, con)
    
#     print('RECORDED', labels)
    
    

    return render_template("all_done.html")

#     return render_template('annotate_factuality.html',
#                                         uuids=sort_idx(label_idx, uuids), 
#                                         review_title=review_title, 
#                                         reference=reference, 
#                                         predictions=sort_idx(label_idx, predictions), 
#                                         systems=sort_idx(label_idx, systems),
#                                         already_done=n_done)


def next():
    ''' pick a rando prediction in the system that hasn't been annotated, display it. '''
    with sqlite3.connect(db_path) as con:
        

        q_str = """SELECT uuid FROM generated_summaries WHERE NOT EXISTS (
                    SELECT * FROM label WHERE generated_summaries.summary_uuid = label.summary_uuid) 
                      ORDER BY uuid, RANDOM() LIMIT 1;""".format(6)


        next_uuid = con.execute(q_str).fetchone()

        if next_uuid is None:
            return render_template("all_done.html")

#         print(coch_id)
        summary_uuid = con.execute("""SELECT summary_uuid FROM generated_summaries where uuid='{}';""".format(next_uuid[0])).fetchone()
        print(summary_uuid)
        
    
        return annotate(summary_uuid, con)

