"""Socket.IO events.

Each logged-in client is put in a room named after its user id so a new message
is pushed only to the two participants instead of broadcast to everyone.
"""
from flask import session
from flask_socketio import join_room

from extensions import socketio


def room_for(user_id):
    return f'user:{user_id}'


@socketio.on('connect')
def on_connect():
    user_id = session.get('user_id')
    if user_id:
        join_room(room_for(user_id))
