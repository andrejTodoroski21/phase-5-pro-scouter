#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from flask import Flask, request, session, jsonify, render_template, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import random
from flask_bcrypt import Bcrypt

from models import db, User, Recruiter, Video, Like, Message, UserRecruiter

load_dotenv()

app = Flask(
    __name__,
    static_url_path='',
    static_folder='../client/dist',
    template_folder='../client/dist'
)
CORS(app,resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app)

app.secret_key = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
@app.errorhandler(404)
def not_found(e):
    return render_template("index.html")

migrate = Migrate(app, db)
bycrypt = Bcrypt(app)

db.init_app(app)

@app.route('/api/messages', methods=['POST'])
def send_message():
    data = request.json
    user_id = data.get('user_id')
    recruiter_id = data.get('recruiter_id')
    content = data.get('content')

    message = Message(
        user_message=user_id,
        recruiter_message=recruiter_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    socketio.emit('message', message.to_dict())
    return jsonify(message.to_dict()), 201

@socketio.on('message')
def handle_message(data):
    user_id = data['user_id']
    recruiter_id = data['recruiter_id']
    content = data['content']
    message = Message(
        user_message=user_id,
        recruiter_message=recruiter_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    emit('message', message.to_dict(), broadcast=True)

@app.get('/api/messages')
def get_messages():
    return [m.to_dict() for m in Message.query.all()], 200

@app.get('/api/users')
def get_all_users():
    return [u.to_dict() for u in User.query.all()], 200

@app.get('/api/users/<string:username>')
def get_user_by_username(username):
    user = User.query.filter(User.username == username).first()
    return user.to_dict(), 200

# user signup
@app.post('/api/signup')
def signup():
    try: 
        new_user = User(username=request.json['username'], first_name = request.json['first_name'], last_name = request.json['last_name'])
        new_user._hashed_password = bycrypt.generate_password_hash(request.json['_hashed_password']).decode('utf-8')
        db.session.add(new_user)
        db.session.commit()
        return new_user.to_dict(), 201
    except Exception as e:
        return {'error': str(e)}, 400

@app.post('/api/login')
def user_login():
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username).first()
    if user and bycrypt.check_password_hash(user._hashed_password, password):
        session['user_id'] = user.id
        return user.to_dict(), 201
    else: 
        return {'error': 'Invalid username or password'}, 401

# check to see if user is logged in
@app.get('/api/get-session-user')
def get_session_user():
    user_id = session.get('id')
    if user_id:
        user = User.query.get(user_id), 200
        if user:
            return user.to_dict(),200
    return {}, 404

@app.delete('/api/logout')
def logout():
    session.pop('user_id')  # Remove the user ID from the session on logout
    return {}, 204

# recruiter signup
@app.post('/api/recruiters')
def create_recruiter():
    try:
        new_recruiter = Recruiter(recruiter_username = request.json['recruiter_username'], recruiter_name = request.json['recruiter_name'])
        new_recruiter._hashed_password = bycrypt.generate_password_hash(request.json['_hashed_password']).decode('utf-8')
        db.session.add(new_recruiter)
        db.session.commit()
        return new_recruiter.to_dict()
    except Exception as e:
        return {'error': str(e)}, 400

@app.get('/api/recruiters')
def get_all_recruiters():
    return [r.to_dict() for r in Recruiter.query.all()], 200

# checks the session to see if recruiter is logged in
@app.get('/api/get-session-recruiter')
def get_session_recruiter():
    recruiter_id = session.get('recruiter_id')
    if recruiter_id:
        recruiter = Recruiter.query.get(user_id), 200
        if recruiter:
            return recruiter.to_dict(), 200
    return {'error':str(e)}, 400

# get all videos
@app.get('/api/videos')
def get_all_videos():
    return [v.to_dict() for v in Video.query.all()], 200

# posting a new video
@app.post('/api/videos')
def create_video():
    try:
        data = request.json
        new_video = Video(**data)
        db.session.add(new_video)
        db.session.commit()
        return jsonify(new_video.to_dict()), 201
    except Exception as e:
        return {'error':str(e)}, 400

# delete video by id, also checks to see if user is authorized to delete the video
@app.delete('/api/videos/<int:id>')
def delete_video(id):
    try:
        video = Video.query.get(id)
        if video:
            if video.id == session.get('user_id'):
                db.session.delete(video)
                db.session.commit()
                return {}, 200
            else:
                return {'error': 'You are not authorized to delete this video'}, 401
        else:
            return {'error': 'Video not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 406



if __name__ == '__main__':
    socketio.run(app, port=5555, debug=True)
