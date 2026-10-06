"""Minimal end-to-end check: boot the app against a temp database and walk the
main flows. Run with ``python -m smoke`` from the server directory."""
import io
import struct
import sys
import tempfile
from pathlib import Path

from app import create_app
from extensions import db


def _mp4(seconds=10.0, timescale=600):
    """A minimal but structurally valid MP4: ftyp + moov>mvhd."""
    def box(typ, payload):
        return struct.pack('>I4s', len(payload) + 8, typ) + payload
    mvhd = (bytes([0, 0, 0, 0]) + struct.pack('>II', 0, 0)
            + struct.pack('>I', timescale)
            + struct.pack('>I', int(seconds * timescale))
            + b'\x00' * 80)
    return box(b'ftyp', b'isom' + struct.pack('>I', 512) + b'isomavc1') + box(b'moov', box(b'mvhd', mvhd))


def main():
    tmp = Path(tempfile.mkdtemp()) / 'smoke.db'
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{tmp}',
        'TESTING': True,
        'SECRET_KEY': 'smoke-test-secret-key-at-least-32-bytes-long',
        'MEDIA_ROOT': str(Path(tempfile.mkdtemp()) / 'media'),
    })
    with app.app_context():
        db.create_all()

    client = app.test_client()
    checks = []

    def check(label, response, expected):
        ok = response.status_code == expected
        checks.append(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {label} -> {response.status_code} (want {expected})")
        return response

    def assert_that(label, condition):
        checks.append(bool(condition))
        print(f"{'ok  ' if condition else 'FAIL'} {label}")

    # --- anonymous ---------------------------------------------------------
    check('anonymous session', client.get('/api/me'), 204)
    check('empty feed', client.get('/api/videos'), 200)
    check('game list', client.get('/api/games'), 200)
    check('link a clip while signed out', client.post('/api/videos', json={
        'title': 'x', 'file_path': 'y', 'game': 'valorant'}), 401)

    # --- player signup -----------------------------------------------------
    player = check('player signup', client.post('/api/signup', json={
        'username': 'smokeplayer', 'first_name': 'S', 'last_name': 'T',
        'password': 'pw'}), 201)
    token = player.get_json().get('token')
    assert_that('signup returns a token', bool(token))
    assert_that('signup role is player', player.get_json()['role'] == 'player')

    check('duplicate username', client.post('/api/signup', json={
        'username': 'smokeplayer', 'first_name': 'S', 'last_name': 'T',
        'password': 'pw'}), 409)
    check('player missing last_name', client.post('/api/signup', json={
        'username': 'nope', 'first_name': 'S', 'password': 'pw'}), 400)
    check('bad role rejected', client.post('/api/signup', json={
        'username': 'nope2', 'password': 'pw', 'role': 'admin'}), 400)
    check('session after signup', client.get('/api/me'), 200)

    # --- videos ------------------------------------------------------------
    video = check('create video', client.post('/api/videos', json={
        'title': 'clip', 'file_path': 'https://youtu.be/dQw4w9WgXcQ',
        'game': 'valorant'}), 201)
    assert_that('URL reduced to an id', video.get_json()['file_path'] == 'dQw4w9WgXcQ')
    assert_that('game name resolved', video.get_json()['game_name'] == 'Valorant')

    check('video needs a game', client.post('/api/videos', json={
        'title': 'clip', 'file_path': 'abc'}), 400)
    check('unknown game rejected', client.post('/api/videos', json={
        'title': 'clip', 'file_path': 'abc', 'game': 'minesweeper'}), 400)
    check('filter by game', client.get('/api/videos?game=valorant'), 200)
    check('filter by unknown game', client.get('/api/videos?game=minesweeper'), 400)
    assert_that(
        'game counts update',
        next(g['clip_count'] for g in client.get('/api/games').get_json()
             if g['slug'] == 'valorant') == 1,
    )

    # --- recruiter ---------------------------------------------------------
    client.delete('/api/logout')
    recruiter = check('recruiter signup', client.post('/api/signup', json={
        'username': 'smokescout', 'password': 'pw', 'role': 'recruiter',
        'organization': 'Acme Esports'}), 201)
    assert_that('recruiter role set', recruiter.get_json()['role'] == 'recruiter')
    assert_that(
        'recruiter display name is the org',
        recruiter.get_json()['display_name'] == 'Acme Esports',
    )
    check('recruiter missing organization', client.post('/api/signup', json={
        'username': 'nope3', 'password': 'pw', 'role': 'recruiter'}), 400)

    # The whole point of the merge: a recruiter can message a player.
    check('recruiter messages a player', client.post('/api/messages', json={
        'content': 'saw your clips', 'recipient_id': 1}), 201)
    check('recruiter conversations', client.get('/api/conversations'), 200)

    # Players showcase, recruiters scout. The navbar hides the upload link from
    # recruiters, so the endpoint must agree.
    check('recruiter cannot link a clip', client.post('/api/videos', json={
        'title': 'nope', 'file_path': 'abc12345678', 'game': 'cs2'}), 403)
    check('recruiter cannot upload a clip', client.post(
        '/api/videos/upload',
        data={'title': 'nope', 'game': 'cs2',
              'file': (io.BytesIO(_mp4()), 'c.mp4')},
        content_type='multipart/form-data'), 403)

    # A second player owns this one, so the first player must not be able to
    # delete it. It cannot belong to the recruiter any more: recruiters are now
    # refused clip creation outright.
    client.delete('/api/logout')
    client.post('/api/signup', json={
        'username': 'smokeplayer2', 'first_name': 'Other', 'last_name': 'Player',
        'password': 'pw'})
    created = check('second player posts a clip', client.post('/api/videos', json={
        'title': 'another player clip', 'file_path': 'zzz11111111',
        'game': 'cs2'}), 201)
    others_video = created.get_json()['id']

    # --- token auth --------------------------------------------------------
    client.delete('/api/logout')
    check('logged out', client.get('/api/me'), 204)
    check('bearer token authenticates', client.get(
        '/api/me', headers={'Authorization': f'Bearer {token}'}), 200)
    check('garbage token rejected', client.get(
        '/api/me', headers={'Authorization': 'Bearer not-a-token'}), 204)
    check('token authorises an upload', client.post(
        '/api/videos', headers={'Authorization': f'Bearer {token}'},
        json={'title': 'via token', 'file_path': 'abc12345678', 'game': 'cs2'}), 201)

    # --- ownership ---------------------------------------------------------
    check("delete another user's video", client.delete(
        f'/api/videos/{others_video}',
        headers={'Authorization': f'Bearer {token}'}), 403)
    check('delete own video', client.delete(
        '/api/videos/1', headers={'Authorization': f'Bearer {token}'}), 204)
    check('delete a missing video', client.delete(
        '/api/videos/9999', headers={'Authorization': f'Bearer {token}'}), 404)
    check('login', client.post('/api/login', json={
        'username': 'smokeplayer', 'password': 'pw'}), 200)
    check('wrong password', client.post('/api/login', json={
        'username': 'smokeplayer', 'password': 'nope'}), 401)
    check('users filtered by role', client.get('/api/users?role=recruiter'), 200)
    check('bad role filter', client.get('/api/users?role=admin'), 400)

    # --- uploads -----------------------------------------------------------
    import storage as storage_module
    with app.app_context():
        assert_that(
            'local storage without R2 settings',
            type(storage_module.get()).__name__ == 'LocalStorage',
        )

    up = check('upload an mp4', client.post(
        '/api/videos/upload',
        headers={'Authorization': f'Bearer {token}'},
        data={'title': 'uploaded clip', 'game': 'valorant',
              'file': (io.BytesIO(_mp4(10.0)), 'clip.mp4')},
        content_type='multipart/form-data'), 201)
    body = up.get_json()
    assert_that('source is upload', body['source'] == 'upload')
    assert_that('duration read from the file', abs(body['duration_seconds'] - 10.0) < 0.01)
    assert_that('playable url returned', bool(body['video_url']))
    assert_that('no youtube id on an upload', body['file_path'] is None)

    check('the stored file is served', client.get(body['video_url']), 200)

    check('re-uploading the same clip', client.post(
        '/api/videos/upload',
        headers={'Authorization': f'Bearer {token}'},
        data={'title': 'dupe', 'game': 'valorant',
              'file': (io.BytesIO(_mp4(10.0)), 'clip.mp4')},
        content_type='multipart/form-data'), 409)

    check('a clip over the length cap', client.post(
        '/api/videos/upload',
        headers={'Authorization': f'Bearer {token}'},
        data={'title': 'too long', 'game': 'valorant',
              'file': (io.BytesIO(_mp4(90.0)), 'long.mp4')},
        content_type='multipart/form-data'), 400)

    check('a file that is not an mp4', client.post(
        '/api/videos/upload',
        headers={'Authorization': f'Bearer {token}'},
        data={'title': 'nope', 'game': 'valorant',
              'file': (io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'0' * 64), 'x.png')},
        content_type='multipart/form-data'), 415)

    check('an empty file', client.post(
        '/api/videos/upload',
        headers={'Authorization': f'Bearer {token}'},
        data={'title': 'empty', 'game': 'valorant',
              'file': (io.BytesIO(b''), 'empty.mp4')},
        content_type='multipart/form-data'), 400)

    check('upload without a game', client.post(
        '/api/videos/upload',
        headers={'Authorization': f'Bearer {token}'},
        data={'title': 'no game', 'file': (io.BytesIO(_mp4()), 'c.mp4')},
        content_type='multipart/form-data'), 400)

    # Drop the session cookie; the checks above authenticate with the token
    # header, so this one really is anonymous.
    client.delete('/api/logout')
    check('upload a file while signed out', client.post(
        '/api/videos/upload',
        data={'title': 'anon', 'game': 'valorant',
              'file': (io.BytesIO(_mp4()), 'c.mp4')},
        content_type='multipart/form-data'), 401)

    # Deleting an upload should take the stored object with it.
    stored_url = body['video_url']
    check('delete the uploaded clip', client.delete(
        f"/api/videos/{body['id']}",
        headers={'Authorization': f'Bearer {token}'}), 204)
    check('its file is gone', client.get(stored_url), 404)

    print()
    if not all(checks):
        print(f'{checks.count(False)} of {len(checks)} checks FAILED')
        sys.exit(1)
    print(f'{len(checks)} checks passed')


if __name__ == '__main__':
    main()
