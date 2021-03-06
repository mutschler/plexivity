#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SelectField, TextField, Field
from wtforms.widgets import TextInput, TextArea
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange, IPAddress, ValidationError
from werkzeug.security import check_password_hash

from flask.ext.babel import lazy_gettext
from flask_security.forms import RegisterForm, LoginForm
from flask.ext.security.utils import encrypt_password

from app import config, babel, db, models
import requests
import json

class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []

def valid_json_check(form, field):
    if type(field.data) != "dict":
        try:
            json_object = json.loads(field.data)
        except ValueError, e:
            raise ValidationError('Field must be valid JSON')
    

class JSONField(Field):
    widget = TextArea()

    def _value(self):
        if self.data and json.loads(self.data):
            return json.dumps(json.loads(self.data), sort_keys=True, indent=4, separators=(',', ': '))
        else:
            return u''

    def process_formdata(self, value):
        if value:
            if value[0] != "":
                self.data = json.dumps(json.loads(value[0]))
            else:
                self.data = json.dumps(dict())
        else:
            self.data = json.dumps(dict())

class RequiredIf(DataRequired):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)

class PlexImportForm(Form):
    __title__ = lazy_gettext("Plex Media Server Import")

    IMPORT_USERNAME = StringField(lazy_gettext('Plex Username to use for Import'), default=config.IMPORT_USERNAME)
    

