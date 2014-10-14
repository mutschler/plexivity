#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from app import app, db, models, forms, lm, babel
from app import helper, plex, config

from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import login_required, current_user, logout_user, login_user
from flask import url_for, render_template, g, redirect, flash, request, send_from_directory, send_file
from flask.ext.babel import gettext as _
from babel.dates import format_timedelta
import json

import datetime

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

    return render_template('index.html', stats=g.plex.libraryStats(), activity=g.plex.currentlyPlaying(), new=g.plex.recentlyAdded())

#reload stuff
@app.route("/load/activity")
@login_required
def activity():
    return render_template('include/activity.html', activity=g.plex.currentlyPlaying())

@app.route("/stats")
@login_required
def stats():

    daily = db.session.query(db.func.count(models.Processed.title), models.Processed).group_by(db.extract('day', models.Processed.time)).order_by(models.Processed.time.desc()).all()
    dailyJSON = list()
    for day in daily:
        dailyJSON.append({"y": day[0], "x": day[1].time.date().strftime("%Y-%m-%d")})

    monthly = db.session.query(db.func.count(models.Processed.title), models.Processed).filter(models.Processed.time >= datetime.datetime.now() - datetime.timedelta(weeks=53)).group_by(db.extract('month', models.Processed.time)).order_by(models.Processed.time.desc()).all()
    monthlyJSON = list()
    for monthly in monthly:
        monthlyJSON.append({"y": monthly[0], "x": monthly[1].time.date().strftime("%Y-%m")})

    hourly = db.session.query(db.func.count(db.extract('hour', models.Processed.time)), models.Processed).filter(models.Processed.time >= datetime.datetime.now() - datetime.timedelta(hours=24)).group_by(db.extract('hour', models.Processed.time)).order_by(models.Processed.time.asc()).all()
    hourlyJSON = list()
    for hour in hourly:
        hourlyJSON.append({"y": hour[0], "x": hour[1].time.strftime("%Y-%m-%d %H")})



    maxhourly = db.session.query(db.func.count(db.extract('hour', models.Processed.time)), models.Processed).group_by(db.extract('hour', models.Processed.time)).order_by(models.Processed.time.asc()).all()
    maxhourlyJSON = list()
    for hour in maxhourly:
        maxhourlyJSON.append({"y": hour[0], "x": hour[1].time.strftime("%Y-%m-%d %H")})

    return render_template('stats.html', hourly=hourlyJSON, daily=dailyJSON, monthly=monthlyJSON, maxhourly=maxhourlyJSON)


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

@app.route("/hue", methods=("GET", "POST"))
@login_required
def hue(args=False):
    from app.providers import hue

    if config.BRIDGE_IP and hue.register_bridge(config.BRIDGE_IP):
        return render_template('hue.html', form=False, bridge_ip=config.BRIDGE_IP)

    form = forms.HueForm()
    if form.validate_on_submit():

        check_hue = hue.register_bridge(form.HUE_IP.data)
        if check_hue:
            config.BRIDGE_IP = check_hue
            config.configval["BRIDGE_IP"] = check_hue
            config.save_config(config.configval)
            flash(_('Successfully connected to Hue Bridge with ip %(ip)s', ip=check_hue) , "success")
            return redirect(url_for('index'))
        else:
            return render_template('hue.html')
    return render_template('hue.html', form=form)

@app.route("/hue/settings")
@login_required
def hue_settings():
    from app.providers import hue
    lights = hue.get_available_lights()
    return render_template("hue_settings.html", lights=lights)

@app.route("/hue/unlink")
@login_required
def hue_unlink():
    config.BRIDGE_IP = ""
    config.configval["BRIDGE_IP"] = ""
    #TODO: Final unlinking, save config remove hue.conf file!
    flash(_('Successfully disconnected from Hue Bridge'), "success")
    #return render_template('hue.html')
    return redirect(url_for("hue"))

