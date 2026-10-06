"""Merge recruiters into users, add video.game, drop the bridge table

Players and recruiters lived in separate tables, so ``messages.sender_id`` and
``messages.recipient_id`` — both pointing at ``users_table`` — could never hold
a recruiter. A scout messaging a player was not expressible. This merges the
two into one table keyed by ``role``.

``users_recruiters_table`` only existed to bridge the two tables and held no
rows; it goes, along with the ``messages.interaction_id`` column that
referenced it. A proper follow/connection table replaces it later.

Revision ID: b3f1c7d92a04
Revises: 9ce1843a2054
"""
import sqlalchemy as sa
from alembic import op

revision = 'b3f1c7d92a04'
down_revision = '9ce1843a2054'
branch_labels = None
depends_on = None

# The seeded demo clips, so existing rows get a truthful game rather than all
# being lumped under one. Anything unrecognised falls back to valorant.
SEED_CLIP_GAMES = {
    'gzvpAFBlPHs': 'valorant', 'cZ60-T8WFAw': 'valorant', 'O0XlJcqZKNY': 'valorant',
    'HTdWFnpcbzk': 'valorant', 'Pt5i1u6FPDQ': 'valorant',
    'cPdbef-JMws': 'cs2', '9eOUDbbePII': 'rocket-league', 'IiJGScfYkYU': 'apex-legends',
}


def upgrade():
    conn = op.get_bind()

    # 1. users_table grows the role/organization columns, and the name columns
    #    become optional because recruiters have an organization instead.
    with op.batch_alter_table('users_table', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('role', sa.String(length=20), nullable=False, server_default='player'),
        )
        batch_op.add_column(sa.Column('organization', sa.String(), nullable=True))
        batch_op.alter_column('first_name', existing_type=sa.String(), nullable=True)
        batch_op.alter_column('last_name', existing_type=sa.String(), nullable=True)
        batch_op.create_index(batch_op.f('ix_users_table_role'), ['role'], unique=False)

    # 2. Move every recruiter across, renaming on the rare username collision
    #    rather than failing the migration.
    taken = {row[0] for row in conn.execute(sa.text('SELECT username FROM users_table'))}
    recruiters = conn.execute(sa.text(
        'SELECT recruiter_username, recruiter_name, _hashed_password FROM recruiters_table'
    )).fetchall()

    for username, organization, password_hash in recruiters:
        candidate, n = username, 2
        while candidate in taken:
            candidate, n = f'{username}-{n}', n + 1
        taken.add(candidate)
        conn.execute(
            sa.text(
                'INSERT INTO users_table (username, role, organization, _hashed_password) '
                'VALUES (:u, :r, :o, :p)'
            ),
            {'u': candidate, 'r': 'recruiter', 'o': organization, 'p': password_hash},
        )

    # 3. The bridge table and the column pointing at it both go. Order matters:
    #    the referencing column must be dropped first.
    with op.batch_alter_table('messages_table', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_messages_table_interaction_id'))
        batch_op.drop_column('interaction_id')

    op.drop_table('users_recruiters_table')
    op.drop_table('recruiters_table')

    # 4. videos.game — added nullable, backfilled, then locked down, because
    #    existing rows have no value to satisfy a NOT NULL constraint.
    with op.batch_alter_table('videos_table', schema=None) as batch_op:
        batch_op.add_column(sa.Column('game', sa.String(length=40), nullable=True))

    conn.execute(sa.text("UPDATE videos_table SET game = 'valorant'"))
    for clip_id, game in SEED_CLIP_GAMES.items():
        conn.execute(
            sa.text('UPDATE videos_table SET game = :g WHERE file_path = :f'),
            {'g': game, 'f': clip_id},
        )

    with op.batch_alter_table('videos_table', schema=None) as batch_op:
        batch_op.alter_column('game', existing_type=sa.String(length=40), nullable=False)
        batch_op.create_index(batch_op.f('ix_videos_table_game'), ['game'], unique=False)


def downgrade():
    conn = op.get_bind()

    op.create_table(
        'recruiters_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recruiter_name', sa.String(), nullable=False),
        sa.Column('recruiter_username', sa.String(), nullable=False),
        sa.Column('_hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_recruiters_table')),
    )
    with op.batch_alter_table('recruiters_table', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_recruiters_table_recruiter_username'),
            ['recruiter_username'], unique=True,
        )

    conn.execute(sa.text(
        'INSERT INTO recruiters_table (recruiter_username, recruiter_name, _hashed_password) '
        "SELECT username, COALESCE(organization, username), _hashed_password "
        "FROM users_table WHERE role = 'recruiter'"
    ))
    conn.execute(sa.text("DELETE FROM users_table WHERE role = 'recruiter'"))

    op.create_table(
        'users_recruiters_table',
        sa.Column('interaction_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('recruiter_id', sa.Integer(), nullable=False),
        sa.Column('interaction_type', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ['recruiter_id'], ['recruiters_table.id'],
            name=op.f('fk_users_recruiters_table_recruiter_id_recruiters_table'),
        ),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users_table.id'],
            name=op.f('fk_users_recruiters_table_user_id_users_table'),
        ),
        sa.PrimaryKeyConstraint('interaction_id', name=op.f('pk_users_recruiters_table')),
    )
    with op.batch_alter_table('users_recruiters_table', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_users_recruiters_table_recruiter_id'), ['recruiter_id'], unique=False)
        batch_op.create_index(
            batch_op.f('ix_users_recruiters_table_user_id'), ['user_id'], unique=False)

    with op.batch_alter_table('messages_table', schema=None) as batch_op:
        batch_op.add_column(sa.Column('interaction_id', sa.Integer(), nullable=True))
        batch_op.create_index(
            batch_op.f('ix_messages_table_interaction_id'), ['interaction_id'], unique=False)

    with op.batch_alter_table('videos_table', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_videos_table_game'))
        batch_op.drop_column('game')

    with op.batch_alter_table('users_table', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_table_role'))
        batch_op.drop_column('organization')
        batch_op.drop_column('role')
        batch_op.alter_column('last_name', existing_type=sa.String(), nullable=False)
        batch_op.alter_column('first_name', existing_type=sa.String(), nullable=False)
