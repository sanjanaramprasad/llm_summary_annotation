from typing import Dict, Tuple, Sequence

from flask import Flask, jsonify, request, render_template, url_for, redirect, send_from_directory
import json 

import sqlalchemy
from sqlalchemy import text, create_engine, Index, MetaData, Table, select, exists
from sqlalchemy.sql import and_

from random import shuffle
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import math
import spacy

nlp = spacy.load('en_core_web_sm')
# import flask_monitoringdashboard as dashboard

#app = Flask(__name__)
application = Flask(__name__)
# dashboard.bind(app)

application.secret_key = 'your_secret_key_here'




directory = '/Users/sanjana/human_annotations_factuality/billsum/set1_round2'
database_name = 'billsum_nonfactual_annotated_generated_summaries.db'
db_path = '/%s/%s'%(directory, database_name)
dbEngine=sqlalchemy.create_engine('sqlite:///' + db_path)

metadata = MetaData(bind=dbEngine)
metadata.reflect()
print(metadata)
nonfactual_annotated_generated_summaries = metadata.tables['nonfactual_annotated_generated_summaries']
error_label = metadata.tables['error_label']
# index1 = Index('idx_generated_summaries', generated_summaries.c.summary_uuid)
# index2 = Index('idx_label', label.c.summary_uuid)
# index3 = Index('idx_label', label.c.summary_uuid)
# index1.create(bind=db_engine)
# index2.create(bind=db_engine)

# con = db_engine.connect()

n_labels_per_doc = 6
n_docs = 5


login_manager = LoginManager()
login_manager.init_app(application)




# User class example
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password_hash = generate_password_hash(password)
        

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username


def get_users():
    users = {
    "ann_hguilf": User(4, "ann_hguilf", "sgnvru"),
    "ann_pvrkuy": User(5, "ann_pvrkuy", "rsjapi"),
    }
    return users

@login_manager.user_loader
def load_user(username):
    return get_users().get(username)


@application.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return next()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = load_user(username)
        
        if user is not None and user.check_password(password):
            login_user(user)
            return next()
        
        # flash('Invalid username or password')
    
    return render_template('login.html')

@login_required
@application.route('/')
def hello():
    return redirect(url_for('login'))





@application.route("/download")
def download_file():
    return send_from_directory(
        directory, database_name, as_attachment=True
    )


@application.route('/logout')
@login_required
def logout():
    login_link = url_for('login')
    print(login_link)
    logout_user()
    return render_template('logout.html', login_lin = login_link)


def get_summary_article_for_uid(summary_uuid, username) -> Tuple[str]:
    # return (target, title, predicted) summary for this *prediction* uid.
    # printsummary_uuid)
    with dbEngine.connect() as con:

        # sql_query = text("""SELECT article, summary, summary_uuid, summ_id, system_id FROM generated_summaries where summary_uuid='{}';""".format(summary_uuid))
        stmt = select([nonfactual_annotated_generated_summaries.c.article, nonfactual_annotated_generated_summaries.c.summary, nonfactual_annotated_generated_summaries.c.nonfactual_sentence, nonfactual_annotated_generated_summaries.c.summary_uuid, \
                      nonfactual_annotated_generated_summaries.c.summ_id, nonfactual_annotated_generated_summaries.c.system_id, ]).where(and_(nonfactual_annotated_generated_summaries.c.summary_uuid == summary_uuid, nonfactual_annotated_generated_summaries.c.user_id == username))
        
        article, summary, nonfactual_sentence, summ_uuid, summ_id, system_id = con.execute(stmt).fetchone()
    return article, summary, nonfactual_sentence, summ_uuid, summ_id, system_id

@login_required
@application.route('/annotate/<uid>')
def annotate(summary_uuid, username):
    # uid is a unique identifier for a *generated*
    # summary. 
    username = current_user.username
    article, summary, nonfactual_sentence, summ_uuid, summ_id, system_id = get_summary_article_for_uid(summary_uuid, username)
    summ_sents = list(nlp(summary).sents)

    return render_template("annotate_categories.html", username = username, article= article, summary = summary, nonfactual_sentence = nonfactual_sentence,  summ_uuid = summ_uuid, summ_id = summ_id, system_id = system_id)

