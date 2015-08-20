import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth


app = Flask(__name__)
app.secret_key = 'ques'

db = SQLAlchemy(app)


from app import views
db.create_all()
