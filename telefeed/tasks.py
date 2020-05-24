import logging
import os

import click
from dramatiq import Actor
from flask.cli import AppGroup
import dramatiq
from threading import local

from . import app, db, redis
from . import parser
from . import telegram
from .queries import (
    select_feeds,
    select_channels,
    select_pending_posts,
    delete_old_posts,
    insert_posts,
)


from dramatiq.brokers.redis import RedisBroker

broker = RedisBroker(url=os.getenv('REDIS_URL'))
dramatiq.set_broker(broker)

logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

FEED_PARSE_LIMIT = 1
FEED_PARSE_LOCK = 'FEED_PARSER_LOCK'
FEED_PARSE_LOCK_TTL_SEC = 60  # 1 min


class AppContextMiddleware(dramatiq.Middleware):
    # https://github.com/Bogdanp/flask_dramatiq_example

    state = local()

    def __init__(self, app):
        self.app = app

    def before_process_message(self, broker, message):
        context = self.app.app_context()
        context.push()

        self.state.context = context

    def after_process_message(self, broker, message, *, result=None, exception=None):
        try:
            context = self.state.context
            context.pop(exception)
            del self.state.context
        except AttributeError:
            pass

    after_skip_message = after_process_message


broker.add_middleware(AppContextMiddleware(app))


@dramatiq.actor
def parse_feeds(offset: int = 0):

    if offset == 0 and redis.get(FEED_PARSE_LOCK):
        logger.warning('Parsing already started')
        return

    redis.setex(FEED_PARSE_LOCK, FEED_PARSE_LOCK_TTL_SEC, 1)

    logger.info(f"Feed parsing started {offset}")
    feeds = select_feeds(offset, limit=FEED_PARSE_LIMIT)

    if not feeds:
        return send_to_channels()

    # Run job again with increased offset
    parse_feeds.send(offset + 1)

    for feed in feeds:
        posts = []
        # Get list of posts for every feed
        for post in parser.get_posts(feed):
            # Select only post that is newer than last parsed
            # post in feed (feed cursor)
            if not feed.date_cursor or post.date > feed.date_cursor:
                posts.append(post)

        if not posts:
            continue

        feed.date_cursor = max(post.date for post in posts)

        insert_posts(posts)
        db.session.commit()


@dramatiq.actor
def send_to_channels():
    logger.info("Sending posts to channels")
    channels = select_channels()
    for channel in channels:
        logger.info(f'Sending post to {channel.name}')

        # Get new posts
        posts = select_pending_posts(channel.id)
        if not posts:
            continue

        logger.info(f'Selected {len(posts)} posts for {channel.name}')

        # actual sent messages to telegram
        telegram.send_posts(channel, posts)

        # Update date cursor
        channel.date_cursor = max(post.date for post in posts)
        db.session.commit()

    cleanup_posts()


@dramatiq.actor
def cleanup_posts():
    delete_old_posts()


# Define cli for tasks
tasks_group = AppGroup("tasks")


@tasks_group.command("create")
@click.argument("func")
@click.argument("args", nargs=-1)
def run_async(func, args):
    actor: Actor = broker.actors[func]
    actor.send()


app.cli.add_command(tasks_group)
