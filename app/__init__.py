#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from app import config, plex
from app.logger import flask_rotation

from flask import Flask, g, request, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.babel import Babel
from flask.ext.babel import lazy_gettext
from flask.ext.login import LoginManager, login_user, logout_user, current_user

from flask.ext.mail import Mail
from flask.ext.security import Security

from flask.ext.restless import APIManager, ProcessingException

# thanks to http://flask.pocoo.org/snippets/35/
class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the 
    front-end server to add these headers, to let you quietly bind 
    this to a URL other than / and to an HTTP scheme that is 
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        server = environ.get('HTTP_X_FORWARDED_SERVER', '') 
        if server: 
            environ['HTTP_HOST'] = server
            
        return self.app(environ, start_response)

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
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

    translations = [str(translation) for translation in babel.list_translations()]
    return request.accept_languages.best_match(translations)

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

app.config["LOGGER_NAME"] = "flask"
app.logger.addHandler(flask_rotation)

app.config['SECRET_KEY'] = config.SECRET_KEY

app.config['SECURITY_CONFIRMABLE'] = False
app.config['DEFAULT_MAIL_SENDER'] = config.MAIL_FROM
app.config['SECURITY_REGISTERABLE'] = False
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = config.PASSWORD_SALT
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False


#make security messages translatabel
app.config['SECURITY_MSG_UNAUTHORIZED'] = (lazy_gettext('You do not have permission to view this resource.'), 'error')
app.config['SECURITY_MSG_CONFIRM_REGISTRATION'] = (lazy_gettext('Thank you. Confirmation instructions have been sent to %(email)s.'), 'success')
app.config['SECURITY_MSG_EMAIL_CONFIRMED'] = (lazy_gettext('Thank you. Your email has been confirmed.'), 'success')
app.config['SECURITY_MSG_ALREADY_CONFIRMED'] = (lazy_gettext('Your email has already been confirmed.'), 'info')
app.config['SECURITY_MSG_INVALID_CONFIRMATION_TOKEN'] = (lazy_gettext('Invalid confirmation token.'), 'error')
app.config['SECURITY_MSG_EMAIL_ALREADY_ASSOCIATED'] = (lazy_gettext('%(email)s is already associated with an account.'), 'error')
app.config['SECURITY_MSG_PASSWORD_MISMATCH'] = (lazy_gettext('Password does not match'), 'error')
app.config['SECURITY_MSG_RETYPE_PASSWORD_MISMATCH'] = (lazy_gettext('Passwords do not match'), 'error')
app.config['SECURITY_MSG_INVALID_REDIRECT'] = (lazy_gettext('Redirections outside the domain are forbidden'), 'error')
app.config['SECURITY_MSG_PASSWORD_RESET_REQUEST'] = (lazy_gettext('Instructions to reset your password have been sent to the given mail.'), 'info')
app.config['SECURITY_MSG_PASSWORD_RESET_EXPIRED'] = (lazy_gettext('You did not reset your password within %(within)s. New instructions have been sent to %(email)s.'), 'error')
app.config['SECURITY_MSG_INVALID_RESET_PASSWORD_TOKEN'] = (lazy_gettext('Invalid reset password token.'), 'error')
app.config['SECURITY_MSG_CONFIRMATION_REQUIRED'] = (lazy_gettext('Email requires confirmation.'), 'error')
app.config['SECURITY_MSG_CONFIRMATION_REQUEST'] = (lazy_gettext('Confirmation instructions have been sent to %(email)s.'), 'info')
app.config['SECURITY_MSG_CONFIRMATION_EXPIRED'] = (lazy_gettext('You did not confirm your email within %(within)s. New instructions to confirm your email have been sent to %(email)s.'), 'error')
app.config['SECURITY_MSG_LOGIN_EXPIRED'] = (lazy_gettext('You did not login within %(within)s. New instructions to login have been sent to %(email)s.'), 'error')
app.config['SECURITY_MSG_LOGIN_EMAIL_SENT'] = (lazy_gettext('Instructions to login have been sent to %(email)s.'), 'success')
app.config['SECURITY_MSG_INVALID_LOGIN_TOKEN'] = (lazy_gettext('Invalid login token.'), 'error')
app.config['SECURITY_MSG_DISABLED_ACCOUNT'] = (lazy_gettext('Account is disabled.'), 'error')
app.config['SECURITY_MSG_EMAIL_NOT_PROVIDED'] = (lazy_gettext('Email not provided'), 'error')
app.config['SECURITY_MSG_INVALID_EMAIL_ADDRESS'] = (lazy_gettext('Invalid email address'), 'error')
app.config['SECURITY_MSG_PASSWORD_NOT_PROVIDED'] = (lazy_gettext('Password not provided'), 'error')
app.config['SECURITY_MSG_PASSWORD_NOT_SET'] = (lazy_gettext('No password is set for this user'), 'error')
app.config['SECURITY_MSG_PASSWORD_INVALID_LENGTH'] = (lazy_gettext('Password must be at least 6 characters'), 'error')
app.config['SECURITY_MSG_USER_DOES_NOT_EXIST'] = (lazy_gettext('Specified user does not exist'), 'error')
app.config['SECURITY_MSG_INVALID_PASSWORD'] = (lazy_gettext('Invalid password'), 'error')
app.config['SECURITY_MSG_PASSWORDLESS_LOGIN_SUCCESSFUL'] = (lazy_gettext('You have successfuly logged in.'), 'success')
app.config['SECURITY_MSG_PASSWORD_RESET'] = (lazy_gettext('You successfully reset your password and you have been logged in automatically.'), 'success')
app.config['SECURITY_MSG_PASSWORD_IS_THE_SAME'] = (lazy_gettext('Your new password must be different than your previous password.'), 'error')
app.config['SECURITY_MSG_PASSWORD_CHANGE'] = (lazy_gettext('You successfully changed your password.'), 'success')
app.config['SECURITY_MSG_LOGIN'] = (lazy_gettext('Please log in to access this page.'), 'info')
app.config['SECURITY_MSG_REFRESH'] = (lazy_gettext('Please reauthenticate to access this page.'), 'info')

