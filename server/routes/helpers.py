"""Small shared helpers for the API blueprints."""
from functools import wraps

import tokens
from extensions import db
from flask import request, session
from models import RECRUITER, User


def current_user():
    """Resolve the caller from a bearer token, falling back to the session.

    Token first so the mobile app wins when both are somehow present.
    """
    user_id = tokens.user_id_from(tokens.from_header(request.headers.get('Authorization')))
    if user_id is None:
        user_id = session.get('user_id')
    return db.session.get(User, user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return {'error': 'Unauthorized'}, 401
        return view(*args, user=user, **kwargs)
    return wrapper


def recruiter_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return {'error': 'Unauthorized'}, 401
        if user.role != RECRUITER:
            return {'error': 'Recruiters only'}, 403
        return view(*args, user=user, **kwargs)
    return wrapper


def json_body(*required):
    """Return (data, error). ``error`` is a ready-to-return response tuple."""
    data = request.get_json(silent=True) or {}
    missing = [f for f in required if not data.get(f)]
    if missing:
        return None, ({'error': f"Missing required fields: {', '.join(missing)}"}, 400)
    return data, None
