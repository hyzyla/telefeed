from datetime import datetime, timedelta
from typing import List, Dict, Any, Iterator, Optional

import feedparser
from feedparser import FeedParserDict as FeedDict
from dataclasses import dataclass
from bs4 import BeautifulSoup
import time
import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import os


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


DataDict = Dict[str, Any]

URLS = [
    'https://eng.uber.com/feed/',
    'https://medium.com/feed/airbnb-engineering',
    'https://www.confluent.io/feed/'
]
TELEGRAM_BOT_TOKEN = '735569833:AAE13xW8zjMKlABMp6UGeTVpDs7ZKnxUjcY'
DATABASE_URL = os.environ['DATABASE_URL']

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
scheduler = BlockingScheduler({
    'default': SQLAlchemyJobStore(url=DATABASE_URL),
})


def get_text_from_html(html: str):
    soup = BeautifulSoup(html, features='html.parser')

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it outs

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text


def time_struct_to_datetime(struct: time.struct_time) -> dataclass:
    return datetime.fromtimestamp(time.mktime(struct))


@dataclass
class Post:
    title: str
    link: str
    summary: str
    date_published: datetime


def parse_post(item: FeedDict) -> Optional[Post]:

    date_published = time_struct_to_datetime(item.published_parsed)
    content = get_text_from_html(item.summary)

    return Post(
        title=item.title,
        link=item.link,
        summary=content,
        date_published=date_published,
    )


def get_posts_by_urls(url: str) -> List[Post]:
    feed = feedparser.parse(url)
    yesterday = datetime.today() - timedelta(days=4)

    posts = []
    for item in feed.entries:
        post = parse_post(item)

        if post.date_published.date() == yesterday.date():
            posts.append(post)

        if post.date_published.date() < yesterday.date():
            break

    return posts


def get_posts() -> List[Post]:
    posts = []
    for url in URLS:
        posts.extend(get_posts_by_urls(url))
    return posts


def send_post(post: Post):
    bot.send_message(
        chat_id='@seblogspoligon',
        text=(
            f'[{post.title}]({post.link}) \n'
            f'{post.summary}'
        ),
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )

def send_posts(posts: List[Post]):
    logger.info(f'Send {len(posts)} posts')
    for post in posts:
        send_post(post)

@scheduler.scheduled_job('cron', hour=8)
def main():
    posts = get_posts()
    send_posts(posts)


if __name__ == '__main__':
    scheduler.start()
