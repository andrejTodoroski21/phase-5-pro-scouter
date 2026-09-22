# Pro Scouter

A video-sharing platform for competitive players. Players upload clips of their
matches; scouts browse the feed and message players directly.

- **Backend** — Flask + SQLAlchemy + Flask-Migrate, SQLite locally
- **Frontend** — React 18 + React Router 6, built with Vite

## Requirements

- **Node 18 or newer.** Vite 5 will not build on Node 16 — it fails with
  `crypto.getRandomValues is not a function`. A `.nvmrc` is checked in, so
  `nvm use` in the project root picks the right version.
- Python 3.9+

## Setup

```bash
nvm use
pipenv install && pipenv shell
npm install --prefix client
```

Create a `.env` in the project root:

```
SECRET_KEY=<any long random string>
# Optional. Without it the app uses local SQLite, which is what you want
# for development — pointing at a remote database makes every query a
# network round trip.
# DATABASE_URL=postgresql://...
```

## Running

Two terminals:

```bash
cd server && python app.py          # API on :5555
```

```bash
npm run dev --prefix client         # UI on :5173, proxies /api to :5555
```

## Database

```bash
cd server
flask db upgrade          # apply migrations
python seed.py            # reset and fill with demo data
```

`seed.py` prints a username to log in with. Every seeded account uses the
password `password`.

## Layout

```
server/
  app.py              application factory; also serves the built client
  extensions.py       shared db / bcrypt / migrate / socketio instances
  models.py           SQLAlchemy models with hand-written to_dict()
  routes/
    auth.py           signup, login, logout, session, for users and recruiters
    videos.py         video feed (paginated), upload, delete
    messages.py       conversation list and direct messages
    events.py         Socket.IO handlers
  seed.py

client/src/
  lib/api.js          fetch wrapper; sends the session cookie, throws on errors
  context/            auth provider and the useAuth hook
  components/
    LiteYouTube.jsx   thumbnail that becomes an iframe only when clicked
```

## API

| Method | Path | Notes |
| --- | --- | --- |
| POST | `/api/signup` | `{username, first_name, last_name, password}` |
| POST | `/api/login` | `{username, password}` |
| DELETE | `/api/logout` | |
| GET | `/api/get-session-user` | `204` when signed out |
| POST | `/api/recruiters` | recruiter signup |
| POST | `/api/recruiters-login` | |
| DELETE | `/api/recruiters-logout` | |
| GET | `/api/get-session-recruiter` | |
| GET | `/api/videos` | `?page=&per_page=&user_id=` |
| POST | `/api/videos` | `{title, file_path}`; owner comes from the session |
| DELETE | `/api/videos/<id>` | owner only |
| GET | `/api/conversations` | |
| GET | `/api/messages/<user_id>` | |
| POST | `/api/messages` | `{recipient_id, content}` |

`file_path` accepts a full YouTube URL or a bare video id; the server stores the id.

## Deploying

```bash
npm run build --prefix client
cd server && gunicorn app:app
```

The Flask app serves `client/dist` and sends far-future cache headers for
Vite's fingerprinted assets.