@login_required
def back(current_uuid):
        with dbEngine.connect() as con:
        
            username = current_user.username
            # sql_query = text(f"""SELECT summary_uuid FROM label WHERE label.user_id = '{username}' ORDER BY summary_uuid;""")
            stmt = select(error_label.c.summary_uuid).where(error_label.c.user_id == username).order_by(error_label.c.summary_uuid)
            uuids = con.execute(stmt).fetchall()
            uuids = [each[0] for each in uuids]
            print('ALL LABELED', uuids)
            if current_uuid in uuids:
                current_uuid_idx = uuids.index(current_uuid)
                back_uuid = uuids[current_uuid_idx - 1]
            elif uuids:
                back_uuid =  uuids[-1]
            else:
                back_uuid = current_uuid
            # summary_uuid = con.execute("""SELECT summary_uuid FROM generated_summaries where uuid='{}';""".format(back_uuid)).fetchone()
            print(back_uuid)
            return annotate(back_uuid, username)

@login_required
def next():
        username = current_user.username
        # print(con.execute("SELECT * FROM label").fetchall())
        
        # q_str = text(f"""SELECT summary_uuid FROM generated_summaries WHERE NOT EXISTS (
        #             SELECT * FROM label WHERE generated_summaries.summary_uuid = label.summary_uuid AND label.user_id = '{username}' ) 
        #               ORDER BY summary_uuid, RANDOM() LIMIT 1;""")
        subquery = select([error_label]).where(and_(nonfactual_annotated_generated_summaries.c.summary_uuid == error_label.c.summary_uuid, error_label.c.user_id == username))
        stmt = select(nonfactual_annotated_generated_summaries.c.summary_uuid).where(and_(nonfactual_annotated_generated_summaries.c.user_id == username, ~exists(subquery))).order_by(nonfactual_annotated_generated_summaries.c.summary_uuid).limit(1)

        # subquery = select([label]).where(and_(generated_summaries.c.summary_uuid == label.c.summary_uuid, label.c.user_id == username))
        # stmt = select(generated_summaries.c.summary_uuid).where(~exists(subquery)).order_by(generated_summaries.c.summary_uuid).limit(1)
        with dbEngine.connect() as con:
            #stmt = select(generated_summaries.c.summary_uuid).limit(1)
            summary_uuid = con.execute(stmt).fetchone()

        if summary_uuid is None:
            return render_template("all_done.html")
        
        print(summary_uuid[0], username)
        return annotate(summary_uuid[0], username)

@login_required
@application.route('/save_annotation', methods = ['POST'])
def save_annotation():
    user_id = str(request.form['username'])
    summ_id = str(request.form['summ_id'])
    summary_uuid = str(request.form['summ_uuid'])
    system_id = str(request.form['system_id'])
    
    button_val = str(request.form['button'])
    
    if button_val == 'submit':
        inaccuracy_severity = str(request.form['severity'])
        error_type_category = str(request.form['error_type'])
        # print('NUM SENTENCES', num_sentences)

        error_type = error_type_category.split('_')[0].strip()
        error_factuality = '_'.join(error_type_category.split('_')[1:])
        comments = str(request.form["comments"])
        nonfactual_sentence = str(request.form['nonfactual_sentence'])
        summary = str(request.form['summary'])
        article = str(request.form['article'])

        with dbEngine.connect() as con:
           

            q_str = """INSERT INTO error_label (user_id, summary_uuid, summ_id, system_id, inaccuracy_severity, error_type, error_factuality, comments, nonfactual_sentence, summary, article) VALUES (:value1, :value2, :value3, :value4, :value5, :value6, :value7, :value8, :value9, :value10, :value11)"""
            values = {'value1': user_id, 
                          'value2': summary_uuid, 
                          'value3': summ_id, 
                          'value4': system_id, 
                          'value5': inaccuracy_severity, 
                          'value6': error_type, 
                          'value7': error_factuality, 
                          'value8': comments,
                          'value9': nonfactual_sentence,
                          'value10': summary,
                          'value11': article}
            con.execute(q_str, **values)
        # con.commit()

        
        return next()
    elif button_val == 'clear':
        return annotate(summary_uuid)
    else:
        return back(summary_uuid)
    

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080)
