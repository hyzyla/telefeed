"""Add ONDELETE rules

Revision ID: 76b530cf2213
Revises: e5d6f3960743
Create Date: 2020-04-21 15:06:29.366863

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '76b530cf2213'
down_revision = 'e5d6f3960743'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        'channel_feeds_feed_id_fkey',
        'channel_feeds',
        type_='foreignkey',
    )
    op.drop_constraint(
        'channel_feeds_channel_id_fkey',
        'channel_feeds',
        type_='foreignkey',
    )
    op.create_foreign_key(
        None,
        'channel_feeds',
        'channels',
        ['channel_id'],
        ['id'],
        ondelete='CASCADE',
    )
    op.create_foreign_key(
        None,
        'channel_feeds',
        'feeds',
        ['feed_id'],
        ['id'],
        ondelete='CASCADE',
    )
    op.drop_constraint('posts_feed_id_fkey', 'posts', type_='foreignkey')
    op.create_foreign_key(
        None,
        'posts',
        'feeds',
        ['feed_id'],
        ['id'],
        ondelete='CASCADE',
    )


def downgrade():
    op.drop_constraint(None, 'posts', type_='foreignkey')
    op.create_foreign_key(
        'posts_feed_id_fkey',
        'posts',
        'feeds',
        ['feed_id'],
        ['id'],
    )
    op.drop_constraint(None, 'channel_feeds', type_='foreignkey')
    op.drop_constraint(None, 'channel_feeds', type_='foreignkey')
    op.create_foreign_key(
        'channel_feeds_channel_id_fkey',
        'channel_feeds',
        'channels',
        ['channel_id'],
        ['id'],
    )
    op.create_foreign_key(
        'channel_feeds_feed_id_fkey',
        'channel_feeds',
        'feeds',
        ['feed_id'],
        ['id'],
    )
