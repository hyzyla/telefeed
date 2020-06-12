from flask_security import RoleMixin, UserMixin

from . import db
from .enums import PostStatus


class UserRoles(db.Model):
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text, unique=True)
    description = db.Column(db.Text)

    def __repr__(self):
        return self.name


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary='user_roles')


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    link = db.Column(db.Text, nullable=False, unique=True)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(
        db.Enum(
            PostStatus,
            native_enum=False,
            create_constraint=False,
            length=16,
        ),
        nullable=False,
        default=PostStatus.new,
    )
    feed_id = db.Column(
        db.Integer,
        db.ForeignKey('feeds.id', ondelete='CASCADE'),
        nullable=False,
    )
    feed = db.relationship('Feed')

    @property
    def summary(self):
        summary = self.body
        summary = summary.split('...')[0]
        return summary.split('…')[0]

    def __repr__(self):
        return self.title


class Feed(db.Model):
    __tablename__ = 'feeds'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    posts_counts = db.Column(
        db.Integer,
        default=0,
        server_default='0',
        nullable=False,
    )
    date_cursor = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return self.name


class Channel(db.Model):
    __tablename__ = 'channels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    feeds = db.relationship('Feed', secondary='channel_feeds', backref='channels')

    # Positing settings
    show_preview = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default='0',
    )
    separate_links = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default='0',
    )
    template = db.Column(db.Text, nullable=False, server_default='')

    date_cursor = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return self.name


class ChannelFeeds(db.Model):
    __tablename__ = 'channel_feeds'

    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(
        db.Integer,
        db.ForeignKey('feeds.id', ondelete='CASCADE'),
        nullable=False,
    )
    channel_id = db.Column(
        db.Integer,
        db.ForeignKey('channels.id', ondelete='CASCADE'),
        nullable=False,
    )

    date_cursor = db.Column(db.DateTime, nullable=True)
