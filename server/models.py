"""Database models.

Serialization is done with hand-written ``to_dict`` methods rather than
``SerializerMixin``. The mixin walks relationships recursively, so a single
``/api/videos`` call would lazy-load every uploader and every like — one extra
query per row. These methods return exactly the fields the client renders.
"""
from sqlalchemy.ext.hybrid import hybrid_property

from extensions import bcrypt, db


class User(db.Model):
    __tablename__ = 'users_table'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False, index=True)
    _hashed_password = db.Column(db.String, nullable=False)

    videos = db.relationship(
        'Video', back_populates='uploader',
        cascade='all, delete-orphan',
    )
    liked_videos = db.relationship(
        'Like', back_populates='user',
        cascade='all, delete-orphan',
    )
    recruiter_interactions = db.relationship(
        'UserRecruiter', back_populates='user',
        cascade='all, delete-orphan',
    )
    received_messages = db.relationship(
        'Message', foreign_keys='Message.recipient_id',
        back_populates='recipient',
    )
    sent_messages = db.relationship(
        'Message', foreign_keys='Message.sender_id',
        back_populates='sender',
    )

    @hybrid_property
    def password(self):
        raise AttributeError('password is write-only')

    @password.setter
    def password(self, plaintext):
        self._hashed_password = bcrypt.generate_password_hash(plaintext).decode('utf-8')

    def authenticate(self, plaintext):
        return bcrypt.check_password_hash(self._hashed_password, plaintext)

    def to_dict(self):
        """Shallow — never includes the password hash or nested collections."""
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': 'user',
        }


class Recruiter(db.Model):
    __tablename__ = 'recruiters_table'

    id = db.Column(db.Integer, primary_key=True)
    recruiter_name = db.Column(db.String, nullable=False)
    recruiter_username = db.Column(db.String, unique=True, nullable=False, index=True)
    _hashed_password = db.Column(db.String, nullable=False)

    interactions = db.relationship(
        'UserRecruiter', back_populates='recruiter',
        cascade='all, delete-orphan',
    )

    @hybrid_property
    def password(self):
        raise AttributeError('password is write-only')

    @password.setter
    def password(self, plaintext):
        self._hashed_password = bcrypt.generate_password_hash(plaintext).decode('utf-8')

    def authenticate(self, plaintext):
        return bcrypt.check_password_hash(self._hashed_password, plaintext)

    def to_dict(self):
        return {
            'id': self.id,
            'recruiter_username': self.recruiter_username,
            'recruiter_name': self.recruiter_name,
            'role': 'recruiter',
        }


class Video(db.Model):
    __tablename__ = 'videos_table'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    time_uploaded = db.Column(db.DateTime, server_default=db.func.now())
    file_path = db.Column(db.String, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users_table.id'), nullable=False, index=True,
    )

    uploader = db.relationship('User', back_populates='videos')
    likes = db.relationship(
        'Like', back_populates='video',
        cascade='all, delete-orphan',
    )

    def to_dict(self, like_count=None):
        """``like_count`` is passed in by the route so we avoid loading the rows."""
        return {
            'id': self.id,
            'title': self.title,
            'file_path': self.file_path,
            'time_uploaded': self.time_uploaded.isoformat() if self.time_uploaded else None,
            'user_id': self.user_id,
            'uploader': {
                'id': self.uploader.id,
                'username': self.uploader.username,
            } if self.uploader else None,
            'like_count': like_count if like_count is not None else len(self.likes),
        }


class Like(db.Model):
    __tablename__ = 'likes_table'

    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos_table.id'), primary_key=True)

    user = db.relationship('User', back_populates='liked_videos')
    video = db.relationship('Video', back_populates='likes')

    def to_dict(self):
        return {'user_id': self.user_id, 'video_id': self.video_id}


class UserRecruiter(db.Model):
    __tablename__ = 'users_recruiters_table'

    interaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users_table.id'), nullable=False, index=True,
    )
    recruiter_id = db.Column(
        db.Integer, db.ForeignKey('recruiters_table.id'), nullable=False, index=True,
    )
    interaction_type = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', back_populates='recruiter_interactions')
    recruiter = db.relationship('Recruiter', back_populates='interactions')
    messages = db.relationship(
        'Message', back_populates='interaction',
    )

    def to_dict(self):
        return {
            'interaction_id': self.interaction_id,
            'user_id': self.user_id,
            'recruiter_id': self.recruiter_id,
            'interaction_type': self.interaction_type,
        }


class Message(db.Model):
    __tablename__ = 'messages_table'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now(), index=True)

    sender_id = db.Column(
        db.Integer, db.ForeignKey('users_table.id'), nullable=False, index=True,
    )
    recipient_id = db.Column(
        db.Integer, db.ForeignKey('users_table.id'), nullable=False, index=True,
    )
    interaction_id = db.Column(
        db.Integer, db.ForeignKey('users_recruiters_table.interaction_id'),
        nullable=True, index=True,
    )

    sender = db.relationship(
        'User', foreign_keys=[sender_id], back_populates='sent_messages',
    )
    recipient = db.relationship(
        'User', foreign_keys=[recipient_id], back_populates='received_messages',
    )
    interaction = db.relationship('UserRecruiter', back_populates='messages')

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'interaction_id': self.interaction_id,
        }
