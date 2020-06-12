from collections import defaultdict
from typing import List

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import contains_eager

from telefeed import db
from telefeed.enums import PostStatus
from telefeed.models import Feed, Channel, Post, ChannelFeeds


def select_feeds(offset: int, limit: int) -> List[Feed]:
    return (
        Feed.query
            .order_by(Feed.id)
            .limit(limit)
            .offset(limit * offset)
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
            Post.status == PostStatus.new,
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
        .filter(Post.status == PostStatus.new)
        # post is published in every channels that subscribed to post feed
        .having(sa.func.every(Post.date <= Channel.date_cursor))
    )

    (
        db.session
            .query(Post)
            .filter(Post.id.in_(query))
            .update({Post.status: PostStatus.sent}, synchronize_session=False)
    )
    db.session.commit()


def insert_posts(posts: List[Post]) -> None:
    posts_data = [
        {
            'title': post.title,
            'body': post.body,
            'link': post.link,
            'date': post.date,
            'feed_id': post.feed_id or post.feed.id,
        }
        for post in posts
    ]
    db.session.execute(
        insert(Post)
        .values(posts_data)
        .on_conflict_do_nothing(index_elements=['link'])
    )


def update_feeds_counts(posts: List[Post]):
    mapping = defaultdict(lambda *args, **kwargs: 0)
    for post in posts:
        mapping[post.feed_id] += 1
    print(mapping)
    for feed_id, count in mapping.items():
        (
            db.session
                .query(Feed)
                .filter(Feed.id == feed_id)
                .update({Feed.posts_counts: Feed.posts_counts + count}, synchronize_session=False)
        )