class Login(LoginForm):
    email = StringField(lazy_gettext('E-Mail'), validators=[DataRequired(), Email()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
    remember = BooleanField(lazy_gettext('Remember password'))
    submit = None

    def validate(self):
        #check for old pw hash and upadte password if needed
        self.user = db.session.query(models.User).filter(models.User.email == self.email.data).first()
        if self.user and self.user.password.startswith("pbkdf2:sha1"):
            if check_password_hash(self.user.password, self.password.data):
                self.user.password = encrypt_password(self.password.data)
                self.user.active = 1
                self.user.roles.append(db.session.query(models.Role).filter(models.Role.name=="admin").first())
                db.session.commit()
                return True

        #do the flask-security checks
        if not super(Login, self).validate():
            return False

        return True

class Settings(Form):
    __title__ = lazy_gettext("Plex Media Server Settings")

    PMS_HOST = StringField(lazy_gettext('Plex Media Server Host'), validators=[DataRequired()], default=config.PMS_HOST)
    PMS_PORT = IntegerField(lazy_gettext('Plex Media Server Port'), validators=[DataRequired(), NumberRange()], default=config.PMS_PORT)
    PMS_USER = StringField(lazy_gettext('Plex Username'), validators=[DataRequired()], default=config.PMS_USER)
    PMS_PASS = StringField(lazy_gettext('Plex Password'), validators=[DataRequired()], default=config.PMS_PASS)
    #PMS_SSL = BooleanField(lazy_gettext('Use SSL encryption'), default=bool(config.PMS_SSL))

    NOTIFY_PUSHOVER = BooleanField(lazy_gettext('use pushover for notifications'), default=config.NOTIFY_PUSHOVER)
    PUSHOVER_USER = StringField(lazy_gettext('Pushover User-Token'), validators=[RequiredIf("NOTIFY_PUSHOVER")], default=config.PUSHOVER_USER)
    PUSHOVER_TOKEN = StringField(lazy_gettext('Pushover App-Token'), validators=[RequiredIf("NOTIFY_PUSHOVER")], default=config.PUSHOVER_TOKEN)

    NOTIFY_MAIL = BooleanField(lazy_gettext('use mail for notifications'), default=config.NOTIFY_MAIL)
    MAIL_SERVER = StringField(lazy_gettext('SMTP Mail Server'), validators=[RequiredIf("NOTIFY_MAIL")], default=config.MAIL_SERVER)
    MAIL_LOGIN = StringField(lazy_gettext('SMTP Server login'), validators=[RequiredIf("NOTIFY_MAIL")], default=config.MAIL_LOGIN)
    MAIL_PASSWORD = StringField(lazy_gettext('SMTP Server password'), validators=[RequiredIf("NOTIFY_MAIL")], default=config.MAIL_PASSWORD)
    MAIL_PORT = IntegerField(lazy_gettext('SMTP Mail Port'), validators=[RequiredIf("NOTIFY_MAIL"), NumberRange()], default=config.MAIL_PORT)
    MAIL_FROM = StringField(lazy_gettext('Sender Mail Information'), validators=[RequiredIf("NOTIFY_MAIL")], default=config.MAIL_FROM)

    #DATA_DIR = StringField(lazy_gettext('plexivity data directory'), validators=[DataRequired()], default=config.DATA_DIR)
    PORT = IntegerField(lazy_gettext('plexivity port'), validators=[DataRequired(), NumberRange()], default=config.PORT)
    NOTIFY_START =  BooleanField(lazy_gettext('Send notification on start'), default=config.NOTIFY_START)
    START_MESSAGE = StringField(lazy_gettext('String for watching notification'), validators=[DataRequired()], default=config.START_MESSAGE)
    NOTIFY_STOP =  BooleanField(lazy_gettext('Send notification on stop'), default=config.NOTIFY_STOP)
    STOP_MESSAGE = StringField(lazy_gettext('String for stoped watching notification'), validators=[DataRequired()], default=config.STOP_MESSAGE)
    NOTIFY_PAUSE =  BooleanField(lazy_gettext('Send notification on pause'), default=config.NOTIFY_PAUSE)
    PAUSE_MESSAGE = StringField(lazy_gettext('String for paused notification'), validators=[DataRequired()], default=config.PAUSE_MESSAGE)
    NOTIFY_RESUME = BooleanField(lazy_gettext('Send notification on resume'), default=config.NOTIFY_RESUME)
    RESUME_MESSAGE = StringField(lazy_gettext('String for resume notification'), validators=[DataRequired()], default=config.RESUME_MESSAGE)
    NOTIFY_RECENTLYADDED = BooleanField(lazy_gettext('Send notification for recently added media'), default=config.NOTIFY_RECENTLYADDED)
    RECENTLYADDED_MESSAGE = StringField(lazy_gettext('String for recently added notification'), validators=[DataRequired()], default=config.RECENTLYADDED_MESSAGE)

    EXCLUDE_USERS = TagListField(lazy_gettext('Comma seperated list of plex usernames to exclude from notifications'), default=','.join(config.EXCLUDE_USERS))
    EXCLUDE_SECTIONS = TagListField(lazy_gettext('Comma seperated list of plex section ids to exclude from notifications'), default=','.join(config.EXCLUDE_SECTIONS))
    USER_NAME_MAP = JSONField(lazy_gettext('JSON Map of plex usernames and push names'), validators=[valid_json_check], default=config.USER_NAME_MAP)

class ExtendedRegisterForm2(RegisterForm):
    all_locales = [('en', 'English')]
    for x in babel.list_translations():
        all_locales.append( (x.language, x.display_name) )

    email = StringField(lazy_gettext('E-Mail'), validators=[DataRequired(), Email()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired(),EqualTo("password_confirm")])
    password_confirm = PasswordField(lazy_gettext('Retype password'), validators=[DataRequired(),EqualTo("password")])
    locale = SelectField(lazy_gettext('Language'), choices=all_locales)
    submit = None

class ExtendedRegisterForm(RegisterForm):
    all_locales = [('en', 'English')]
    for x in babel.list_translations():
        all_locales.append( (x.language, x.display_name) )

    email = StringField(lazy_gettext('E-Mail'), validators=[DataRequired(), Email()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired(),EqualTo("password_confirm")])
    password_confirm = PasswordField(lazy_gettext('Retype password'), validators=[DataRequired(),EqualTo("password")])
    locale = SelectField(lazy_gettext('Language'), choices=all_locales)
    submit = None