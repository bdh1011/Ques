# -*- coding: utf-8 -*-
from flask import render_template, flash, session, url_for, g, request, redirect
from app import db
from app import app
import hashlib
import os
import sys
import datetime
import random
import re
from functools import wraps
from flask.ext.login import login_user, logout_user, current_user, login_required
from models import User, Survey, Question
import decorator
# from forms import LoginForm

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'userid' in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/join', methods=['POST'])
def join():

    email = request.form['email']
    password =  request.form['password']

    year = request.form['year']
    month = request.form['month']
    day = request.form['day']
    birthday =  year + month + day
    gender =  request.form['gender']
    
    
    if email is None or password is None:
        return redirect(url_for('join'))

    if User.query.filter_by(email=email).first() is not None:
        return redirect(url_for('join'))

    print email, password, birthday, gender

    user = User(email=email, password=password, gender=gender, birthday=birthday )

    db.session.add(user)
    db.session.commit()
    session['userid'] = user.id

    # user_hash = hashlib.sha1(str(user.id)).hexdigest()
    # session['token'] = user_hash

    return redirect(url_for('main'))


@app.route('/join',  methods=['GET'])
def sign_up():
    return render_template("join.html")



@app.route('/join/email/<email>')
def check_duplicate_email(email):
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'exist':'true'})
    else:
        return jsonify({'exist':'false'})


@app.route('/logout')
@login_required
def logout():
    # remove the user from the session if it's there
    logout_user()
    session.pop('token', None)
    return redirect(url_for('login'))

@app.route('/create', methods=['GET','POST'])
@login_required
def create():
    if request.method=='GET':
        current_time = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
        print current_time
        print session['userid']
        hash = hashlib.md5(str(session['userid'])+current_time).hexdigest()
        return redirect('survey/'+hash+'/edit')
        
    else:
        survey_title = request.form['survey_title']
        survey_subtitle = request.form['survey_subtitle']
        question_type = request.form['question_type']
        isEssential = request.form['is_essential']
        userid = session['userid']
        survey = Survey(title=title, subtitle=subtitle, userID=userid)
        db.session.add(survey)
        db.session.commit()
        # question = Question(title=survey_title, subtitle=survey_subtitle, questionType=question_type, surveyID)
        return render_template("create.html")

@app.route('/survey/<survey_id>/edit', methods=['GET','POST'])
@login_required
def survey_edit(survey_id):
    return render_template("create.html")

@app.route('/survey/<survey_id>/tmpsave', methods=['POST'])
@login_required
def tmp_create(survey_id):
    question = request.get_json()
    question_index = question.keys()
    question = question[question_index]

    tmp_question = {}

    tmp_question['title'] = question['title']
    tmp_question['subtitle'] = question['subtitle']
    tmp_question['type'] = question['type']
    question_option = question['option']
    question_option_list = []
    for each_question_option in question_option:
        question_option_list.append(each_question_option)
        print each_question_option
    session[question_index].append(question)
    return jsonify('success')

@app.route('/')
@app.route('/login' , methods=['GET', 'POST'])
def login():
    if request.method=='GET':
        # if g.get('user', None) is not None:
        #     return redirect(url_for('main'))
    	return render_template("login.html")
    else:
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        try:
            if not user.verify_password(password):
				error_msg = "아이디와 비밀번호를 확인해주세요"
				flash(error_msg)
				return render_template("login.html", error_msg=error_msg)
        except:
			error_msg = "아이디와 비밀번호를 확인해주세요"
			flash(error_msg)
			return render_template("login.html", error_msg=error_msg)
        user_hash = hashlib.sha1(str(user.id)).hexdigest()
        session['userid'] = user.id
        # username = re.match('(.*)(@)',user.email).group(1)
        return redirect(url_for('main'))



@app.route('/fb_login' , methods=['POST'])
def fb_login():
    email = request.form['email']
    birthday = request.form['birthday']
    print email, birthday
    user = User.query.filter_by(email=email).first()
    try:
        if not user.verify_password(password):
			error_msg = "아이디와 비밀번호를 확인해주세요"
			flash(error_msg)
			return render_template("login.html", error_msg=error_msg)
    except:
		gender =  "male" #request.form['gender']
		password = birthday
		user = User(email=email, password=birthday, gender=gender, birthday=birthday )

		db.session.add(user)
		db.session.commit()

		# user_hash = hashlib.sha1(str(user.id)).hexdigest()
		session['userid'] = user.id
    return redirect(url_for('userid'))


@app.route('/main')
def main():
    if not 'userid' in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(id=session['userid']).first()
    username = re.match('(.*)(@)',user.email).group(1)

    session['tmp_question_dict'] = []
        
    return render_template("main.html", username=username)

@app.route('/home')
@login_required
def home():

	return render_template('home.html')
