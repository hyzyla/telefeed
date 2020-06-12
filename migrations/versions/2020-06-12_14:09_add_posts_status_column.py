"""Add posts.status column

Revision ID: c3f4523bf3cd
Revises: 172a7254c12b
Create Date: 2020-06-12 14:09:29.493918

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c3f4523bf3cd'
down_revision = '172a7254c12b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'posts',
        sa.Column(
            'status',
            sa.Enum('new', 'sent', name='poststatus', native_enum=False),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column('posts', 'status')
