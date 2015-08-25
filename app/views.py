# -*- coding: utf-8 -*-
from flask import render_template, flash, session, url_for, g, request, redirect
from app import db
from app import app
import hashlib
import os
import sys
from models import User

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


#temp decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print request.headers
        session_token = session.get('token')
        if session_token is None:
            return jsonify({ 'message': u'로그인해주세요.' }), 401

        session_token = escape(session_token)
        if redis_connections.get(session_token) is None:
            return jsonify({ 'message': u'로그인해주세요.' }), 401

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
    	flash('폼을 채워주세요')
        return redirect(url_for('join'))
    # if User.query.filter_by(email=email).first() is not None:
    #     flash('이미 존재하는 계정입니다')
    #     return redirect(url_for('join'))
    print email, password, birthday, gender

    user = User(email=email, password=password, gender=gender, birthday=birthday )

    db.session.add(user)
    db.session.commit()
    g.user = user

    user_hash = hashlib.sha1(str(user.id)).hexdigest()
    session['token'] = user_hash

    return render_template("main.html")


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
def logout():
    # remove the user from the session if it's there
    session.pop('token', None)
    return redirect(url_for('login'))



@app.route('/')
@app.route('/login' , methods=['GET', 'POST'])
def login():
    if request.method=='GET':
        if 'token' in session:
            return redirect(url_for('main'))
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
        session['token'] = user_hash
        g.user = user
        return render_template("main.html")



@app.route('/fb_login' , methods=['POST'])
def fb_login():
    email = request.form['email']
    birthday = request.form['birthday']
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

    user_hash = hashlib.sha1(str(user.id)).hexdigest()
    session['token'] = user_hash
    g.user = user
    return render_template("main.html")



@app.route('/main')
def main():
	if not 'token' in session:
		return redirect(url_for('login'))
	return render_template("main.html")

@app.route('/home')
def home():

	return render_template('home.html')

@app.route('/create')
def create():
	return render_template('create.html')