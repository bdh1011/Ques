# -*- coding: utf-8 -*-
from flask import render_template, flash, session, url_for, g, request, redirect
from app import db
from app import app
import os
import sys

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
def sign_up():
    email = request.args.get('email')
    password =  request.args.get('password')
    birthday =  request.args.get('birthday')
    gender =  request.args.get('gender')

    
    if email is None or password is None:
    	flash('폼을 채워주세요')
        return redirect(url_for('join'))
    if User.query.filter_by(email=email).first() is not None:
        flash('이미 존재하는 계정입니다')
        return redirect(url_for('join'))

    user = User(email=email, password=password, gender=gender, birthday=birthday )

    db.session.add(user)
    db.session.commit()
    g.user = user

    return redirect(url_for('home'))



@app.route('/')
def login():
	return render_template("login.html")

@app.route('/main')
def main():
	return render_template("main.html")

@app.route('/join',  methods=['GET'])
def join():
	return render_template("join.html")

@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/create')
def create():
	return render_template('create.html')