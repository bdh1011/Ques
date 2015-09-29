# -*- coding: utf-8 -*-
from flask import render_template, flash,jsonify, session, url_for, g, request, redirect, make_response
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
from sqlalchemy import or_, and_
from models import User, Survey, Question, Option, Answer, Like
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
        print session['userid']
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
    q_point = 1000
    
    if email is None or password is None:
        return redirect(url_for('join'))

    if User.query.filter_by(email=email).first() is not None:
        return redirect(url_for('join'))

    print email, password, birthday, gender
    user = User(email=email, password=password, gender=gender, birthday=birthday,q_point=q_point )
    db.session.add(user)
    db.session.commit()
    session['userid'] = user.id
    # user_hash = hashlib.sha1(str(user.id)).hexdigest()
    # session['token'] = user_hash
    return redirect(url_for('main'))


@app.route('/join',  methods=['GET'])
def sign_up():
    if 'userid' in session:
        return redirect(url_for('main'))
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
    session.pop('userid', None)
    return redirect(url_for('login'))

@app.route('/create', methods=['GET','POST'])
@login_required
def create():
    session['tmp_question_dict'] = {}
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

@app.route('/result')
@login_required
def result():
    return render_template('result.html')

@app.route('/archive')
@login_required
def archive():
    created_survey_list = Survey.query.filter_by(userID=session['userid']).all()
    answer_list = Answer.query.filter_by(userID=session['userid']).all()
    joined_survey_list = []
    for each_answer in answer_list:
        joined_question = Question.query.filter_by(id=each_answer.questionID).first()
        joined_survey_list.append(Survey.query.filter_by(id=joined_question.surveyID).first())
    user = User.query.filter_by(id=session['userid']).first()
    username = re.match('(.*)(@)',user.email).group(1)
    for i in range(len(created_survey_list)):
        created_survey_list[i].like_len = len(Like.query.filter_by(surveyID=created_survey_list[i].id).all())
        created_survey_question = Question.query.filter_by(surveyID=created_survey_list[i].id).first()
        created_survey_list[i].joined_len = len(Answer.query.filter_by(questionID=created_survey_question.id).all())

    for i in range(len(joined_survey_list)):
        joined_survey_list[i].like_len = len(Like.query.filter_by(surveyID=joined_survey_list[i].id).all())
        joined_survey_question = Question.query.filter_by(surveyID=joined_survey_list[i].id).first()
        joined_survey_list[i].joined_len = len(Answer.query.filter_by(questionID=joined_survey_question.id).all())


    return render_template('archive.html', created_survey_list=created_survey_list, joined_survey_list=joined_survey_list, joined_survey_count=len(joined_survey_list),username=username, profile_picture=user.profile_picture, q_point=user.q_point)

@app.route('/survey')
@login_required
def survey():
    return render_template('survey.html')


@app.route('/survey/<survey_id>/edit', methods=['GET','POST'])
@login_required
def survey_edit(survey_id):
    return render_template("create.html")

@app.route('/survey/<survey_id>/tmpsave', methods=['POST','GET'])
@login_required
def tmp_create(survey_id):
    if request.method=='GET':
        return jsonify(request.get_json())
    question = request.get_json()['question']
    print question
    if session['tmp_question_dict'].has_key(survey_id):
        session['tmp_question_dict'][survey_id].append(question)
    else:
        session['tmp_question_dict'][survey_id] = []
        session['tmp_question_dict'][survey_id].append(question)
    print session
    return jsonify({'success': session['tmp_question_dict']})


@app.route('/survey/<survey_id>', methods=['POST','GET'])
@login_required
def get_survey(survey_id):
    survey = Survey.query.filter_by(link=survey_id).first()
    question_list = Question.query.filter_by(surveyID=survey.id).all()
    
    if request.method=='GET':
        question_option_list = []
        for each_question in question_list:
            each_question_options = {}
            each_question_options['title'] = each_question.title
            each_question_options['subtitle'] = each_question.subtitle
            each_question_options['type'] = each_question.questionType
            each_question_options['id'] = each_question.id

            option_list = Option.query.filter_by(questionID=each_question.id).all()
            each_question_options['option_list'] = option_list
            question_option_list.append(each_question_options)
        return render_template("survey.html",survey=survey, question_list=question_option_list)
    else:
        user = User.query.filter_by(id=session['userid']).first()
        print request
        user.q_point += survey.que
        db.session.commit()
        db.session.flush()
        for each_question in question_list:
            print each_question.id
            each_answer = request.form[str(each_question.id)]
            answer = Answer(userID = user.id, content=each_answer, questionID=each_question.id)
            db.session.add(answer)
            db.session.commit()
            db.session.flush()
        return redirect('/survey/'+survey_id+'/result')


