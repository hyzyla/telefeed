import logging
import os

import celery
import click
from flask.cli import AppGroup

from . import app, db
from . import parser
from . import telegram
from .queries import select_feeds, select_channels, select_pending_posts, delete_old_posts

logger = logging.getLogger(__name__)
FEED_PARSE_LIMIT = 1


class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask

worker = celery.Celery('example')
worker.conf.update(
    broker_url=os.environ['REDIS_URL'],
    celery_result_backend=os.environ['REDIS_URL'],
    celery_task_serializer="json",
    broker_pool_limit=0,
    redis_max_connections=0,
    task_ignore_result=True,
    result_expires=60 * 60, # 1 hour
)


@worker.task
def parse_feeds(offset: int = 0):
    logger.info('Feed parsing started')
    feeds = select_feeds(offset, limit=FEED_PARSE_LIMIT)
    if not feeds:
        return send_to_channels()

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
        if not posts:
            continue

        # actual sent messages to telegram
        telegram.send_posts(channel, posts)

        # Update date cursor
        channel.date_cursor = max(post.date for post in posts)
        db.session.commit()

    cleanup_posts()


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
    worker.tasks[name].delay(*args).forget()


app.cli.add_command(tasks_group)
