#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from app import config, plex

from flask import Flask, g, request
from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.babel import Babel
from flask.ext.login import LoginManager, login_user, logout_user, current_user

from flask.ext.mail import Mail


app = Flask(__name__)
app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % os.path.join(config.DATA_DIR, "plexivity.db")

db = SQLAlchemy(app)
babel = Babel(app)

app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USERNAME'] = config.MAIL_LOGIN
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['DEFAULT_MAIL_SENDER'] = config.MAIL_FROM
app.config['MAIL_DEBUG'] = False
mail = Mail(app)

lm = LoginManager(app)
lm.init_app(app)
lm.login_view = 'login'

from app import views, models
