"""Video listing, upload and deletion."""
import hashlib
import uuid

import games
import mp4
import storage
from extensions import db
from flask import Blueprint, current_app, request
from models import UPLOAD, YOUTUBE, Like, Video
from routes.helpers import json_body, login_required, player_required
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
@player_required
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
        source=YOUTUBE,
        user_id=user.id,
    )
    db.session.add(video)
    db.session.commit()
    return video.to_dict(like_count=0), 201


@videos_bp.post('/videos/upload')
@player_required
def upload_video(user):
    """Accept a clip file and create the video row in one request.

    Validation order matters: cheap checks first, so a 200 MB file is rejected
    on its size before anything parses or uploads it.
    """
    uploaded = request.files.get('file')
    if uploaded is None or not uploaded.filename:
        return {'error': 'Missing required fields: file'}, 400

    title = (request.form.get('title') or '').strip()
    game = (request.form.get('game') or '').strip()
    if not title or not game:
        missing = [n for n, v in (('title', title), ('game', game)) if not v]
        return {'error': f"Missing required fields: {', '.join(missing)}"}, 400
    if not games.is_valid(game):
        return {'error': f'Unknown game: {game}'}, 400

    stream = uploaded.stream
    size = _stream_size(stream)
    max_bytes = current_app.config['MAX_CLIP_BYTES']
    if size == 0:
        return {'error': 'That file is empty'}, 400
    if size > max_bytes:
        return {
            'error': f'Clip is {size // (1024 * 1024)} MB; the limit is '
                     f'{max_bytes // (1024 * 1024)} MB'
        }, 413

    try:
        info = mp4.inspect(stream)
    except mp4.NotAnMp4 as exc:
        return {'error': f'Only MP4 video is accepted ({exc})'}, 415

    max_seconds = current_app.config['MAX_CLIP_SECONDS']
    duration = info['duration']
    if duration is not None and duration > max_seconds:
        return {
            'error': f'Clip is {duration:.0f}s; the limit is {max_seconds}s'
        }, 400

    digest = _sha256(stream)
    existing = Video.query.filter_by(content_hash=digest, user_id=user.id).first()
    if existing:
        return {'error': 'You have already uploaded this clip'}, 409

    key = f'clips/{digest[:12]}-{uuid.uuid4().hex[:8]}.mp4'
    stream.seek(0)
    storage.get().save(key, stream, content_type='video/mp4')

    video = Video(
        title=title,
        game=game,
        source=UPLOAD,
        storage_key=key,
        duration_seconds=duration,
        size_bytes=size,
        content_hash=digest,
        user_id=user.id,
    )
    db.session.add(video)
    db.session.commit()
    return video.to_dict(like_count=0), 201


def _stream_size(stream):
    stream.seek(0, 2)
    size = stream.tell()
    stream.seek(0)
    return size


def _sha256(stream):
    stream.seek(0)
    digest = hashlib.sha256()
    while chunk := stream.read(1024 * 256):
        digest.update(chunk)
    stream.seek(0)
    return digest.hexdigest()


@videos_bp.delete('/videos/<int:video_id>')
@login_required
def delete_video(video_id, user):
    video = db.session.get(Video, video_id)
    if not video:
        return {'error': 'Video not found'}, 404
    if video.user_id != user.id:
        return {'error': 'You are not authorized to delete this video'}, 403
    # Drop the stored object first; a row pointing at a missing file is better
    # than an orphaned file nothing references.
    if video.is_upload and video.storage_key:
        storage.get().delete(video.storage_key)
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
