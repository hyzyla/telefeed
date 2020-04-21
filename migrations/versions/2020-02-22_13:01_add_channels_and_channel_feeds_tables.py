"""Add channels and channel_feeds tables

Revision ID: e5d6f3960743
Revises: c378a70a5dd1
Create Date: 2020-02-22 13:01:32.041977

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e5d6f3960743'
down_revision = 'c378a70a5dd1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'channels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('date_cursor', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'channel_feeds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('feed_id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.Column('date_cursor', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(('channel_id',), ['channels.id'], ),
        sa.ForeignKeyConstraint(('feed_id',), ['feeds.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('channel_feeds')
    op.drop_table('channels')
