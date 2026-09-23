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
        'SECRET_KEY': 'smoke',
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

    check('anonymous session', client.get('/api/get-session-user'), 204)
    check('empty feed', client.get('/api/videos'), 200)
    check('signup', client.post('/api/signup', json={
        'username': 'smoke', 'first_name': 'S', 'last_name': 'T', 'password': 'pw'}), 201)
    check('duplicate signup', client.post('/api/signup', json={
        'username': 'smoke', 'first_name': 'S', 'last_name': 'T', 'password': 'pw'}), 409)
    check('session after signup', client.get('/api/get-session-user'), 200)

    video = check('create video', client.post('/api/videos', json={
        'title': 'clip', 'file_path': 'https://youtu.be/dQw4w9WgXcQ'}), 201)
    assert video.get_json()['file_path'] == 'dQw4w9WgXcQ', 'URL was not reduced to an id'

    check('own feed', client.get('/api/videos?user_id=1'), 200)
    check('delete own video', client.delete(f"/api/videos/{video.get_json()['id']}"), 204)
    check('conversations', client.get('/api/conversations'), 200)
    check('logout', client.delete('/api/logout'), 204)
    check('upload while signed out', client.post('/api/videos', json={
        'title': 'x', 'file_path': 'y'}), 401)

    if not all(checks):
        sys.exit(1)
    print(f'\n{len(checks)} checks passed')


if __name__ == '__main__':
    main()
