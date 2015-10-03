import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.login import LoginManager
from redis import Redis

redis = Redis()

app = Flask(__name__)
app.secret_key = 'ques'

db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/ques.db'

login_manager = LoginManager()
login_manager.init_app(app)

from app import views
db.create_all()
