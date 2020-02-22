from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import contains_eager

from telefeed import db
from telefeed.models import Feed, Channel, Post, ChannelFeeds


def select_feeds(offset: int, limit: int) -> List[Feed]:
    return (
        Feed.query
            .limit(limit)
            .offset(limit * offset)
            .order(Feed.id)
            .all()
    )


def select_channels() -> List[Channel]:
    return Channel.query.all()


def select_pending_posts(channel_id: str) -> List[Post]:
    """ Get posts for sending by given channel  """
    query = (
        db.session
        .query(Post)
        .join(Feed)
        .join(ChannelFeeds)
        .join(Channel)
        .options(contains_eager(Post.feed))
        .filter(
            # Post is published before last posted post in channel
            Post.date > Channel.date_cursor,
            Channel.id == channel_id,
        )
    )

    return query.all()


def delete_old_posts() -> None:
    query = (
        db.session
        .query(Post.id)
        .join(Feed)
        .join(ChannelFeeds)
        .join(Channel)
        .group_by(Post.id)
        # post is published in every channels that subscribed to post feed
        .having(sa.func.every(Post.date <= Channel.date_cursor))
    )

    db.session.query(Post).filter(Post.id.in_(query)).delete(synchronize_session=False)
    db.session.commit()
