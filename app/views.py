import os

from app import app, db, models, forms, lm, babel
from app import helper, plex, config

from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import login_required, current_user, logout_user, login_user
from flask import url_for, render_template, g, redirect, flash, request, send_from_directory
from flask.ext.babel import gettext as _
from babel.dates import format_timedelta
import json

p = plex.Server(config.PMS_HOST, config.PMS_PORT)

app.jinja_env.globals.update(helper=helper)
app.jinja_env.filters['timeago'] = helper.pretty_date
app.jinja_env.filters['timestamp'] = helper.date_timestamp

#workaround to load scheduler only once through debug time
#TODO: remove this
@app.before_first_request
def initialize():
    helper.startScheduler()

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

@app.route("/")
@login_required
def index():
    #check for plex connection else redirect to settings page and show a error message!
    if not g.plex.test():
        flash(_("Unable to connect to PMS. Please check your settings"), "error")
        return redirect(url_for("settings"))

    return render_template('stats.html', stats=g.plex.libraryStats(), activity=g.plex.currentlyPlaying(), new=g.plex.recentlyAdded())

#reload stuff
@app.route("/load/activity")
@login_required
def activity():
    return render_template('activity.html', activity=g.plex.currentlyPlaying())

@app.route("/stats")
@login_required
def stats():
    return render_template('stats.html', stats=g.plex.libraryStats(), activity=g.plex.currentlyPlaying(), new=g.plex.recentlyAdded())


@app.route("/setup", methods=("GET", "POST"))
def setup():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash(_("User %(username)s created", username=form.email.data), "success")
        user = models.User(password=generate_password_hash(form.password.data), email=form.email.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('settings'))
    if not db.session.query(models.User).first():
        return render_template('setup.html', form=form)
    else:
        return redirect(url_for("index"))


@app.route("/info/<id>")
@login_required
def info(id):
    return render_template('info.html', info=g.plex.getInfo(id))

@app.route("/login", methods=("GET", "POST"))
def login():
    if not db.session.query(models.User).first():
        return redirect(url_for("setup"))
    form = forms.Login()
    if form.validate_on_submit():
        user = db.session.query(models.User).filter(models.User.email == form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember_me.data)
            flash(_("you are now logged in as: '%(username)s'", username=user.email), category="success")
            return redirect(request.args.get("next") or url_for("index"))
        else:
            flash(_("username/password missmatch or no such user in database"), "error")
    return render_template('login.html', form=form)


@app.route("/history")
@login_required
def history():
    history = db.session.query(models.Processed).all()
    return render_template('history.html', history=history)

@app.route('/logout')
@login_required
def logout():
    if current_user is not None and current_user.is_authenticated():
        logout_user()
        flash(_("Logged out"), "success")
    return redirect(request.args.get("next") or url_for("index"))

@app.route('/cache/<path:filename>', strict_slashes=False)
@login_required
def cache(filename):
    cache_dir = os.path.join(config.DATA_DIR, "cache")
    cache_file = os.path.join(cache_dir, filename)
    if not os.path.exists(cache_file + ".jpg"):
        if helper.cache_file(filename, g.plex):
            return send_from_directory(cache_dir, filename + ".jpg")
        else:
            return app.send_static_file('images/fallback_cover.png')
    else:
        return send_from_directory(cache_dir, filename + ".jpg")

@app.route('/users')
@login_required
def users():
    users = db.session.query(models.Processed).group_by(models.Processed.user).all()
    return render_template('users.html', users=users)

@app.route("/settings", methods=("GET", "POST"))
@login_required
def settings():
    form = forms.Settings()
    old_host = config.PMS_HOST
    old_port = config.PMS_PORT
    if form.validate_on_submit():
        for x in form._fields:
            if x != "csrf_token":
                config.configval[x] = form[x].data
                setattr(config, x, form[x].data)
        config.save_config(config.configval)
        flash(_('Settings saved!'), "success")

    #update form values with latest config vals always!
    if config.PMS_PORT != old_port or config.PMS_HOST != old_host:
        print "reload plex server!"
        g.plex.update_settings(config.PMS_HOST, int(config.PMS_PORT))
        print g.plex.test()
   # p = False

    for x in form._fields:
        if x != "csrf_token":
            form[x].data = config.configval[x]

    return render_template('settings.html', form=form)