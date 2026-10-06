"""Add uploaded-clip columns to videos

A clip is now either a YouTube embed (``source='youtube'``, id in
``file_path``) or an uploaded file (``source='upload'``, object key in
``storage_key``). ``file_path`` therefore becomes nullable, and existing rows
are all marked as YouTube.

Revision ID: c81d4e2f5a37
Revises: b3f1c7d92a04
"""
import sqlalchemy as sa
from alembic import op

revision = 'c81d4e2f5a37'
down_revision = 'b3f1c7d92a04'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    with op.batch_alter_table('videos_table', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('source', sa.String(length=20), nullable=False, server_default='youtube'),
        )
        batch_op.add_column(sa.Column('storage_key', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('duration_seconds', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('size_bytes', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('content_hash', sa.String(length=64), nullable=True))
        batch_op.create_index(
            batch_op.f('ix_videos_table_content_hash'), ['content_hash'], unique=False,
        )

    # Every row that exists predates uploads, so it is a YouTube embed.
    conn.execute(sa.text("UPDATE videos_table SET source = 'youtube' WHERE source IS NULL"))

    with op.batch_alter_table('videos_table', schema=None) as batch_op:
        batch_op.alter_column('file_path', existing_type=sa.String(), nullable=True)


def downgrade():
    conn = op.get_bind()
    # Uploaded clips have no YouTube id to fall back on, so they cannot survive
    # a column that is about to become NOT NULL.
    conn.execute(sa.text("DELETE FROM videos_table WHERE source = 'upload'"))

    with op.batch_alter_table('videos_table', schema=None) as batch_op:
        batch_op.alter_column('file_path', existing_type=sa.String(), nullable=False)
        batch_op.drop_index(batch_op.f('ix_videos_table_content_hash'))
        batch_op.drop_column('content_hash')
        batch_op.drop_column('size_bytes')
        batch_op.drop_column('duration_seconds')
        batch_op.drop_column('storage_key')
        batch_op.drop_column('source')
