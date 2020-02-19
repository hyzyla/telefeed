"""Initial migration.

Revision ID: 1b7bd3b61539
Revises: 
Create Date: 2020-02-09 16:42:43.069232

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1b7bd3b61539'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'feeds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('link', sa.Text(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('feed_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(('feed_id',), ['feeds.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('posts')
    op.drop_table('feeds')
