from app import app
from app import helper, plex, config

from flask import url_for, render_template, g, redirect, flash
from flask.ext.babel import gettext as _
from flask.ext.babel import lazy_gettext
from babel.dates import format_timedelta
import json

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email

app.jinja_env.globals.update(helper=helper)
app.jinja_env.filters['timeago'] = helper.pretty_date

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

class Login(Form):
    username = StringField(lazy_gettext('Username'), validators=[DataRequired()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
    remember_me = BooleanField(lazy_gettext('Remember password'))

class Register(Form):
    username = StringField(lazy_gettext('Username'), validators=[DataRequired()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
    email = StringField(lazy_gettext('E-Mail'), validators=[DataRequired(), Email()])

class Settings(Form):
    use_pushover = BooleanField(lazy_gettext('use pushover for notifications'))
    pushover_user = StringField(lazy_gettext('Pushover User-Token'), validators=[RequiredIf("use_pushover")])
    pushover_app = StringField(lazy_gettext('Pushover App-Token'), validators=[RequiredIf("use_pushover")])

@app.route("/")
def index():
    #check for plex connection else redirect to settings page and show a error message!
    if not g.plex.test():
        flash(_("Unable to connect to PMS. Please check your settings"), "error")
        return redirect("settings")

    return render_template('stats.html', stats=g.plex.libraryStats(), activity=g.plex.currentlyPlaying(), new=g.plex.recentlyAdded())

#reload stuff
@app.route("/load/activity")
def activity():
    return render_template('activity.html', activity=g.plex.currentlyPlaying())

@app.route("/stats")
def stats():
    return render_template('stats.html', stats=g.plex.libraryStats(), activity=g.plex.currentlyPlaying(), new=g.plex.recentlyAdded())





@app.route("/info/<id>")
def info(id):
    return render_template('info.html', info=g.plex.getInfo(id))

@app.route("/login", methods=("GET", "POST"))
def login():
    form = Login()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    pass


@app.route("/settings")
def settings():
    return render_template('index.html')