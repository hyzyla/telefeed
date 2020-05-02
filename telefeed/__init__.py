import os

import flask
from flask import url_for
from flask_migrate import Migrate
from flask_security import SQLAlchemyUserDatastore, Security
from flask_sqlalchemy import SQLAlchemy
from flask_admin import helpers as admin_helpers

app = flask.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'default'

app.config['SECURITY_PASSWORD_HASH'] = os.environ['SECURITY_PASSWORD_HASH']
app.config['SECURITY_PASSWORD_SALT'] = os.environ['SECURITY_PASSWORD_SALT']
app.config['SECURITY_REGISTERABLE'] = os.environ['SECURITY_REGISTERABLE']
app.config['SECURITY_SEND_REGISTER_EMAIL'] = os.environ['SECURITY_SEND_REGISTER_EMAIL']
app.config['BROKER_POOL_LIMIT'] = os.environ['BROKER_POOL_LIMIT']

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import models
from . import admin
from . import tasks
from . import parser
from . import handlers

user_store = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_store)


# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.admin.base_template,
        admin_view=admin.admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )



