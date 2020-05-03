"""Add channels posting settings

Revision ID: 3b6f84b39b76
Revises: 76b530cf2213
Create Date: 2020-05-03 10:18:26.640111

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b6f84b39b76'
down_revision = '76b530cf2213'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'channels',
        sa.Column('separate_links', sa.Boolean(), server_default='0', nullable=False),
    )
    op.add_column(
        'channels',
        sa.Column('show_preview', sa.Boolean(), server_default='0', nullable=False),
    )


def downgrade():
    op.drop_column('channels', 'show_preview')
    op.drop_column('channels', 'separate_links')
