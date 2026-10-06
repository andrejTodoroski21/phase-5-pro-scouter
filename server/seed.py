#!/usr/bin/env python3
"""Reset the database and fill it with demo data.

    python seed.py
"""
import random

from faker import Faker

from app import app
from extensions import db
from models import Like, Message, Recruiter, User, Video

faker = Faker()

# Real gameplay clips, grouped by game. Each id was checked against YouTube's
# oEmbed endpoint, so they exist and allow embedding.
#
# Grouped this way because Video has no `game` column yet. When that column
# lands, this dict is already the taxonomy and the seed can write it straight in.
CLIPS_BY_GAME = {
    'Valorant': [
        ('gzvpAFBlPHs', 'Valorant 1v5 Sheriff God Ace'),
        ('cZ60-T8WFAw', 'Vandal ace on Ascent'),
        ('O0XlJcqZKNY', 'Clean ace, full buy round'),
        ('HTdWFnpcbzk', 'Fastest gun ace - 1.2s, all headshots'),
        ('Pt5i1u6FPDQ', 'Kuronami Vandal ace'),
    ],
    'Counter-Strike 2': [
        ('cPdbef-JMws', 'CS2 montage - spray control'),
    ],
    'Rocket League': [
        ('9eOUDbbePII', 'Aerial goal compilation'),
    ],
    'Apex Legends': [
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

    users = []
    for _ in range(8):
        user = User(
            username=faker.unique.user_name(),
            first_name=faker.first_name(),
            last_name=faker.last_name(),
        )
        user.password = DEMO_PASSWORD
        users.append(user)
    db.session.add_all(users)

    recruiters = []
    for _ in range(3):
        recruiter = Recruiter(
            recruiter_username=faker.unique.user_name(),
            recruiter_name=faker.company(),
        )
        recruiter.password = DEMO_PASSWORD
        recruiters.append(recruiter)
    db.session.add_all(recruiters)
    db.session.commit()

    videos = [
        Video(
            title=title,
            file_path=clip_id,
            user_id=random.choice(users).id,
        )
        # Every clip once, so no title is attached to the wrong thumbnail.
        for clip_id, title, _game in CLIPS
    ]
    db.session.add_all(videos)
    db.session.commit()

    likes = {
        (random.choice(users).id, random.choice(videos).id)
        for _ in range(60)
    }
    db.session.add_all(Like(user_id=u, video_id=v) for u, v in likes)

    for _ in range(40):
        sender, recipient = random.sample(users, 2)
        db.session.add(Message(
            content=faker.sentence(),
            sender_id=sender.id,
            recipient_id=recipient.id,
        ))
    db.session.commit()

    print(f'Seeded {len(users)} users, {len(recruiters)} recruiters, '
          f'{len(videos)} clips across {len(CLIPS_BY_GAME)} games '
          f'({", ".join(CLIPS_BY_GAME)}).')
    print(f'Password for every account: {DEMO_PASSWORD!r}')
    print(f'Try logging in as: {users[0].username}')


if __name__ == '__main__':
    with app.app_context():
        seed()