@app.route("/hue/push", methods=("GET", "POST"))
@login_required
def hue_push():
    from app.providers import hue
    check_hue = hue.register_bridge(config.BRIDGE_IP)
    if check_hue:
        flash(_('Successfully connected to Hue Bridge with ip %(ip)s', ip=check_hue), "success")
        return redirect(url_for('index'))
    else:
        return redirect(url_for('hue'))
    return render_template('hue.html')


@app.route("/charts")
@login_required
def charts():
    #all10 = db.session.query(models.Processed.count as count, models.Processed).group_by(models.Processed.title).order_by(db.func.count(models.Processed.title).desc()).limit(10)
    all10 = db.session.query(db.func.count(models.Processed.title), models.Processed).group_by(models.Processed.title).having(db.func.count(models.Processed.title) > 0).order_by(db.func.count(models.Processed.title).desc(), models.Processed.time.desc()).limit(10)
    movie10 = db.session.query(db.func.count(models.Processed.title), models.Processed).group_by(models.Processed.title).having(db.func.count(models.Processed.title) > 0).order_by(db.func.count(models.Processed.title).desc(), models.Processed.time.desc()).limit(10)
    show_top10 = db.session.query(db.func.count(models.Processed.orig_title), models.Processed).group_by(models.Processed.orig_title).having(db.func.count(models.Processed.orig_title) > 0).order_by(db.func.count(models.Processed.orig_title).desc(), models.Processed.time.desc()).limit(10)
    return render_template('charts.html', all_top10=all10, movie_top10=movie10, show_top10=show_top10, ep_top10=movie10)

@app.route("/info/<id>")
@login_required
def info(id):
    info = g.plex.getInfo(id)
    views = None
    parent = None
    episodes = None
    cur_el = info.getchildren()[0]
    cur_type = cur_el.get("type")
    if cur_type == "movie":
        views = db.session.query(models.Processed).filter(models.Processed.title == info.find("Video").get("title")).all()
    elif cur_type == "season":
        parent = g.plex.getInfo(info.getchildren()[0].get("parentRatingKey")).getchildren()[0]
        episodes = g.plex.episodes(id)
    elif cur_type == "episode":
        views = db.session.query(models.Processed).filter(models.Processed.session_id.like("%/metadata/" + cur_el.get("ratingKey") + "_%")).all()
    elif cur_type == "show":
        episodes = db.session.query(db.func.count(models.Processed.title), models.Processed).filter(models.Processed.orig_title.like(cur_el.get("title"))).group_by(models.Processed.title).having(db.func.count(models.Processed.orig_title) > 0).order_by(db.func.count(models.Processed.orig_title).desc(), models.Processed.time.desc()).all()

    return render_template('info.html', info=g.plex.getInfo(id), history=views, parent=parent, episodes=episodes)

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
    history = db.session.query(models.Processed).order_by(models.Processed.time.desc()).all()
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
            return send_file('static/images/poster.png')
    else:
        return send_from_directory(cache_dir, filename + ".jpg")

@app.route('/users')
@login_required
def users():
    users = db.session.query(models.Processed).group_by(models.Processed.user).all()
    return render_template('users.html', users=users)


@app.route('/user/<name>')
@login_required
def user(name):
    platform_plays = db.session.query(db.func.count(models.Processed.platform), models.Processed).filter(models.Processed.user == name).group_by(models.Processed.platform).all()
    recent = db.session.query(models.Processed).filter(models.Processed.user == name).order_by(models.Processed.time.desc()).limit(12)
    stats = helper.calculate_plays(db, models, name)
    history = db.session.query(models.Processed).filter(models.Processed.user == name).order_by(models.Processed.time.desc()).all()
    allstuff = db.session.query(models.Processed).filter(models.Processed.user == name).order_by(models.Processed.time.desc()).all()
    return render_template('user.html', stats=stats, username=name, platforms=platform_plays, recently=recent, allstuff=allstuff, history=history)

@app.route('/logs')
@login_required
def logs():
    f = open(os.path.join(config.DATA_DIR, "plexivity.log"), "r")
    content = f.readlines()
    f.close()
    print content
    log_content = reversed(content[-200:])
    return render_template('logs.html', log=log_content)

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