@app.route('/survey/<survey_id>/delete', methods=['POST'])
@login_required
def tmp_delete(survey_id):
    question = request.get_json()
    question_index = question['index']
    print question_index
    print session['tmp_question_dict'][survey_id]
    session['tmp_question_dict'][survey_id].pop(question_index)
    return jsonify({'result':'success'})


@app.route('/survey/<survey_id>/register', methods=['POST'])
@login_required
def register_survey(survey_id):
    survey = request.get_json()
    survey_size = survey['size']
    survey_title = survey['title']
    survey_subtitle = survey['subtitle']
    user = User.query.filter_by(id=session['userid']).first()
    if user.q_point < 100:
        return jsonify({'result':'q_shortage'})
    user.q_point -= 100
    question_len = len(session['tmp_question_dict'][survey_id])
    if question_len < 5:
        survey_que = question_len * 10
    else:
        survey_que = 50
    survey = Survey(link=survey_id, title=survey_title, subtitle=survey_subtitle, userID=user.id, que=survey_que)
    db.session.add(survey)
    db.session.commit()
    db.session.flush()
    session['userid'] = user.id


    for each_question in session['tmp_question_dict'][survey_id]: 
        question = Question(
            title=each_question['title'],
         subtitle=each_question['subtitle'],
         questionType=each_question['type'],
         isEssential=True, 
         surveyID=survey.id)
        db.session.add(question)
        db.session.commit()
        db.session.flush()
        question = Question.query.filter_by(title=question.title).first()
        for each_option in each_question['option']:
            option = Option(content=each_option, questionID=question.id)
            db.session.add(option)
            db.session.commit()
            db.session.flush()

    return jsonify({'result':'success'})




@app.route('/survey/<survey_link>/result', methods=['GET'])
@login_required
def survey_result(survey_link):
    survey = Survey.query.filter_by(link=survey_link).first()
    question_list = Question.query.filter_by(surveyID=survey.id).all()
    question_answers_dict_list = []
    for each_question in question_list:
        question_answers_dict = {}
        question_answers_dict['question'] = each_question
        question_answers_dict['answers'] = Answer.query.filter_by(questionID=each_question.id).all()
        question_answers_dict['answers_size'] = len(Answer.query.filter_by(questionID=each_question.id).all())
        question_answers_dict_list.append(question_answers_dict)
    print question_answers_dict_list
    answer_count = {}  

    answer_size = len(question_answers_dict['answers'])
    for each_answer in question_answers_dict['answers']:

        if each_answer.content in answer_count:
            answer_count[each_answer.content]['count'] += 1
        else:
            answer_count[each_answer.content] = {}
            answer_count[each_answer.content]['count'] = 1

    for content, statistic in answer_count.iteritems():
        answer_count[each_answer.content]['percentage'] = (statistic['count']*100) / answer_size
        print answer_count[each_answer.content]['percentage']


    return render_template('result.html', answer_count=answer_count, survey=survey, question_answers_dict_list=question_answers_dict_list)



@app.route('/')
@app.route('/login' , methods=['GET', 'POST'])
def login():
    if request.method=='GET':

        try:
            if 'request_url' in request.args:
                session['request_url'] = request.args['request_url']
        except Exception as e:
            print e
        if 'userid' in session:
            return redirect(url_for('main'))
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
        
        if 'request_url' in session:
            return redirect(session['request_url'])
        return redirect(url_for('main'))



@app.route('/fb_login' , methods=['POST'])
def fb_login():
    email = request.form['email']
    birthday = request.form['birthday']
    profile_picture = request.form['profile_picture']
    name = request.form['name']
    gender = request.form['gender']
    fb_id = request.form['id']
    print fb_id,email, birthday, profile_picture, name, gender
    user = User.query.filter_by(email=email).first()
    try:
        if not user.verify_password(password):
			error_msg = "아이디와 비밀번호를 확인해주세요"
			flash(error_msg)
			return render_template("login.html", error_msg=error_msg)
    except:
		password = fb_id
		user = User(email=email, gender=gender, birthday=birthday, profile_picture=profile_picture,password=password,q_point=1000 )
		db.session.add(user)
		db.session.commit()
		# user_hash = hashlib.sha1(str(user.id)).hexdigest()
		session['userid'] = user.id
    return redirect(url_for('main'))


