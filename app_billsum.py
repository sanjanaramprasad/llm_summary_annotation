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




directory = '/home/ec2-user/human_annotations_factuality/billsum/qualifying'
database_name = 'billsum_summaries_sample.db'
db_path = '/%s/%s'%(directory, database_name)
db_engine = dbEngine=sqlalchemy.create_engine('sqlite:///' + db_path)

metadata = MetaData(bind=db_engine)
metadata.reflect()
print(metadata)
generated_summaries = metadata.tables['generated_summaries']
label = metadata.tables['label']
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
    "sanjana": User(1, "sanjana", "zR46"),
    "byron": User(2, "byron", "fJ89"),
    "kundan": User(3, "kundan", "8f*7"),
    "ngfgoa": User(4, "ann_ngfgoa", "ioosws"),
    "ztkkmy": User(5, "ann_ztkkmy", "fakxqd"),
    "ufanpu": User(6, "ann_ufanpu", "emetym"),
    "xgsueu": User(7, "ann_xgsueu", "kjmzwm"),
    "fpvldm": User(8, "ann_fpvldm", "eglqqo"),
    "vkzklp": User(9, "ann_vkzklp", "hwnzlo"),
    "yswdty": User(10, "ann_yswdty", "xlviuw"),
    "bcfrmq": User(11, "ann_bcfrmq", "nwddkd"),
    "pvjwev": User(12, "ann_pvjwev", "kklrre"),
    "npeznj": User(13, "ann_npeznj", "metkjq"),
    "wfydpj": User(14, "ann_wfydpj", "ricuyr"),
    "ttkoat": User(15, "ann_ttkoat", "ooyyzj"),
    "hjzzvu": User(16, "ann_hjzzvu", "hwinkr"),
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


def get_summary_article_for_uid(summary_uuid) -> Tuple[str]:
    # return (target, title, predicted) summary for this *prediction* uid.
    with dbEngine.connect() as con:
        # sql_query = text("""SELECT article, summary, summary_uuid, summ_id, system_id FROM generated_summaries where summary_uuid='{}';""".format(summary_uuid))
        stmt = select([generated_summaries.c.article, generated_summaries.c.summary, generated_summaries.c.summary_uuid, \
                      generated_summaries.c.summ_id, generated_summaries.c.system_id]).where(generated_summaries.c.summary_uuid == summary_uuid)
        
        article, summary, summ_uuid, summ_id, system_id = con.execute(stmt).fetchone()
    return article, summary, summ_uuid, summ_id, system_id

@login_required
@application.route('/annotate/<uid>')
def annotate(summary_uuid):
    # uid is a unique identifier for a *generated*
    # summary. 
    username = current_user.username
    article, summary, summ_uuid, summ_id, system_id= get_summary_article_for_uid(summary_uuid)
    summ_sents = list(nlp(summary).sents)

    return render_template("annotate.html", username = username, article= article, summary = summary, summ_sents = summ_sents,  summ_uuid = summ_uuid, summ_id = summ_id, system_id = system_id)

@login_required
def back(current_uuid):
        with dbEngine.connect() as con:
        
            username = current_user.username
            # sql_query = text(f"""SELECT summary_uuid FROM label WHERE label.user_id = '{username}' ORDER BY summary_uuid;""")
            stmt = select(label.c.summary_uuid).where(label.c.user_id == username).order_by(label.c.summary_uuid)
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
            return annotate(back_uuid)

@login_required
def next():
        username = current_user.username
        # print(con.execute("SELECT * FROM label").fetchall())
        
        # q_str = text(f"""SELECT summary_uuid FROM generated_summaries WHERE NOT EXISTS (
        #             SELECT * FROM label WHERE generated_summaries.summary_uuid = label.summary_uuid AND label.user_id = '{username}' ) 
        #               ORDER BY summary_uuid, RANDOM() LIMIT 1;""")
        subquery = select([label]).where(and_(generated_summaries.c.summary_uuid == label.c.summary_uuid, label.c.user_id == username))
        stmt = select(generated_summaries.c.summary_uuid).where(~exists(subquery)).order_by(generated_summaries.c.summary_uuid).limit(1)
        with dbEngine.connect() as con:
            #stmt = select(generated_summaries.c.summary_uuid).limit(1)
            summary_uuid = con.execute(stmt).fetchone()

        if summary_uuid is None:
            return render_template("all_done.html")
        
        print(summary_uuid[0])
        return annotate(summary_uuid[0])

@login_required
@application.route('/save_annotation', methods = ['POST'])
def save_annotation():
    # print('Annotated by ' , current_user.username)
    # relevancy_score  = int(request.form['likert_relevance'])
    num_sentences = int(request.form['submit_var'])
    uid = str(request.form['summ_uuid'])
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
        username = str(request.form['username'])
        summ_id = str(request.form['summ_id'])
        system_id = str(request.form['system_id'])
        # label_type = "binary"
        summary = str(request.form['summary'])
        article = str(request.form['article'])

        with dbEngine.connect() as con:
            
            q_str = """INSERT INTO label (user_id, summary_uuid, summ_id, system_id, label_type, summary, nonfactual_sentences, article) VALUES (:value1, :value2, :value3, :value4, :value5, :value6, :value7, :value8)"""
            values = {'value1': username, 
                          'value2': uid, 
                          'value3': summ_id, 
                          'value4': system_id, 
                          'value5': label_type, 
                          'value6': summary, 
                          'value7': '<new_annotation>'.join(checked_values), 
                          'value8': article}
            con.execute(q_str, **values)
        # con.commit()

        
        return next()
    elif button_val == 'clear':
        return annotate(uid)
    else:
        return back(uid)
    

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080)
