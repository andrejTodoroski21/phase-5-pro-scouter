from routes.auth import auth_bp
from routes.messages import messages_bp
from routes.videos import videos_bp


def register_blueprints(app):
    import routes.events  # noqa: F401  (registers the Socket.IO handlers)

    for bp in (auth_bp, videos_bp, messages_bp):
        app.register_blueprint(bp)
