"""Add channel.template column

Revision ID: 172a7254c12b
Revises: 052c03de63d0
Create Date: 2020-05-09 12:36:25.400317

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '172a7254c12b'
down_revision = '052c03de63d0'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'channels',
        sa.Column('template', sa.Text(), server_default='', nullable=False),
    )


def downgrade():
    op.drop_column('channels', 'template')
