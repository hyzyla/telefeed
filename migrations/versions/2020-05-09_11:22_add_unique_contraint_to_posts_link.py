"""Add unique contraint to posts.link

Revision ID: 052c03de63d0
Revises: 3b6f84b39b76
Create Date: 2020-05-09 11:22:31.454815

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '052c03de63d0'
down_revision = '3b6f84b39b76'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(None, 'posts', ['link'])


def downgrade():
    op.drop_constraint(None, 'posts', type_='unique')
