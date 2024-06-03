#!/usr/bin/env python3
import os
from flask import Flask, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt

from models import db, User, Recruiter, Video, Like, Message, UserRecruiter

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)

migrate = Migrate(app, db)
bycrypt = Bcrypt(app)

db.init_app(app)

@app.get('/api/users')
def get_all_users():
    return [u.to_dict() for u in User.query.all()], 200

@app.post('/api/users')
def signup():
    try: 
        new_user = User(username=request.json['username'], first_name = request.json['first_name'], last_name = request.json['last_name'])
        new_user._hashed_password = bycrypt.generate_password_hash(request.json['password']).decode('utf-8')
        db.session.add(new_user)
        db.session.commit()
        return new_user.to_dict(), 201
    except Exception as e:
        return {'error': str(e)}, 400

@app.get('/api/get-session-user')
def get_session_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id), 200
        if user:
            return user.to_dict(),200
    return {'error': 'User not found'}, 404

@app.post('/api/recruiters')
def create_recruiter():
    try:
        new_recruiter = Recruiter(recruiter_username = request.json['recruiter_username'], recruiter_name = request.json['recruiter_name'])
        new_recruiter._hashed_password = bycrypt.generate_password_hash(request.json['password']).decode('utf-8')
            


# write your routes here! 
# all routes should start with '/api' to account for the proxy


if __name__ == '__main__':
    app.run(port=5555, debug=True)
