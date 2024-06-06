#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from flask import Flask, request, session, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt

from models import db, User, Recruiter, Video, Like, Message, UserRecruiter

load_dotenv()

app = Flask(
    __name__,
    static_url_path='',
    static_folder='../client/dist',
    template_folder='../client/dist'
)

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
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id), 200
        if user:
            return user.to_dict(),200
    return {'error': 'User not found'}, 404

# recruiter signup
@app.post('/api/recruiters')
def create_recruiter():
    try:
        new_recruiter = Recruiter(recruiter_username = request.json['recruiter_username'], recruiter_name = request.json['recruiter_name'])
        new_recruiter._hashed_password = bycrypt.generate_password_hash(request.json['password']).decode('utf-8')
        db.session.add(new_recruiter)
        db.session.commit()
        return new_recruiter
    except Exception as e:
        return {'error': str(e)}, 400

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




            


# write your routes here! 
# all routes should start with '/api' to account for the proxy


if __name__ == '__main__':
    app.run(port=5555, debug=True)
