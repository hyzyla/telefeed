

import celery
import os

import click
from flask.cli import AppGroup

from . import app as flask_app, db
from .models import Feed
from . import parser


FEED_PARSE_LIMIT = 1


class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask

app = celery.Celery('example')
app.conf.update(
    BROKER_URL=os.environ['REDIS_URL'],
    CELERY_RESULT_BACKEND=os.environ['REDIS_URL'],
    CELERY_TASK_SERIALIZER="json",
)


@app.task
def parse_feeds(offset: int = 0):
    # TODO: add logging
    feeds = Feed.query.limit(FEED_PARSE_LIMIT).offset(FEED_PARSE_LIMIT * offset).all()
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


# Define cli for running tasks
tasks_group = AppGroup('tasks')


@tasks_group.command('create')
@click.argument('func')
@click.argument('args', nargs=-1)
def run_async(func, args):
    name = f'telefeed.tasks.{func}'
    app.tasks[name].delay(*args)


flask_app.cli.add_command(tasks_group)
