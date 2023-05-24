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
import flask_monitoringdashboard as dashboard

app = Flask(__name__)
dashboard.bind(app)
app.secret_key = 'your_secret_key_here'



directory = 'data'
database_name = 'summaries_news_sample_qual.db'
db_path = '%s/%s'%(directory, database_name)
n_labels_per_doc = 6
n_docs = 5


login_manager = LoginManager()
login_manager.init_app(app)




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
    "sanjana": User(1, "sanjana", "zR46"),
    "byron": User(2, "byron", "fJ89"),
    "kundan": User(3, "kundan", "8f*7"),
    
    }
    return users

@login_manager.user_loader
def load_user(username):
    return get_users().get(username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return show_annotator_list()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = load_user(username)
        
        if user is not None and user.check_password(password):
            login_user(user)
            return show_annotator_list()
        
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


def show_annotator_list():
    with sqlite3.connect(db_path) as con:
        username = current_user.username
        # print(con.execute("SELECT * FROM label").fetchall())
        q_str = f"""SELECT DISTINCT user_id from label"""


        user_ids = con.execute(q_str).fetchall()
        user_ids = [each[0] for each in user_ids]
        if not user_ids:
            return render_template("no_annotations.html")
        
        # print(summary_uuid[0])
        return render_template('annotator_list.html', annotators = user_ids)
    
def next(idx, user_annotations):
    user_annotation = user_annotations[idx]
    # print(user_annotations)
    user_id = user_annotation[0]
    summary_uuid = user_annotation[1]
    label_type = user_annotation[2]
    nonfactual_sentence = user_annotation[3]
    summary = user_annotation[4]
    article = user_annotation[5]
    nonfactual_sentence = nonfactual_sentence.split('<new_annotation>')
    nonfactual_sentence = [each for each in nonfactual_sentence if each.strip()]
    return render_template('display_annotation.html', user_annotations = user_annotations, idx = idx, user_id = user_id, summary_uuid = summary_uuid, \
                           label_type = label_type, nonfactual_sentence = nonfactual_sentence, summary=summary, article = article)
@login_required
@app.route('/show_annotations/<annotators>', methods = ['POST'])  
def show_annotations(annotators):
    annotators = eval(annotators)
    # print(annotators)
    user_id = None
    for annot in annotators:
        key_name = f'checked_{annot}'
        if key_name in request.form.keys():
            print(request.form[key_name])
            user_id = request.form[key_name]

    with sqlite3.connect(db_path) as con:
        
        # user_id = annot
        q_str = f"""SELECT user_id, summary_uuid, label_type, nonfactual_sentences, summary, article from label where user_id == '{user_id}'"""
        user_annotations = con.execute(q_str).fetchall()

        idx = 0
        return next(idx, user_annotations)

@login_required
@app.route('/next_annotation/<user_id>', methods = ['POST'])  
def next_annotations(user_id):
    button_val = str(request.form['button'])
    user_annotations = eval(request.form['user_annotations'])
    idx = int(request.form['idx'])
    print(idx, len(user_annotations))
    if button_val == 'next':
        idx +=1 
        if idx >= len(user_annotations):
            return render_template("no_annotations.html")
        
    elif button_val == 'back': 
        if idx ==0:
            idx = 0
        else:
            idx -= 1
    else:
        return show_annotator_list()
    
    return next(idx, user_annotations)
        
      

    return next(idx, user_annotations)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)