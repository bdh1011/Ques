# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context


import json, os, uuid
from app import db
from app import app

class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
	password_hash = db.Column(db.String(256), nullable=False)
	email = db.Column(db.String(64), nullable=False)
	gender = db.Column(db.String(64), nullable=False)
	birthday = db.Column(db.String(64), nullable=False)
	q_point = db.Column(db.Integer)
	profile_picture = db.Column(db.String(64))

	register_timestamp = db.Column(db.DateTime, default=db.func.now())
	recent_login_timestamp = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
	survey = db.relationship('Survey', backref='user', lazy='dynamic')
	like = db.relationship('Like', backref='user', lazy='dynamic')
	answer = db.relationship('Answer', backref='user', lazy='dynamic')
	
	def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.hash_password(password)

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
	id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	title = db.Column(db.String(64), nullable=False)
	link = db.Column(db.String(64), nullable=False)
	subtitle = db.Column(db.String(256), nullable=True)
	register_timestamp = db.Column(db.DateTime, default=db.func.now())
	userID = db.Column(db.String(64), db.ForeignKey('user.id'))

	def __init__(self, link, title, subtitle, userID):
		self.link = link
		self.title = title
		self.subtitle = subtitle
		self.userID = userID

	like = db.relationship('Like', backref='survey',lazy='dynamic')
	question = db.relationship('Question', backref='survey',lazy='dynamic')

class Like(db.Model):
	__tablename__ = 'like'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
	timestamp = db.Column(db.DateTime, default=db.func.now())
	userID = db.Column(db.String(64), db.ForeignKey('user.id'))
	surveyID = db.Column(db.String(64), db.ForeignKey('survey.id'))
	


class Question(db.Model):
	__tablename__ = 'question'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
	title = db.Column(db.String(64), nullable=False)
	subtitle = db.Column(db.Text, nullable=False)
	questionType = db.Column(db.Integer, nullable=False)
	surveyID = db.Column(db.String(64), db.ForeignKey('survey.id'))
	def __init__(self, title, subtitle, questionType, isEssential, surveyID):
		self.title = title
		self.subtitle = subtitle
		self.questionType = questionType
		self.isEssential = isEssential
		self.surveyID = surveyID


	option = db.relationship('Option', backref='question', lazy = 'dynamic')


class Option(db.Model):
	__tablename__ = 'option'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
	content = db.Column(db.Text)
	questionID = db.Column(db.String(64), db.ForeignKey('question.id'))
	def __init__(self, content, questionID):
		self.content = content
		self.questionID = questionID

	


class Answer(db.Model):
	__tablename__ = 'answer'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
	userID = db.Column(db.String(64), db.ForeignKey('user.id'))

	content = db.Column(db.Text)
	questionID = db.Column(db.String(64), db.ForeignKey('question.id'))
	def __init__(self, userID, content, questionID):
		self.userID = userID
		self.content = content
		self.questionID = questionID

	timestamp = db.Column(db.DateTime, default=db.func.now())



