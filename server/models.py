from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    __tablename__ = 'users_table'

    serialize_rules = ('-videos', '-liked_videos', '-recruiter_interactions.user', '-sent_messages.sender',)

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    _hashed_password = db.Column(db.String, nullable=False)

    videos = db.relationship('Video', back_populates='uploader', lazy=True)
    liked_videos = db.relationship('Like', back_populates='user', lazy=True)
    recruiter_interactions = db.relationship('UserRecruiter', back_populates='user', lazy=True)
    sent_messages = db.relationship('Message', back_populates='sender', foreign_keys='Message.user_message', lazy=True)

class Recruiter(db.Model, SerializerMixin):
    __tablename__ = "recruiters_table"

    serialize_rules = ('-interactions.recruiter', '-received_messages.receiver',)

    id = db.Column(db.Integer, primary_key=True)
    recruiter_name = db.Column(db.String, nullable=False)
    recruiter_username = db.Column(db.String, nullable=False)
    _hashed_password = db.Column(db.String, nullable=False)

    interactions = db.relationship('UserRecruiter', back_populates='recruiter', lazy=True)
    received_messages = db.relationship('Message', back_populates='receiver', foreign_keys='Message.recruiter_message', lazy=True)

class Video(db.Model, SerializerMixin):
    __tablename__ = "videos_table"

    serialize_rules = ('-uploader.videos', '-likes.video',)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    time_uploaded = db.Column(db.DateTime, server_default=db.func.now())
    file_path = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'))

    uploader = db.relationship('User', back_populates='videos')
    likes = db.relationship('Like', back_populates='video', lazy=True)

class Like(db.Model, SerializerMixin):
    __tablename__ = "likes_table"

    serialize_rules = ('-user.liked_videos', '-video.likes',)

    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos_table.id'), primary_key=True)

    user = db.relationship('User', back_populates='liked_videos')
    video = db.relationship('Video', back_populates='likes')

class Message(db.Model, SerializerMixin):
    __tablename__ = 'messages_table'

    serialize_rules = ('-sender.sent_messages', '-receiver.received_messages', '-interaction.messages',)

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    user_message = db.Column(db.Integer, db.ForeignKey('users_table.id'))
    recruiter_message = db.Column(db.Integer, db.ForeignKey('recruiters_table.id'), nullable=False)
    interaction_id = db.Column(db.Integer, db.ForeignKey('users_recruiters_table.interaction_id'))
    
    sender = db.relationship('User', back_populates='sent_messages', foreign_keys=[user_message])
    receiver = db.relationship('Recruiter', back_populates='received_messages', foreign_keys=[recruiter_message])
    interaction = db.relationship('UserRecruiter', back_populates='messages')

class UserRecruiter(db.Model, SerializerMixin):
    __tablename__ = 'users_recruiters_table'

    serialize_rules = ('-user.recruiter_interactions', '-recruiter.interactions', '-messages.interaction',)

    interaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), nullable=False)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiters_table.id'), nullable=False)
    interaction_type = db.Column(db.String(50), nullable=False)  # e.g., 'view', 'message'

    user = db.relationship('User', back_populates='recruiter_interactions')
    recruiter = db.relationship('Recruiter', back_populates='interactions')
    messages = db.relationship('Message', back_populates='interaction', lazy=True)
