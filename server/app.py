#!/usr/bin/env python3
"""Application factory.

``app`` is still exposed at module level so ``flask db migrate`` and
``python app.py`` keep working exactly as the README describes.
"""
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, send_from_directory

from extensions import bcrypt, cors, db, migrate, socketio

load_dotenv()

CLIENT_DIST = (Path(__file__).resolve().parent.parent / 'client' / 'dist')


def create_app(config=None):
    app = Flask(
        __name__,
        # Static files are served by the SPA catch-all below so that the
        # long-lived cache headers actually get applied to Vite's assets.
        static_folder=None,
        template_folder=str(CLIENT_DIST),
    )

    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-only-insecure-key'),
        SQLALCHEMY_DATABASE_URI=_database_url(),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        # Pre-ping keeps pooled connections from going stale on hosted Postgres,
        # which otherwise shows up as a multi-second hang on the first request.
        SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping': True},
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        JSON_SORT_KEYS=False,
    )
    if config:
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db, directory=str(Path(__file__).resolve().parent / 'migrations'))
    bcrypt.init_app(app)
    # Credentials must be allowed for the session cookie to survive a
    # cross-origin request; that rules out the "*" origin wildcard.
    cors.init_app(
        app,
        resources={r'/api/*': {'origins': _allowed_origins()}},
        supports_credentials=True,
    )
    socketio.init_app(app, cors_allowed_origins=_allowed_origins())

    import models  # noqa: F401  (registers the mapped classes)
    from routes import register_blueprints
    register_blueprints(app)

    _register_spa(app)
    return app


def _database_url():
    """Local SQLite unless DATABASE_URL is set.

    Pointing local development at a remote free-tier Postgres adds a network
    round trip to every single query, which reads as a slow site.
    """
    url = os.environ.get('DATABASE_URL', '').strip()
    if not url:
        return 'sqlite:///app.db'
    # SQLAlchemy dropped the legacy postgres:// scheme.
    return url.replace('postgres://', 'postgresql://', 1)


def _allowed_origins():
    raw = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173')
    return [o.strip() for o in raw.split(',') if o.strip()]


def _register_spa(app):
    """Serve the built client, with long cache lifetimes on hashed assets."""

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_client(path):
        target = CLIENT_DIST / path
        if path and target.is_file():
            response = send_from_directory(str(CLIENT_DIST), path)
            if path.startswith('assets/'):
                # Vite fingerprints these filenames, so they are safe to pin.
                response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
            return response
        if not (CLIENT_DIST / 'index.html').is_file():
            return {'error': 'client not built — run `npm run build --prefix client`'}, 404
        return send_from_directory(str(CLIENT_DIST), 'index.html')


app = create_app()

if __name__ == '__main__':
    socketio.run(app, port=5555, debug=True, allow_unsafe_werkzeug=True)
