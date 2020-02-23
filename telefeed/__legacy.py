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
import textwrap


logging.basicConfig(
    format='%(asctime)s|%(levelname)s|%(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


DataDict = Dict[str, Any]

URLS = set([
    ('Uber', 'https://eng.uber.com/feed/'),
    ('Airbnb', 'https://medium.com/feed/airbnb-engineering'),
    ('500px', 'https://developers.500px.com/feed'),
    ('Confluent', 'https://www.confluent.io/feed'),
    ('8th Light', 'https://8thlight.com/blog/feed/rss.xml'),
    ('AdRoll', 'http://tech.adroll.com/feed.xml'),
    ('Addepar', 'https://www.confluent.io/feed'),
    ('Build@Addepar', 'https://medium.com/feed/build-addepar'),
    ('Affinity', 'https://build.affinity.co/feed'),
    ('Airbrake', 'https://airbrake.io/blog/feed'),
    ('Advanced Web Machinery', 'https://advancedweb.hu/rss.xml'),
    ('Airtame', 'https://airtame.engineering/feed'),
    ('Algolia', 'https://blog.algolia.com/feed/'),
    ('Allegro Group', 'https://allegro.tech/feed.xml'),
    ('AppNexus', 'https://techblog.appnexus.com/feed'),
    ('Arkency', 'https://blog.arkency.com/atom.xml'),
    ('Artsy', 'https://artsy.github.io/feed'),
    ('Auth0', 'https://auth0.com/blog/rss.xml'),
    ('Avenue Code', 'https://blog.avenuecode.com/rss.xml'),
])
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
    name: str
    title: str
    link: str
    summary: str
    date_published: datetime

    def get_markdown(self):
        summary = self.summary
        summary = summary.split('...')[0]
        summary = summary.split('…')[0]

        return (
            f'*[{self.name}]*\n'
            f'[{self.title}]({self.link}) \n'
            f'{self.summary}'
         )


def parse_post(name: str, item: FeedDict) -> Optional[Post]:

    date_published = time_struct_to_datetime(item.published_parsed)
    content = get_text_from_html(item.summary)
    content = textwrap.shorten(content, width=300, placeholder="...")
    content = (
        content
        .replace('_', '')
        .replace('*', '')
        .replace('`', '')
        .replace('[', '')
        .replace(']', '')
        .replace('(', '')
        .replace(')', '')
    )

    return Post(
        name=name,
        title=item.title,
        link=item.link,
        summary=content,
        date_published=date_published,
    )


def get_posts_by_urls(name: str, url: str) -> List[Post]:
    feed = feedparser.parse(url)
    yesterday = datetime.today() - timedelta(days=4)

    posts = []
    for item in feed.entries:
        post = parse_post(name, item)

        if post.date_published.date() == yesterday.date():
            posts.append(post)

        if post.date_published.date() < yesterday.date():
            break

    return posts


def get_posts() -> List[Post]:
    posts = []
    for name, url in URLS:
        try:
            parsed_posts = get_posts_by_urls(name, url)
        except Exception as exception:
            logger.exception(
                msg='Cannot get post by url',
                extra={
                    'url': url,
                    'name': name,
                    'exception': exception
                },
            )
            continue

        logger.info(
            msg='New posts by url',
            extra={
                'url': url,
                'company_name': name,
                'posts': len(parsed_posts),
            }
        )
        posts.extend(parsed_posts)

    return posts


def send_post(text: str):

    bot.send_message(
        chat_id='@seblogspoligon',
        text=text,
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


def send_posts(posts: List[Post]):
    logger.info(f'Send {len(posts)} posts')
    text = ''
    for post in posts:
        markdown = post.get_markdown()
        if len(markdown) >= 4096:
            logger.exception(
                msg='Message too long',
                extra={'message': markdown}
            )
            continue

        if len(text + markdown) < 4000:
            text = f'{text}\n\n{markdown}'
        else:
            send_post(text)
            text = markdown

    if text:
        send_post(text)


# @scheduler.scheduled_job('interval', seconds=20)
@scheduler.scheduled_job('cron', hour=8)
def main():
    posts = get_posts()
    send_posts(posts)


if __name__ == '__main__':
   scheduler.start()
