import logging

import celery
import os

import click
from flask.cli import AppGroup

from . import app, db
from .models import Feed, Channel
from . import telegram
from . import parser
from .templates.db import select_feeds, select_channels, select_pending_posts, delete_old_posts

logger = logging.getLogger(__name__)
FEED_PARSE_LIMIT = 1


class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask

worker = celery.Celery('example')
worker.conf.update(
    BROKER_URL=os.environ['REDIS_URL'],
    CELERY_RESULT_BACKEND=os.environ['REDIS_URL'],
    CELERY_TASK_SERIALIZER="json",
)


@worker.task
def parse_feeds(offset: int = 0):
    logger.info('Feed parsing started')
    feeds = select_feeds(offset, limit=FEED_PARSE_LIMIT)
    if not feeds:
        return

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
        db.session.add_all(posts)
        db.session.commit()

    # Run job again with increased offset
    parse_feeds.delay(offset + 1)


@worker.task
def send_to_channels():
    channels = select_channels()
    for channel in channels:
        # Get new posts
        posts = select_pending_posts(channel.id)

        # actual sent messages to telegram
        telegram.send_posts(channel, posts)

        # Update date cursor
        channel.date_cursor = max(post.date for post in posts)
        db.session.commit()


@worker.task
def cleanup_posts():
    delete_old_posts()


# Define cli for tasks
tasks_group = AppGroup('tasks')


@tasks_group.command('create')
@click.argument('func')
@click.argument('args', nargs=-1)
def run_async(func, args):
    name = f'telefeed.tasks.{func}'
    worker.tasks[name].delay(*args)


app.cli.add_command(tasks_group)