#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from app import config, plex

from flask import Flask, g, request, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.babel import Babel
from flask.ext.babel import lazy_gettext
from flask.ext.login import LoginManager, login_user, logout_user, current_user

from flask.ext.mail import Mail
from flask.ext.security import Security

app = Flask(__name__)
app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % os.path.join(config.DATA_DIR, "plexivity.db")

db = SQLAlchemy(app)
babel = Babel(app)

@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None and hasattr(user, "locale"):
        return user.locale

    return request.accept_languages.best_match(['de', "en", "fr"])

@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone

app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USERNAME'] = config.MAIL_LOGIN
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['DEFAULT_MAIL_SENDER'] = config.MAIL_FROM
app.config['MAIL_DEBUG'] = False

app.config['SECURITY_CONFIRMABLE'] = False
app.config['DEFAULT_MAIL_SENDER'] = 'info@site.com'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_TRACKABLE'] = True

mail = Mail(app)

lm = LoginManager(app)
lm.init_app(app)
lm.login_view = 'login'

from app import views, models, forms

security = Security(app, views.user_datastore, register_form=forms.ExtendedRegisterForm2, login_form=forms.Login)


## try import admin view and functions if module is not there, just skip this for now
try:
    from flask.ext.admin import Admin, AdminIndexView
    from flask.ext.admin.contrib.sqla import ModelView
    from flask.ext.admin.contrib import fileadmin
    from flask.ext.admin import expose

    # Create customized model view class
    class MyModelView(ModelView):

        def is_accessible(self):
            return current_user.is_authenticated()


    # Create customized index view class that handles login
    class MyAdminIndexView(AdminIndexView):

        @expose('/')
        def index(self):
            if not current_user.is_authenticated():
                return redirect(url_for('login'))
            return super(MyAdminIndexView, self).index()

    class UserView(ModelView):
        can_create = False

        # Override displayed fields
        column_list = ('email', 'locale')

        def __init__(self, session, **kwargs):
            # You can pass name and other parameters if you want to
            super(UserView, self).__init__(models.User, db.session, **kwargs)


    class HistoryView(ModelView):
        can_create = False
        column_list = ('time', 'user', 'title', 'platform', 'notified', 'stopped', 'paused', 'duration', 'view_offset')
        column_searchable_list = ('user', 'title', 'platform')

        def __init__(self, session, **kwargs):
            # You can pass name and other parameters if you want to
            super(HistoryView, self).__init__(models.Processed, db.session, **kwargs)

    admin = Admin(app, name="plexivity", index_view=MyAdminIndexView())

    admin.add_view(UserView(db.session))
    admin.add_view(HistoryView(db.session, name="History"))
    admin.add_view(fileadmin.FileAdmin(config.DATA_DIR + '/cache/', name='Cached Files'))
except:
    pass