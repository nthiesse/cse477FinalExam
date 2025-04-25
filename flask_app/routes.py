# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from datetime import datetime, timedelta
import sys
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

# socketio = SocketIO(app, cors_allowed_origins="*")
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


# register a new user page 
@app.route('/register')
def register():
    return render_template('register.html', user=getUser())



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

    session['email'] = db.reversibleEncrypt('encrypt', email)
    return json.dumps({'status': 1})


# process if a user is trying to register 
@app.route('/processregistration', methods=["POST", "GET"])
def processregistration():
    # get the email and password from the post
    email = request.form.get("email")
    password = request.form.get("password")

    # authenticate the login
    temp = db.createUser(email=email, password=password)
    if temp.get('status') == 2:
        print("Email already exists in the database")
        return json.dumps({'status': 2})

    session['email'] = db.reversibleEncrypt('encrypt', email)
    return json.dumps({'status': 1})


#######################################################################################
# CHATROOM RELATED
#######################################################################################
# @app.route('/chat')
# @login_required
# def chat():
#     return render_template('chat.html', user=getUser())


# @socketio.on('joined', namespace='/chat')
# def joined(message):
#     join_room('main')
#     role = db.getUserRole(getUser())

#     if role == "owner":
#         emit('status', {'msg': getUser() + ' has entered the room.',
#              'style': 'width: 100%; color: blue; text-align: right'}, room='main')
#     else:
#         emit('status', {'msg': getUser() + ' has entered the room.',
#              'style': 'width: 100%; color: grey; text-align: left'}, room='main')


# @socketio.on('message', namespace='/chat')
# def handle_message(data):
#     role = db.getUserRole(getUser())

#     if role == "owner":
#         emit('message', {
#              'msg': data['msg'], 'style': 'width: 100%; color: blue; text-align: right'}, room='main')
#     else:
#         emit('message', {
#              'msg': data['msg'], 'style': 'width: 100%; color: grey; text-align: left'}, room='main')


# @socketio.on('leaveChat', namespace='/chat')
# def leaveChat(message):
#     leave_room('main')
#     role = db.getUserRole(getUser())
#     if role == "owner":
#         emit('status', {'msg': getUser() + ' has left the room.',
#              'style': 'width: 100%; color: blue; text-align: right'}, room='main')
#     else:
#         emit('status', {'msg': getUser() + ' has left the room.',
#              'style': 'width: 100%; color: grey; text-align: left'}, room='main')




#######################################################################################
# OTHER
#######################################################################################
@app.route('/')
def root():
    return redirect('/home')


@app.route('/home')
def home():
    return render_template('home.html', user=getUser())


@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

@app.route('/events')
def events():
    return render_template('events.html', user=getUser())


@app.route('/createevent')
def createevent():
    return render_template('createevent.html', user=getUser())


@app.route('/joinevent', methods=['GET'])
def joinevent():
    user = getUser()
    user_events = db.getEventsForUser(user)

    return render_template('joinevent.html', events=user_events, user=getUser())


    



@app.route('/event_page/<int:event_id>', methods=['GET'])
def event_page(event_id): 
    # get the event's name, dates, and time frame 
    event_details = db.getNameDateTime(event_id)

    # structure the dates in a way each day can be figured out 
    date_start = datetime.strptime(event_details['start_date'], '%B %d, %Y').date()
    date_end = datetime.strptime(event_details['end_date'], '%B %d, %Y').date()
    num_days = (date_end - date_start).days + 1
    all_dates = []
    for i in range(num_days): 
        all_dates.append(date_start + timedelta(days=i))

    # format the times 
    time_start = datetime.combine(datetime.today(), event_details['start_time'])
    time_end = datetime.combine(datetime.today(), event_details['end_time'])

    all_times = []
    while time_start <= time_end: 
        all_times.append(time_start.strftime('%I:%M %p'))
        time_start += timedelta(minutes=30)

    print("ALL times", all_times)

    return render_template('event_page.html', event_id=event_id, event=event_details, dates=all_dates, times=all_times, user=getUser())


