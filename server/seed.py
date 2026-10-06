#!/usr/bin/env python3
"""Reset the database and fill it with demo data.

    python seed.py
"""
import random

from app import app
from extensions import db
from faker import Faker
from models import PLAYER, RECRUITER, Like, Message, User, Video

faker = Faker()

# Real gameplay clips, keyed by the game slugs in games.py. Each id was checked
# against YouTube's oEmbed endpoint, so they exist and allow embedding.
CLIPS_BY_GAME = {
    'valorant': [
        ('gzvpAFBlPHs', 'Valorant 1v5 Sheriff God Ace'),
        ('cZ60-T8WFAw', 'Vandal ace on Ascent'),
        ('O0XlJcqZKNY', 'Clean ace, full buy round'),
        ('HTdWFnpcbzk', 'Fastest gun ace - 1.2s, all headshots'),
        ('Pt5i1u6FPDQ', 'Kuronami Vandal ace'),
    ],
    'cs2': [
        ('cPdbef-JMws', 'CS2 montage - spray control'),
    ],
    'rocket-league': [
        ('9eOUDbbePII', 'Aerial goal compilation'),
    ],
    'apex-legends': [
        ('IiJGScfYkYU', 'Final ring clutch, 1v3'),
    ],
}

CLIPS = [
    (clip_id, title, game)
    for game, clips in CLIPS_BY_GAME.items()
    for clip_id, title in clips
]

DEMO_PASSWORD = 'password'


def seed():
    print('Resetting database...')
    db.drop_all()
    db.create_all()

    players = []
    for _ in range(8):
        player = User(
            username=faker.unique.user_name(),
            role=PLAYER,
            first_name=faker.first_name(),
            last_name=faker.last_name(),
        )
        player.password = DEMO_PASSWORD
        players.append(player)

    recruiters = []
    for _ in range(3):
        recruiter = User(
            username=faker.unique.user_name(),
            role=RECRUITER,
            organization=faker.company(),
        )
        recruiter.password = DEMO_PASSWORD
        recruiters.append(recruiter)

    db.session.add_all(players + recruiters)
    db.session.commit()

    videos = [
        Video(
            title=title,
            file_path=clip_id,
            game=game,
            user_id=random.choice(players).id,
        )
        # Every clip once, so no title is attached to the wrong thumbnail.
        for clip_id, title, game in CLIPS
    ]
    db.session.add_all(videos)
    db.session.commit()

    likes = {
        (random.choice(players).id, random.choice(videos).id)
        for _ in range(40)
    }
    db.session.add_all(Like(user_id=u, video_id=v) for u, v in likes)

    # Player-to-player chatter, plus recruiters reaching out — the second kind
    # was impossible before players and recruiters shared a table.
    for _ in range(20):
        sender, recipient = random.sample(players, 2)
        db.session.add(Message(
            content=faker.sentence(),
            sender_id=sender.id,
            recipient_id=recipient.id,
        ))
    for recruiter in recruiters:
        for player in random.sample(players, 3):
            db.session.add(Message(
                content=f'Hi {player.first_name}, {recruiter.organization} here — '
                        'saw your clips and would like to talk.',
                sender_id=recruiter.id,
                recipient_id=player.id,
            ))
    db.session.commit()

    print(f'Seeded {len(players)} players, {len(recruiters)} recruiters, '
          f'{len(videos)} clips across {len(CLIPS_BY_GAME)} games.')
    print(f'Password for every account: {DEMO_PASSWORD!r}')
    print(f'Player login:    {players[0].username}')
    print(f'Recruiter login: {recruiters[0].username}')


if __name__ == '__main__':
    with app.app_context():
        seed()
