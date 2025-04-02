# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database import database
from werkzeug.datastructures import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from . import socketio
db = database()


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function


def getUser():
    #return session['email'] if 'email' in session else 'Unknown'
    return db.reversibleEncrypt(type="decrypt", message=session['email']) if 'email' in session else 'Unknown'


@app.route('/login')
def login():
    return render_template('login.html', user=getUser())


@app.route('/logout')
def logout():
    session.pop('email', default=None)
    return redirect('/')


@app.route('/processlogin', methods=["POST", "GET"])
def processlogin():
    # get the email and password from the post
    email = request.form.get("email")
    password = request.form.get("password")

    # authenticate the login
    temp = db.authenticate(email=email, password=password)
    if temp.get('status') == 2:
        print("Email and password combination not in the database")
        return json.dumps({'status': 2})

    # session['email'] = email
    session['email'] = db.reversibleEncrypt('encrypt', email)
    return json.dumps({'status': 1})


#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=getUser())


@socketio.on('joined', namespace='/chat')
def joined(message):
    join_room('main')
    role = db.getUserRole(getUser())

    if role == "owner":
        emit('status', {'msg': getUser() + ' has entered the room.',
             'style': 'width: 100%; color: blue; text-align: right'}, room='main')
    else:
        emit('status', {'msg': getUser() + ' has entered the room.',
             'style': 'width: 100%; color: grey; text-align: left'}, room='main')


@socketio.on('message', namespace='/chat')
def handle_message(data):
    role = db.getUserRole(getUser())

    if role == "owner":
        emit('message', {
             'msg': data['msg'], 'style': 'width: 100%; color: blue; text-align: right'}, room='main')
    else:
        emit('message', {
             'msg': data['msg'], 'style': 'width: 100%; color: grey; text-align: left'}, room='main')


@socketio.on('leaveChat', namespace='/chat')
def leaveChat(message):
    leave_room('main')
    role = db.getUserRole(getUser())
    if role == "owner":
        emit('status', {'msg': getUser() + ' has left the room.',
             'style': 'width: 100%; color: blue; text-align: right'}, room='main')
    else:
        emit('status', {'msg': getUser() + ' has left the room.',
             'style': 'width: 100%; color: grey; text-align: left'}, room='main')


#######################################################################################
# OTHER
#######################################################################################
@app.route('/')
def root():
    return redirect('/home')


@app.route('/home')
def home():
    print(db.query('SELECT * FROM users'))
    x = random.choice(['I love to read books.',
                      'My favorite season is summer.', 'My favorite animal is a cow'])
    return render_template('home.html', user=getUser(), fun_fact=x)


@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r


@app.route('/resume')
def resume():
    resume_data = db.getResumeData()
    # pprint(resume_data)
    return render_template('resume.html', resume_data=resume_data)


@app.route('/projects')
def projects():
    return render_template('projects.html')


@app.route('/processfeedback', methods=['POST'])
def processfeedback():
    feedback = request.form
    name = feedback.get("name")
    email = feedback.get("email")
    comment = feedback.get("comment")
    db.insertRows(table="feedback", columns=[
                  "name", "email", "comment"], parameters=[[name, email, comment]])
    feedback_data = db.getFeedbackRows()
    return render_template('processfeedback.html', feedback_data=feedback_data)
