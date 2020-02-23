from datetime import datetime

from telefeed import db, models, tasks


channel_name = 'seblogspoligon'


if __name__ == '__main__':
    channel = models.Channel(name=channel_name, date_cursor=datetime.now())
    with open('data/blogs.txt', 'r') as file:
        lines = file.readlines()
    db.session.add(channel)

    for line in lines:
        name, link = line.split(',')
        feed = models.Feed(name=name, url=link, date_cursor=datetime.now())
        channel.feeds.append(feed)

    db.session.commit()
    tasks.parse_feeds()
    tasks.send_to_channels()
    tasks.delete_old_posts()
