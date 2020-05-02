"""Add feed.date_cursor column

Revision ID: c378a70a5dd1
Revises: d2a98f6fa6e6
Create Date: 2020-02-16 12:50:52.969182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c378a70a5dd1'
down_revision = 'd2a98f6fa6e6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('feeds', sa.Column('date_cursor', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('feeds', 'date_cursor')