# creating an event information processing 
@app.route('/create_event_info', methods=['POST'])
def create_event_info(): 
    event_name = request.form.get('event_name')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    invitees_raw = request.form.get('invitees')

    # separate the emails and put into a list 
    people = [email.strip() for email in invitees_raw.split(',') if email.strip()]
    people.append(getUser())

    # pass to database 
    temp = json.loads(db.addEvent(event_name, start_date, end_date, start_time, end_time, people, getUser()))
    if temp.get('status') == 2: 
        print("Failure in adding event to database (this is from routes.py")
        
    event_id = temp.get('id')
    return redirect(f'/event_page/{event_id}')


# adds a users availability based on how they filled out the when to meet grid to the database 
@app.route('/add_availability/<int:event_id>', methods=['POST'])
def add_availability(event_id): 
    data = request.get_json()
    user = getUser()  
    # tell the database to add the values 
    db.addEventAvailability(user, event_id, data[0]['date'], data[0]['time_slot'], data[0]['available'])
    return json.dumps({'status': 1})


@app.route('/load_availability/<int:event_id>', methods=['GET'])
def load_availability(event_id): 
    user = getUser()
    # get the availability for the user for the specific event from the database 
    temp = db.getEventAvailability(user, event_id)
    if temp['status'] == 1: 
        return json.dumps({'status': 1, 'data': temp['data']})
    elif temp['status'] == 2: 
        return json.dumps({'status': 2, 'data': 'No data for user'})
    else: 
        return json.dumps({'status': 3, 'data': 'Error occured'})


# get the heat map information from the database 
@app.route('/get_heatmap_info/<int:event_id>', methods=['GET'])
def get_heatmap_info(event_id): 
    heatmap_info = db.getHeatMapInfo(event_id)
    if heatmap_info['status'] == 1: 
        # print("HEAT MAP INFOR", heatmap_info)
        return json.dumps(heatmap_info)
    else: 
        return json.dumps({'status': 2, 'data': 'issue in getting heat map'})


# get the best time calculation from the database
@app.route('/get_best_time/<int:event_id>', methods=['GET'])
def get_best_time(event_id): 
    return json.dumps(calculate_best_time(event_id))
    


def calculate_best_time(event_id):
    best_time = db.getBestTime(event_id)
    if best_time['status'] == 1:
        return {'status': 1, 'date': str(best_time['data'][0]), 'time': str(best_time['data'][1])}
    elif best_time['status'] == 2:
        return {'status': 2, 'date': 'NULL', 'time': 'NULL'}
    elif best_time['status'] == 3:
        return {'status': 3, 'date': str(best_time['data'][0]), 'time': str(best_time['data'][1])}
    else:
        return {'status': 4}



# socket functions: 
@socketio.on('join_event')
def join_event(id): 
    # event = id['event_id']
    event = id
    join_room(event)
    print("JOINING ROOM")


@socketio.on('availability_changed')
def update_availability(data):
    with app.app_context():
        event_id = data['event_id']
        
        temp = db.getBestTime(event_id)
        if temp['status'] == 1:
            best_time = {'status': 1, 'date': str(temp['data'][0]), 'time': str(temp['data'][1])}
        elif temp['status'] == 2:
            best_time = {'status': 2, 'date': 'NULL', 'time': 'NULL'}
        elif temp['status'] == 3:
            best_time = {'status': 3, 'date': str(temp['data'][0]), 'time': str(temp['data'][1])}
        else:
            best_time = {'status': 4}

        print('EMITTING BEST TIME AND HEAT MAP')
        emit('best_time_update', best_time, room=event_id)
        # emit('heatmap_update', {}, room=event_id, include_self=False)
        emit('heatmap_update', room=event_id)


