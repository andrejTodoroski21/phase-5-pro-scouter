"""Direct messaging between users."""
from flask import Blueprint
from sqlalchemy import case, func, or_, select

from extensions import db, socketio
from models import Message, User
from routes.helpers import json_body, login_required

messages_bp = Blueprint('messages', __name__, url_prefix='/api')

CONVERSATION_PAGE_SIZE = 100


@messages_bp.get('/conversations')
@login_required
def list_conversations(user):
    """Everyone this user has exchanged messages with, plus the last message.

    Built as two queries instead of walking ``user.sent_messages`` and
    ``user.received_messages`` in Python, which pulled the whole table.
    """
    partner = case(
        (Message.sender_id == user.id, Message.recipient_id),
        else_=Message.sender_id,
    ).label('partner_id')

    latest = (
        select(partner, func.max(Message.id).label('last_id'))
        .where(or_(Message.sender_id == user.id, Message.recipient_id == user.id))
        .group_by(partner)
        .subquery()
    )

    rows = db.session.execute(
        select(User, Message)
        .join(latest, latest.c.partner_id == User.id)
        .join(Message, Message.id == latest.c.last_id)
        .order_by(Message.timestamp.desc())
    ).all()

    return [
        {
            **partner_user.to_dict(),
            'last_message': last_message.content,
            'timestamp': last_message.timestamp.isoformat() if last_message.timestamp else None,
        }
        for partner_user, last_message in rows
    ], 200


@messages_bp.get('/messages/<int:recipient_id>')
@login_required
def get_chat_history(recipient_id, user):
    messages = (
        Message.query
        .filter(
            or_(
                (Message.sender_id == user.id) & (Message.recipient_id == recipient_id),
                (Message.sender_id == recipient_id) & (Message.recipient_id == user.id),
            )
        )
        .order_by(Message.timestamp.asc(), Message.id.asc())
        .limit(CONVERSATION_PAGE_SIZE)
        .all()
    )
    return [m.to_dict() for m in messages], 200


@messages_bp.post('/messages')
@login_required
def create_message(user):
    data, error = json_body('content', 'recipient_id')
    if error:
        return error
    if not db.session.get(User, data['recipient_id']):
        return {'error': 'Recipient not found'}, 404

    message = Message(
        content=data['content'],
        sender_id=user.id,
        recipient_id=data['recipient_id'],
    )
    db.session.add(message)
    db.session.commit()

    payload = message.to_dict()
    # Only the two participants need this, not every connected client.
    socketio.emit('new_message', payload, to=f'user:{message.recipient_id}')
    return payload, 201
