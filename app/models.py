# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context


import json, os, uuid
from app import db
from app import app

class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Interger, primary_key=True, autoincrement=True, nullable=False)
	password_hash = db.Column(db.String(256), nullable=False)
	email = db.Column(db.String(64), nullable=False)
	gender = db.Column(db.Interger, nullable=False)
	birthday = db.Column(db.String(64), nullable=False)
	q_point = db.Column(db.Interger)
	profile_picture_filename = db.Column(db.String(64))

	register_timestamp = db.Column(db.DateTime, default=db.func.now())
	recent_login_timestamp = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
	survey = db.relationship('Survey', backref='user', lazy='dynamic')
	like = db.relationship('Like', backref='user', lazy='dynamic')
	answer = db.relationship('Answer', backref='user', lazy='dynamic')
	
	def __init__(self, email, password, gender, birthday):
		self.email = email
		hash_password(password)
		self.gender = gender
		self.birthday = birthday

	def hash_password(self, password):
		self.password_hash = pwd_context.encrypt(password)

	def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

	def generate_auth_token(self, expiration=360000):
		s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
		return s.dumps({'username': self.username})

	@staticmethod
	def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


class Survey(db.Model):
	__tablename__ = 'survey'
	id = db.Column(db.Interger, primary_key=True, autoincrement=True, nullable=False)
	title = db.Column(db.String(64), nullable=False)
	register_timestamp = db.Column(db.DateTime, default=db.func.now())
	userID = db.Column(db.String(64), db.ForeignKey('user.id'))

	like = db.relationship('Like', backref='survey',lazy='dynamic')
	question = db.relationship('Question', backref='survey',lazy='dynamic')

class Like(db.Model):
	__tablename__ 'like'
	id = db.Column(db.Interger, primary_key=True, autoincrement=True, nullable=False)
	timestamp = db.Column(db.DateTime, default=db.func.now())
	userID = db.Column(db.String(64), db.ForeignKey('user.id'))
	surveyID = db.Column(db.String(64), db.ForeignKey('survey.id'))
	


class Question(db.Model):
	__tablename__ = 'question'
	id = db.Column(db.Interger, primary_key=True, autoincrement=True, nullable=False)
	title = db.Column(db.String(64), nullalbe=False)
	subtitle = db.Column(db.Text, nullalbe=False)
	questionType = db.Column(db.Integer, nullable=False)
	isEssential = db.Column(db.Boolean, nullable=False)
	surveyID = db.Column(db.String(64), db.ForeignKey('survey.id'))
	option = db.relationship('Option', backref='question', lazy = 'dynamic')

class Option(db.Model):
	__tablename__ = 'option'
	id = db.Column(db.Interger, primary_key=True, autoincrement=True, nullable=False)
	optionType = db.Column(db.Interger)
	content = db.Column(db.Text)
	questionID = db.Column(db.String(64), db.ForeignKey('question.id'))

	answer = db.relationship('Answer', backref='option', lazy = 'dynamic')


class Answer(db.Model):
	__tablename__ = 'answer'
	id = db.Column(db.Interger, primary_key=True, autoincrement=True, nullable=False)
	userID = db.Column(db.String(64), db.ForeignKey('user.id'))

	content = db.Column(db.Text)
	optionID = db.Column(db.String(64), db.ForeignKey('option.id'))

	timestamp = db.Column(db.DateTime, default=db.func.now())



