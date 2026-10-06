"""Minimal end-to-end check: boot the app against a temp database and walk the
main flows. Run with ``python -m smoke`` from the server directory."""
import sys
import tempfile
from pathlib import Path

from app import create_app
from extensions import db


def main():
    tmp = Path(tempfile.mkdtemp()) / 'smoke.db'
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{tmp}',
        'TESTING': True,
        'SECRET_KEY': 'smoke-test-secret-key-at-least-32-bytes-long',
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
    check('upload while signed out', client.post('/api/videos', json={
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

    # Owned by the recruiter, so the player must not be able to delete it.
    others_video = client.post('/api/videos', json={
        'title': 'recruiter clip', 'file_path': 'zzz11111111',
        'game': 'cs2'}).get_json()['id']

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

    print()
    if not all(checks):
        print(f'{checks.count(False)} of {len(checks)} checks FAILED')
        sys.exit(1)
    print(f'{len(checks)} checks passed')


if __name__ == '__main__':
    main()
