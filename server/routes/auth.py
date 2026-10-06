"""Signup, login, logout and session lookup.

Players and recruiters share these routes now; ``role`` in the signup body is
the only thing that differs. This replaces four near-identical pairs of routes
that existed when the two were separate tables.
"""
import tokens
from extensions import db
from flask import Blueprint, request, session
from models import PLAYER, RECRUITER, ROLES, User
from routes.helpers import current_user, json_body
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__, url_prefix='/api')


def _authenticated(user, status):
    """Log the user in on both channels and return the standard payload."""
    session['user_id'] = user.id
    session.permanent = True
    return {**user.to_dict(), 'token': tokens.issue(user)}, status


@auth_bp.post('/signup')
def signup():
    data, error = json_body('username', 'password')
    if error:
        return error

    role = data.get('role', PLAYER)
    if role not in ROLES:
        return {'error': f"role must be one of: {', '.join(ROLES)}"}, 400

    if role == RECRUITER and not data.get('organization'):
        return {'error': 'Missing required fields: organization'}, 400
    if role == PLAYER and not (data.get('first_name') and data.get('last_name')):
        return {'error': 'Missing required fields: first_name, last_name'}, 400

    user = User(
        username=data['username'],
        role=role,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        organization=data.get('organization'),
    )
    user.password = data['password']
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'That username is already taken'}, 409
    return _authenticated(user, 201)


@auth_bp.post('/login')
def login():
    data, error = json_body('username', 'password')
    if error:
        return error
    user = User.query.filter_by(username=data['username']).first()
    if user and user.authenticate(data['password']):
        return _authenticated(user, 200)
    return {'error': 'Invalid username or password'}, 401


@auth_bp.delete('/logout')
def logout():
    session.pop('user_id', None)
    return {}, 204


@auth_bp.get('/me')
def me():
    user = current_user()
    return (user.to_dict(), 200) if user else ({}, 204)


@auth_bp.get('/users')
def list_users():
    """All users, optionally narrowed by role: ``/api/users?role=player``."""
    query = User.query
    role = request.args.get('role')
    if role:
        if role not in ROLES:
            return {'error': f"role must be one of: {', '.join(ROLES)}"}, 400
        query = query.filter(User.role == role)
    return [u.to_dict() for u in query.order_by(User.username).all()], 200


@auth_bp.get('/users/<string:username>')
def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return {'error': 'User not found'}, 404
    return user.to_dict(), 200
