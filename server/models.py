from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from by

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class User(db.Model):
    __tablename__ = 'users_table'

    id = db.Column(db.Integer, primary_key =True)
    first_name = db.Column(db.String, nullable = False)
    last_name = db.Column(db.String, nullable = False)
    username = db.Column(db.String, nullable = False)
    _hashed_password = db.Column(db.String, nullable = False)
    
    # videos and liked_videos relationship
    videos = db.relationship('Video', back_populates='users')
    liked_videos = db.relationship('Like', back_populates='users')

class Video(db.Model):
    __tablename__ = "videos_table"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    time_uploaded = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    
