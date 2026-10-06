"""Signed auth tokens.

React Native has no usable cookie jar, so the mobile app cannot rely on the
Flask session cookie the web client uses. Login and signup therefore return a
JWT alongside the user, and requests may authenticate with either:

    Authorization: Bearer <token>     (mobile)
    session cookie                    (web, unchanged)

Both paths resolve to the same user, so the web client keeps working untouched
while the app has something it can actually store.
"""
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app

ALGORITHM = 'HS256'
TOKEN_LIFETIME = timedelta(days=30)


def issue(user):
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(user.id),
        'role': user.role,
        'iat': now,
        'exp': now + TOKEN_LIFETIME,
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm=ALGORITHM)


def user_id_from(token):
    """Return the user id in a valid token, or None.

    Returns None rather than raising so callers can fall through to the session
    cookie without having to catch anything.
    """
    if not token:
        return None
    try:
        payload = jwt.decode(
            token, current_app.config['SECRET_KEY'], algorithms=[ALGORITHM],
        )
    except jwt.PyJWTError:
        return None
    try:
        return int(payload.get('sub'))
    except (TypeError, ValueError):
        return None


def from_header(header_value):
    """Pull the token out of an ``Authorization: Bearer <token>`` header."""
    if not header_value:
        return None
    scheme, _, token = header_value.partition(' ')
    if scheme.lower() != 'bearer':
        return None
    return token.strip() or None
