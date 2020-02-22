import os
from typing import List

import telegram

from telefeed.models import Channel, Post


bot = telegram.Bot(token=os.getenv('TELEGRAM_TOKEN'))


def _send_message(channel: Channel, text: str) -> None:
    bot.send_message(
        chat_id=f'@{channel.name}',
        text=text,
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


def _post_markdown(post: Post) -> str:
    summary = post.body
    summary = summary.split('...')[0]
    summary = summary.split('…')[0]

    return (
        f'*[{post.feed.name}]*\n'
        f'[{post.title}]({post.link}) \n'
        f'{summary}'
     )


def send_posts(channel: Channel, posts: List[Post]) -> None:
    text = ''
    for post in posts:
        markdown = _post_markdown(post)
        if len(markdown) >= 4096:
            continue

        if len(text + markdown) < 4000:
            text = f'{text}\n\n{markdown}'
        else:
            _send_message(channel, text)
            text = markdown

    if text:
        _send_message(channel, text)
