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

# Real, embeddable clip ids so the video pages have something to show.
CLIP_IDS = [
    'e-ORhEE9VVg', 'ZyhrYis509A', 'tgbNymZ7vqY', 'VbfpW0pbvaU',
    '3JZ_D3ELwOQ', 'lTTajzrSkCw', 'kJQP7kiw5Fk', '9bZkp7q19f0',
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
            title=faker.sentence(nb_words=4).rstrip('.'),
            file_path=random.choice(CLIP_IDS),
            user_id=random.choice(users).id,
        )
        for _ in range(20)
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
          f'{len(videos)} videos. Password for every account: {DEMO_PASSWORD!r}')
    print(f'Try logging in as: {users[0].username}')


if __name__ == '__main__':
    with app.app_context():
        seed()
