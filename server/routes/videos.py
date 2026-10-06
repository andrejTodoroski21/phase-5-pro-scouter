"""Video listing, upload and deletion."""
import games
from extensions import db
from flask import Blueprint, request
from models import Like, Video
from routes.helpers import json_body, login_required
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

videos_bp = Blueprint('videos', __name__, url_prefix='/api')

MAX_PAGE_SIZE = 50


@videos_bp.get('/games')
def list_games():
    """The game list with clip counts, for the home screen's game picker.

    One grouped query for the counts rather than one per game.
    """
    counts = dict(db.session.execute(
        select(Video.game, func.count(Video.id)).group_by(Video.game)
    ).all())
    return [
        {**game, 'clip_count': counts.get(game['slug'], 0)}
        for game in games.GAMES
    ], 200


@videos_bp.get('/videos')
def list_videos():
    """One query for the rows (uploader joined in) and one for the like counts.

    Previously this was 1 + 2N queries: the serializer lazy-loaded each video's
    uploader and its full like collection just to render a username.
    """
    page = max(request.args.get('page', 1, type=int), 1)
    per_page = min(request.args.get('per_page', 12, type=int), MAX_PAGE_SIZE)
    user_id = request.args.get('user_id', type=int)
    game = request.args.get('game')

    if game and not games.is_valid(game):
        return {'error': f'Unknown game: {game}'}, 400

    query = Video.query.options(joinedload(Video.uploader))
    if user_id:
        query = query.filter(Video.user_id == user_id)
    if game:
        query = query.filter(Video.game == game)

    pagination = query.order_by(Video.time_uploaded.desc(), Video.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False,
    )
    rows = pagination.items
    like_counts = _like_counts([v.id for v in rows])

    return {
        'videos': [v.to_dict(like_count=like_counts.get(v.id, 0)) for v in rows],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'has_next': pagination.has_next,
    }, 200


def _like_counts(video_ids):
    if not video_ids:
        return {}
    rows = db.session.execute(
        select(Like.video_id, func.count(Like.user_id))
        .where(Like.video_id.in_(video_ids))
        .group_by(Like.video_id)
    ).all()
    return dict(rows)


@videos_bp.post('/videos')
@login_required
def create_video(user):
    data, error = json_body('title', 'file_path', 'game')
    if error:
        return error
    if not games.is_valid(data['game']):
        return {'error': f"Unknown game: {data['game']}"}, 400
    # Built field by field on purpose — Video(**data) let a client set any
    # column, including id and user_id.
    video = Video(
        title=data['title'],
        file_path=_youtube_id(data['file_path']),
        game=data['game'],
        user_id=user.id,
    )
    db.session.add(video)
    db.session.commit()
    return video.to_dict(like_count=0), 201


@videos_bp.delete('/videos/<int:video_id>')
@login_required
def delete_video(video_id, user):
    video = db.session.get(Video, video_id)
    if not video:
        return {'error': 'Video not found'}, 404
    if video.user_id != user.id:
        return {'error': 'You are not authorized to delete this video'}, 403
    db.session.delete(video)
    db.session.commit()
    return {}, 204


def _youtube_id(value):
    """Accept a full YouTube URL or a bare id and always store the bare id."""
    value = (value or '').strip()
    for marker in ('watch?v=', 'youtu.be/', '/embed/', '/shorts/'):
        if marker in value:
            value = value.split(marker, 1)[1]
            break
    return value.split('&', 1)[0].split('?', 1)[0].split('/', 1)[0]
