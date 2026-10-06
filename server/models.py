"""Database models.

Two things worth knowing:

1. Players and recruiters are one ``User`` table separated by ``role``. They
   used to be separate tables, which made the product's core action — a scout
   messaging a player — impossible to express, because both message foreign
   keys pointed at the players table.
2. Serialization is hand-written rather than ``SerializerMixin``. The mixin
   walks relationships recursively, so one ``/api/videos`` call would lazy-load
   every uploader and every like — an extra query per row.
"""
from sqlalchemy.ext.hybrid import hybrid_property

from extensions import bcrypt, db
from games import GAME_NAMES

PLAYER = 'player'
RECRUITER = 'recruiter'
ROLES = (PLAYER, RECRUITER)

#: How a clip's video is obtained. ``youtube`` holds an embed id in
#: ``file_path``; ``upload`` holds an object key in ``storage_key``.
YOUTUBE = 'youtube'
UPLOAD = 'upload'
SOURCES = (YOUTUBE, UPLOAD)


class User(db.Model):
    __tablename__ = 'users_table'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False, default=PLAYER, index=True)
    _hashed_password = db.Column(db.String, nullable=False)

    # Players have a name; recruiters have an organization. Each side's fields
    # are null for the other, which is why neither is required.
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    organization = db.Column(db.String, nullable=True)

    videos = db.relationship(
        'Video', back_populates='uploader',
        cascade='all, delete-orphan',
    )
    liked_videos = db.relationship(
        'Like', back_populates='user',
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

    @property
    def is_recruiter(self):
        return self.role == RECRUITER

    @property
    def display_name(self):
        if self.is_recruiter:
            return self.organization or self.username
        full = ' '.join(p for p in (self.first_name, self.last_name) if p)
        return full or self.username

    def to_dict(self):
        """Shallow — never includes the password hash or nested collections."""
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'display_name': self.display_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'organization': self.organization,
        }


class Video(db.Model):
    __tablename__ = 'videos_table'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    time_uploaded = db.Column(db.DateTime, server_default=db.func.now())
    # Slug from games.GAMES. Indexed because the feed is always filtered by it.
    game = db.Column(db.String(40), nullable=False, index=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users_table.id'), nullable=False, index=True,
    )

    source = db.Column(db.String(20), nullable=False, default=YOUTUBE)
    # Set when source is youtube: the bare embed id.
    file_path = db.Column(db.String, nullable=True)
    # Set when source is upload: the storage key, plus what we learned from
    # the file. duration_seconds is null when the container did not say.
    storage_key = db.Column(db.String, nullable=True)
    duration_seconds = db.Column(db.Float, nullable=True)
    size_bytes = db.Column(db.Integer, nullable=True)
    # sha256 of the uploaded bytes, so the same clip is not stored twice.
    content_hash = db.Column(db.String(64), nullable=True, index=True)

    uploader = db.relationship('User', back_populates='videos')
    likes = db.relationship(
        'Like', back_populates='video',
        cascade='all, delete-orphan',
    )

    @property
    def is_upload(self):
        return self.source == UPLOAD

    def video_url(self):
        """Playable URL for an uploaded clip, or None for a YouTube embed."""
        if not self.is_upload or not self.storage_key:
            return None
        import storage
        return storage.get().public_url(self.storage_key)

    def to_dict(self, like_count=None):
        """``like_count`` is passed in by the route so we avoid loading the rows."""
        return {
            'id': self.id,
            'title': self.title,
            'source': self.source,
            'file_path': self.file_path,
            'video_url': self.video_url(),
            'duration_seconds': self.duration_seconds,
            'game': self.game,
            'game_name': GAME_NAMES.get(self.game, self.game),
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


class Message(db.Model):
    __tablename__ = 'messages_table'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now(), index=True)

    # Both sides are plain users now, so a recruiter messaging a player is
    # just a row like any other.
    sender_id = db.Column(
        db.Integer, db.ForeignKey('users_table.id'), nullable=False, index=True,
    )
    recipient_id = db.Column(
        db.Integer, db.ForeignKey('users_table.id'), nullable=False, index=True,
    )

    sender = db.relationship(
        'User', foreign_keys=[sender_id], back_populates='sent_messages',
    )
    recipient = db.relationship(
        'User', foreign_keys=[recipient_id], back_populates='received_messages',
    )

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
        }
