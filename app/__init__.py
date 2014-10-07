#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from app import config, plex

p = plex.Server(config.PMS_HOST, config.PMS_PORT)
from flask import Flask, g, request
from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.babel import Babel
from flask.ext.login import LoginManager, login_user, logout_user, current_user



app = Flask(__name__)
app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % os.path.join(config.DATA_DIR, "plexivity.db")

db = SQLAlchemy(app)
babel = Babel(app)

lm = LoginManager(app)
lm.init_app(app)
lm.login_view = 'login'

from app import views, models


class MyAnonymousUser(object):
    def __init__(self):
        self.random_books = 1

    def is_active(self):
        return False

    def is_authenticated(self):
        return False

    def is_anonymous(self):
        return True

    def get_id(self):
        return unicode(self.id)

lm.anonymous_user = MyAnonymousUser

@lm.user_loader
def load_user(id):
    return db.session.query(models.User).filter(models.User.id == int(id)).first()

@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None and hasattr(user, "locale"):
         return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(['de', "en"])

@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone

@app.before_request
def before_request():
    g.user = current_user
    g.plex = p


