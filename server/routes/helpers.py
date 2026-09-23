"""Small shared helpers for the API blueprints."""
from functools import wraps

from flask import session

from models import Recruiter, User
from extensions import db


def current_user():
    user_id = session.get('user_id')
    return db.session.get(User, user_id) if user_id else None


def current_recruiter():
    recruiter_id = session.get('recruiter_id')
    return db.session.get(Recruiter, recruiter_id) if recruiter_id else None


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return {'error': 'Unauthorized'}, 401
        return view(*args, user=user, **kwargs)
    return wrapper


def json_body(*required):
    """Return (data, error). ``error`` is a ready-to-return response tuple."""
    from flask import request
    data = request.get_json(silent=True) or {}
    missing = [f for f in required if not data.get(f)]
    if missing:
        return None, ({'error': f"Missing required fields: {', '.join(missing)}"}, 400)
    return data, None
