# -*- coding: utf-8 -*-
from flask import render_template, flash, session, url_for
from app import app
import os
import sys

@app.route('/')
def main():
	return render_template("main.html")

@app.route('/join')
def join():
	return render_template("join.html")

@app.route('/home')
def home():
	return render_template('home.html')