import textwrap
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any

import feedparser
from bs4 import BeautifulSoup
from feedparser import FeedParserDict as FeedDict

from .models import Post, Feed

DataDict = Dict[str, Any]


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


def parse_content(item: FeedDict) -> str:
    content = get_text_from_html(item.get('summary') or '')
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
    return content


def parse_date(item: FeedDict) -> datetime:
    date = item.get('published_parsed') or item.get('updated_parsed')
    return time_struct_to_datetime(date)


def get_posts(feed: Feed) -> List[Post]:
    try:
        _feed = feedparser.parse(feed.url)
    except Exception as exc:
        print(exc)
        return []

    for item in _feed.entries:
        try:
            content = parse_content(item)
        except Exception as e:
            print(item)
            print(e)
            continue

        try:
            date = parse_date(item)
        except Exception:
            continue

        yield Post(
            title=item.title,
            body=content,
            link=item.link,
            date=date,
            feed=feed,
        )
