import os
from typing import List, Generator, Set

import jinja2
import telegram

from telefeed.models import Channel, Post


bot = telegram.Bot(token=os.getenv('TELEGRAM_TOKEN'))


DEFAULT_TEMPLATE = """
*[{{ post.feed.name }}]*
[{{ post.title }}]({{ post.link }})
{{ post.summary }}
"""


def _send_message(channel: Channel, text: str) -> None:
    try:
        bot.send_message(
            chat_id=f'@{channel.name}',
            text=text,
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=not channel.show_preview,
        )
    except Exception as exc:
        print(exc)


def _post_markdown(channel: Channel, post: Post) -> str:
    template_str = channel.template or DEFAULT_TEMPLATE
    template = jinja2.Template(template_str)
    return template.render(post=post, channel=channel)


def _uniq_posts(posts: List[Post]) -> Generator[Post, None, None]:
    seen: Set[str] = set()
    for post in posts:
        if post.title in seen:
            continue
        seen.add(post.title)
        yield post


def send_posts(channel: Channel, posts: List[Post]) -> None:
    text = ''
    for post in _uniq_posts(posts):
        try:
            markdown = _post_markdown(channel, post)
        except Exception as exc:
            print(exc)
            continue

        if len(markdown) >= 4096:
            continue

        # Every post will be sent as separate message
        if channel.separate_links:
            _send_message(channel, markdown)
            continue

        if len(text + markdown) < 4000:
            text = f'{text}\n\n{markdown}'
        else:
            _send_message(channel, text)
            text = markdown

    if text:
        _send_message(channel, text)