@app.route('/main', methods=['POST','GET'])
@login_required
def main():
    if request.method=='GET':
        if not 'userid' in session:
            return redirect(url_for('login'))
        user = User.query.filter_by(id=session['userid']).first()
        username = re.match('(.*)(@)',user.email).group(1)
        search_query = request.args.get('search')
        if search_query is not None:
            survey_list = db.session.query(Survey).join(Question).filter(or_(
                Survey.title.contains(search_query),
                Survey.subtitle.contains(search_query),
                Question.title.contains(search_query),
                Question.subtitle.contains(search_query)
                )).order_by(Survey.register_timestamp).all()
        else:
            search_query = ''
            survey_list = Survey.query.order_by(Survey.register_timestamp).all()

        for i in range(len(survey_list)):
            like_list = Like.query.filter_by(surveyID=survey_list[i].id).all()
            if len(survey_list[i].title) > 20:
                survey_list[i].title = survey_list[i].title[:20] + '...'
            survey_list[i].like_len = len(like_list)
            survey_list[i].melike=False
            for each_like in like_list:
                if session['userid'] == each_like.userID:
                    survey_list[i].melike = True
                    break

            survey_question = Question.query.filter_by(surveyID=survey_list[i].id).first()
            survey_list[i].joined_len = len(Answer.query.filter_by(questionID=survey_question.id).all())
        return render_template("main.html", search_query=search_query,username=username,user_q=user.q_point, profile_picture=user.profile_picture,survey_list=survey_list)

@app.route('/like', methods=['POST'])
@login_required
def like():
    survey_id = request.get_json()['survey_id']
    survey_list = db.session.query(Question).join(Answer).filter(and_(Answer.userID==session['userid'],
        Question.surveyID==survey_id)).all()
    if(len(survey_list)==0):
        return jsonify({"result":"403"})
    already_like = Like.query.filter(and_(Like.userID==session['userid'], Like.surveyID==survey_id)).first()
    if already_like is not None:
        Like.query.filter(and_(Like.userID==session['userid'], Like.surveyID==survey_id)).delete()
        db.session.commit()
        return jsonify({"result":"unlike"})
    else:
        like = Like(userID=session['userid'], surveyID=survey_id)
        db.session.add(like)
        db.session.commit()
        return jsonify({"result":"like"})


import csv

@app.route('/survey/<survey_link>/download',methods=['get'])
def survey_download(survey_link):
    survey = Survey.query.filter_by(link=survey_link).first()
    question_list = Question.query.filter_by(surveyID=survey.id).all()
    question_answers_dict_list = []
    for each_question in question_list:
        question_answers_dict = {}
        question_answers_dict['question'] = each_question
        question_answers_dict['answers'] = Answer.query.filter_by(questionID=each_question.id).all()
        question_answers_dict['answers_size'] = len(Answer.query.filter_by(questionID=each_question.id).all())
        question_answers_dict_list.append(question_answers_dict)

    data_for_csv = []

    (file_basename, server_path, file_size) = create_csv(survey, question_answers_dict_list)
    print file_basename, server_path, file_size
    return_file = open(server_path+file_basename, 'r')
    
    response = make_response(return_file.read(),200)
    response.headers['Content-Description'] = 'File Transfer'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=%s' % file_basename
    response.headers['Content-Length'] = file_size
    print response
    return response

## function to create csv from the SQLAlchemy query response object
import time
import datetime

def create_csv(survey, question_answers_dict_list):
    """ returns (file_basename, server_path, file_size) """
    user = User.query.filter_by(id=survey.userID).first()

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('-%Y-%m-%d-%H:%M:%S')
    file_basename = str(survey.id) + st + '.csv'
    server_path = os.path.dirname(os.path.realpath(__file__))+"/csv/"
    w_file = open(str(server_path+file_basename),'w')

    w_file.write("title : "+survey.title + "\n")
    w_file.write("subtitle : "+survey.subtitle+"\n")
    w_file.write("user email : "+user.email+"\n")
    w_file.write("create time : "+str(survey.register_timestamp)+"\n")
    w_file.write("survey link : ques.co.kr/survey/"+survey.link+"\n")
    w_file.write("\n")
    for question_answers_dict in question_answers_dict_list:
        w_file.write("question title : "+question_answers_dict['question'].title+"\n")
        w_file.write("question subtitle : "+question_answers_dict['question'].subtitle+"\n")
        w_file.write("question type : "+question_answers_dict['question'].questionType+"\n")
        for each_answers in question_answers_dict['answers']:
            w_file.write(each_answers.content+','+str(each_answers.timestamp)+"\n")
        w_file.write("\n")
        
    w_file.close()

    w_file = open(server_path+file_basename,'r')
    # print w_file
    file_size = len(w_file.read())
    
    return file_basename, server_path, file_size