# uncomment for productional use
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'

mail = Mail(app)

lm = LoginManager(app)
lm.init_app(app)
lm.login_view = 'login'

from app import views, models, forms

def auth_func(*args, **kw):
    if not current_user.is_authenticated():
        raise ProcessingException(description='Not authenticated!', code=401)

apimanager = APIManager(app, flask_sqlalchemy_db=db, preprocessors=dict(GET_SINGLE=[auth_func], GET_MANY=[auth_func]))

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
apimanager.create_api(models.User, methods=['GET', 'POST', 'DELETE'], exclude_columns=['password'])
apimanager.create_api(models.Processed, methods=['GET', 'DELETE'], collection_name='history')
apimanager.create_api(models.RecentlyAdded, methods=['GET', 'DELETE'], collection_name='recently-added')

security = Security(app, views.user_datastore, register_form=forms.ExtendedRegisterForm2, login_form=forms.Login)

#fix lazy_gettext json encoding ...
from flask.json import JSONEncoder as BaseEncoder
from speaklater import _LazyString

class JSONEncoder(BaseEncoder):
    def default(self, o):
        if isinstance(o, _LazyString):
            return str(o)

        return BaseEncoder.default(self, o)

app.json_encoder = JSONEncoder

#try import admin view and functions if module is not there, just skip this for now

from flask.ext.admin import Admin, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib import fileadmin
from flask.ext.admin import expose

# Create customized model view class
class MyModelView(ModelView):

    def is_accessible(self):
        return current_user.has_role('admin')


# Create customized index view class that handles login
class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        if not current_user.has_role('admin'):
            return redirect(url_for('security.login'))
        return super(MyAdminIndexView, self).index()

class UserView(MyModelView):
    can_create = True

    # Override displayed fields
    column_list = ('email', 'locale')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(UserView, self).__init__(models.User, db.session, **kwargs)

class MyFileAdmin(fileadmin.FileAdmin):

    def is_accessible_path(self, path):
        return current_user.has_role('admin')

class RecentlyAddedView(MyModelView):
    can_create = False
    column_list = ('item_id', 'time', 'title')
    column_searchable_list = ('debug', 'filename', 'title')
    column_default_sort = ('time', True)
    
    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(RecentlyAddedView, self).__init__(models.RecentlyAdded, db.session, **kwargs)

class HistoryView(MyModelView):
    can_create = False
    column_list = ('time', 'user', 'title', 'platform', 'notified', 'stopped', 'paused', 'progress')
    column_searchable_list = ('user', 'title', 'platform')
    column_filters = ('time', 'user', 'title', 'platform', 'notified', 'stopped', 'paused', 'duration', 'orig_title', 'season', 'episode', 'year')
    column_default_sort = ('time', True)

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(HistoryView, self).__init__(models.Processed, db.session, **kwargs)

admin = Admin(app, name="plexivity", index_view=MyAdminIndexView())

admin.add_view(UserView(db.session))
admin.add_view(HistoryView(db.session, name="History"))
admin.add_view(RecentlyAddedView(db.session, name="Recently Added"))

if config.CACHE_IMAGES and os.path.exists(os.path.join(config.DATA_DIR, "cache")):
    admin.add_view(MyFileAdmin(config.DATA_DIR + '/cache/', name='Cached Files'))
