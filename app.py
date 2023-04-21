from typing import Dict, Tuple, Sequence

from flask import Flask, jsonify, request, render_template, url_for, redirect, send_from_directory
import json 
import sqlite3
from random import shuffle
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import math
import spacy
nlp = spacy.load('en_core_web_sm')

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'



directory = 'data'
database_name = 'summaries_test.db'
db_path = '%s/%s'%(directory, database_name)
n_labels_per_doc = 6
n_docs = 5


login_manager = LoginManager()
login_manager.init_app(app)




# User class example
class User:
    def __init__(self, username, password):
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
    "sanjana": User("sanjana", "zR46"),
    "byron": User("byron", "fJ89"),
    "kundan": User("kundan", "8f*7")
    }
    return users

@login_manager.user_loader
def load_user(username):
    return get_users().get(username)


@app.route('/login', methods=['GET', 'POST'])
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
@app.route('/')
def hello():
    return redirect(url_for('login'))





@app.route("/download")
def download_file():
    return send_from_directory(
        directory, database_name, as_attachment=True
    )


@app.route('/logout')
@login_required
def logout():
    login_link = url_for('login')
    print(login_link)
    logout_user()
    return render_template('logout.html', login_lin = login_link)


def get_summary_article_for_uid(summary_uuid) -> Tuple[str]:
    # return (target, title, predicted) summary for this *prediction* uid.
    with sqlite3.connect(db_path) as con:
        article, summary, summ_uuid, summ_id, system_id = con.execute("""SELECT article, summary, summary_uuid, summ_id, system_id FROM generated_summaries where summary_uuid='{}';""".format(summary_uuid)).fetchone()
        return article, summary, summ_uuid, summ_id, system_id

@login_required
@app.route('/annotate/<uid>')
def annotate(summary_uuid):
    # uid is a unique identifier for a *generated*
    # summary. 
    article, summary, summ_uuid, summ_id, system_id= get_summary_article_for_uid(summary_uuid)
    summ_sents = list(nlp(summary).sents)

    
    

    return render_template("annotate.html", article= article, summary = summary, summ_sents = summ_sents,  summ_uuid = summ_uuid, summ_id = summ_id, system_id = system_id)

@login_required
def back(current_uuid):
    with sqlite3.connect(db_path) as con:
        
        # print(con.execute("SELECT * FROM label").fetchall())

        q_str = """SELECT summary_uuid FROM label ORDER BY summary_uuid;"""
        uuids = con.execute(q_str).fetchall()
        uuids = [each[0] for each in uuids]
        print('ALL LABELED', uuids)
        if current_uuid in uuids:
            current_uuid_idx = uuids.index(current_uuid)
            back_uuid = uuids[current_uuid_idx - 1]
        else:
            back_uuid =  uuids[-1]
        # summary_uuid = con.execute("""SELECT summary_uuid FROM generated_summaries where uuid='{}';""".format(back_uuid)).fetchone()
        print(back_uuid)
        return annotate(back_uuid)

@login_required
def next():
    ''' pick a rando prediction in the system that hasn't been annotated, display it. '''
    with sqlite3.connect(db_path) as con:
        
        # print(con.execute("SELECT * FROM label").fetchall())
        q_str = """SELECT summary_uuid FROM generated_summaries WHERE NOT EXISTS (
                    SELECT * FROM label WHERE generated_summaries.summary_uuid = label.summary_uuid) 
                      ORDER BY summary_uuid, RANDOM() LIMIT 1;"""


        summary_uuid = con.execute(q_str).fetchone()

        if summary_uuid is None:
            return render_template("all_done.html")
        
        print(summary_uuid[0])
        return annotate(summary_uuid[0])

@login_required
@app.route('/save_annotation/<uid>', methods = ['POST'])
def save_annotation(uid):
    # print('Annotated by ' , current_user.username)
    # relevancy_score  = int(request.form['likert_relevance'])
    num_sentences = int(request.form['submit_var'])
    # print('NUM SENTENCES', num_sentences)

    checked_values = []
    for i in range(1, num_sentences + 1):
        key_name = f'checkbox_{i}'
        if key_name in request.form.keys():
            checked_values.append(request.form[key_name])
    
    if not checked_values:
        label_type = 'factual'
    else:
        label_type = 'non_factual'

    button_val = str(request.form['button'])
    
    if button_val == 'submit':
        user_id = current_user.username
        summ_id = str(request.form['summ_id'])
        system_id = str(request.form['system_id'])
        label_type = "binary"
        summary = str(request.form['summary'])
        article = str(request.form['article'])

        with sqlite3.connect(db_path) as con:
            con.execute("""INSERT INTO label (user_id, summary_uuid, summ_id, system_id, label_type, summary, nonfactual_sentences, article) VALUES (?, ?, ?, ?, ?, ? ,?, ?);""",
                                                            (user_id, uid, summ_id, system_id, label_type, summary, ','.join(checked_values), article))

        
        return next()
    elif button_val == 'clear':
        return annotate(uid)
    else:
        return back(uid)