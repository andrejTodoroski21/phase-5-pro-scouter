"""Shared extension instances.

Kept in their own module so models and blueprints can import them without
creating a circular import back to ``app``.
"""
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
})

db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
bcrypt = Bcrypt()
cors = CORS()
socketio = SocketIO()
