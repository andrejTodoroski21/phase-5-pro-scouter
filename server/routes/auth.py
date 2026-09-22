"""Signup, login, logout and session lookup for both users and recruiters."""
from flask import Blueprint, session
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Recruiter, User
from routes.helpers import current_recruiter, current_user, json_body

auth_bp = Blueprint('auth', __name__, url_prefix='/api')


@auth_bp.post('/signup')
def signup():
    data, error = json_body('username', 'first_name', 'last_name', 'password')
    if error:
        return error
    user = User(
        username=data['username'],
        first_name=data['first_name'],
        last_name=data['last_name'],
    )
    user.password = data['password']
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'That username is already taken'}, 409
    session['user_id'] = user.id
    session.permanent = True
    return user.to_dict(), 201


@auth_bp.post('/login')
def login():
    data, error = json_body('username', 'password')
    if error:
        return error
    user = User.query.filter_by(username=data['username']).first()
    if user and user.authenticate(data['password']):
        session['user_id'] = user.id
        session.permanent = True
        return user.to_dict(), 200
    return {'error': 'Invalid username or password'}, 401


@auth_bp.delete('/logout')
def logout():
    session.pop('user_id', None)
    return {}, 204


@auth_bp.get('/get-session-user')
def get_session_user():
    user = current_user()
    return (user.to_dict(), 200) if user else ({}, 204)


@auth_bp.post('/recruiters')
def create_recruiter():
    data, error = json_body('recruiter_username', 'recruiter_name', 'password')
    if error:
        return error
    recruiter = Recruiter(
        recruiter_username=data['recruiter_username'],
        recruiter_name=data['recruiter_name'],
    )
    recruiter.password = data['password']
    db.session.add(recruiter)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'That username is already taken'}, 409
    session['recruiter_id'] = recruiter.id
    session.permanent = True
    return recruiter.to_dict(), 201


@auth_bp.post('/recruiters-login')
def recruiter_login():
    data, error = json_body('recruiter_username', 'password')
    if error:
        return error
    recruiter = Recruiter.query.filter_by(
        recruiter_username=data['recruiter_username'],
    ).first()
    if recruiter and recruiter.authenticate(data['password']):
        session['recruiter_id'] = recruiter.id
        session.permanent = True
        return recruiter.to_dict(), 200
    return {'error': 'Invalid username or password'}, 401


@auth_bp.delete('/recruiters-logout')
def recruiter_logout():
    session.pop('recruiter_id', None)
    return {}, 204


@auth_bp.get('/get-session-recruiter')
def get_session_recruiter():
    recruiter = current_recruiter()
    return (recruiter.to_dict(), 200) if recruiter else ({}, 204)


@auth_bp.get('/recruiters')
def list_recruiters():
    return [r.to_dict() for r in Recruiter.query.all()], 200


@auth_bp.get('/users')
def list_users():
    return [u.to_dict() for u in User.query.all()], 200


@auth_bp.get('/users/<string:username>')
def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return {'error': 'User not found'}, 404
    return user.to_dict(), 200
