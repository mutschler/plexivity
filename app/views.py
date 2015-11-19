#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import datetime

from app import app, db, models, forms, lm
from app import helper, plex, config

from flask.ext.login import login_required, logout_user
from flask import url_for, render_template, g, redirect, flash, request, send_from_directory, send_file, session
from flask.ext.babel import gettext as _
from babel.dates import format_timedelta

from flask.ext.security import SQLAlchemyUserDatastore, url_for_security, current_user
from flask.ext.security.decorators import roles_required
from flask.ext.security.utils import encrypt_password, login_user

from datatables import DataTable

import tweepy

user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)

p = plex.Server(config.PMS_HOST, config.PMS_PORT)

app.jinja_env.globals.update(helper=helper)
app.jinja_env.filters['timeago'] = helper.pretty_date
app.jinja_env.filters['timestamp'] = helper.date_timestamp



#workaround to load scheduler only once through debug time
#TODO: remove this
@app.before_first_request
def initialize():
    helper.startScheduler()

@lm.user_loader
def load_user(id):
    return db.session.query(models.User).filter(models.User.id == int(id)).first()


@app.before_request
def before_request():
    g.user = current_user
    g.plex = p

    if current_user is not None and hasattr(current_user, "locale") and current_user.locale not in ['de','en']:
        flash(_("You are useing an incomplete translation please help! %(link)s", link="https://www.transifex.com/projects/p/plexivity/"), "info")

    if not db.session.query(models.User).first() and not (request.url_rule.endpoint in ["setup", "static"]):
        return redirect(url_for("setup"))

@app.route("/")
@login_required
def index():
    #check for plex connection else redirect to settings page and show a error message!
    if not g.plex.test():
        # NOTE: Test2
        flash(_("Unable to connect to PMS. Please check your settings"), "error")
        return redirect(url_for("settings"))
    if config.SHOW_LIBRARY_STATS:
        stats=g.plex.libraryStats()
    else:
        stats = None
    return render_template('index.html', stats=stats, activity=g.plex.currentlyPlaying(), new=g.plex.recentlyAdded())

@app.route("/twitter")
def twitter():
    auth = tweepy.OAuthHandler("T4NRPcEtUrCEU58FesRmRtkdW", "zmpbytgPpSbro6RZcXsKgYQoz24zLH3vYZHOHAAs5j33P4eoRg",  "http://"+ request.environ["HTTP_HOST"] + "/auth/twitter")
    auth.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)
    try:
         if api.me().name:
             return redirect(url_for('index'))
    except tweepy.TweepError:
        pass

    redirect_url = auth.get_authorization_url()
    session["request_token"] = auth.request_token
    return redirect(redirect_url)

@app.route("/auth/twitter")
def auth_twitter():
    verifier = request.args.get('oauth_verifier')
    auth = tweepy.OAuthHandler("T4NRPcEtUrCEU58FesRmRtkdW", "zmpbytgPpSbro6RZcXsKgYQoz24zLH3vYZHOHAAs5j33P4eoRg")
    token = session["request_token"]
    auth.request_token = token
    config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET = auth.get_access_token(verifier)
    config.configval["TWITTER_ACCESS_TOKEN"] = config.TWITTER_ACCESS_TOKEN
    config.configval["TWITTER_ACCESS_TOKEN_SECRET"] = config.TWITTER_ACCESS_TOKEN_SECRET
    config.save_config(config.configval)
    return redirect(url_for('index'))

#reload stuff
@app.route("/load/activity")
@login_required
def activity():
    return render_template('include/activity.html', activity=g.plex.currentlyPlaying())

@app.route("/load/overview")
@login_required
def overview():
    return render_template('include/overview.html', stats=g.plex.libraryStats())

@app.route("/load/recentlyAdded")
@login_required
def recently_added():
    return render_template('include/recently_added.html', new=g.plex.recentlyAdded())

@app.route("/load/streaminfo/<id>")
@login_required
def streaminfo(id):
    item = db.session.query(models.Processed).filter(models.Processed.id == id).first()
    if item.platform == "Imported":
        return render_template('include/stream_info.html', id=item.id, xml=None)

    xml = helper.load_xml(item.xml)
    return render_template('include/stream_info.html', id=item.id, xml=xml)


def perform_some_search(queryset, user_input):
    return queryset.filter(
        db.or_(
            models.Processed.title.like('%'+user_input+'%'),
            models.Processed.user.like('%'+user_input+'%'),
            models.Processed.platform.like('%'+user_input+'%')
            )
        )

@app.route("/load/history")
@login_required
def jsonhistory():
    history = db.session.query(models.Processed)
    table = DataTable(request.args, models.Processed, history, [
        ("date", "time", lambda i: "{}".format(i.time.strftime('%Y/%m/%d')) if i.stopped else '<span class="orange">{}</span>'.format(_("Currently watching..."))),
        ("user", lambda i: '<a href="{0}" class="invert-link">{1}</a>'.format(url_for('user', name=i.user), i.user)),
        ("platform"),
        ("title", lambda i: u'<a class="invert-link" href="{0}">{1}</a>'.format(url_for('info', id=i.get_xml_value('ratingKey')), i.title)),
        ("type", lambda i: "{}".format(i.get_xml_value("type"))),
        ("streaminfo", lambda i: '<a href="#" data-link="{0}" class="orange" data-target="#streamModal" data-toggle="modal"><i class="glyphicon glyphicon glyphicon-info-sign"></i></a>'.format(url_for('streaminfo',id=i.id)) if i.platform != "Imported" else ''),
        ("time",lambda i: "{}".format(i.time.strftime('%H:%M'))),
        ("paused_counter", lambda i: "{} min".format(int(i.paused_counter)/60) if i.paused_counter else "0 min" ),
        ("stopped", lambda i: "{}".format(i.stopped.strftime('%H:%M')) if i.stopped else "n/a"),
        ("duration", lambda i: "{} min".format(int((((i.stopped - i.time).total_seconds() - (int(i.paused_counter or 0))) /60))) if i.stopped else "n/a"),
        ("completed", lambda i: '<span class="badge badge-warning">{}%</span>'.format(helper.getPercentage(i.get_xml_value("duration") if i.platform == "Imported" else i.get_xml_value("viewOffset"), i.get_xml_value("duration")))),
    ])
    table.searchable(lambda queryset, user_input: perform_some_search(queryset, user_input))

    return json.dumps(table.json())

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

    maxhourly = db.session.query(db.func.count(db.extract('hour', models.Processed.time)), models.Processed).group_by(db.extract('hour', models.Processed.time)).order_by(db.extract('hour', models.Processed.time).desc()).all()
    maxhourlyJSON = list()
    for hour in maxhourly:
        maxhourlyJSON.append({"y": hour[0], "x": hour[1].time.strftime("%H")})

    playperuser = db.session.query(db.func.count(models.Processed.title), models.Processed).filter(models.Processed.time >= datetime.datetime.now() - datetime.timedelta(days=30)).group_by(models.Processed.user).order_by(db.func.count(models.Processed.title).desc()).all()
    playperuserJSON = list()
    for play in playperuser:
        playperuserJSON.append({"y": play[0], "x": play[1].user})

    playperuserEver = db.session.query(db.func.count(models.Processed.title), models.Processed).group_by(models.Processed.user).order_by(db.func.count(models.Processed.title).desc()).all()
    playperuserEverJSON = list()
    for cplay in playperuserEver:
        playperuserEverJSON.append({"y": cplay[0], "x": cplay[1].user})

    return render_template('stats.html', hourly=hourlyJSON, daily=dailyJSON, monthly=monthlyJSON, maxhourly=maxhourlyJSON, userplays=playperuserJSON, userplaysalltime=playperuserEverJSON, title=_('Statistics'))


@app.route("/setup", methods=("GET", "POST"))
def setup():
    form = forms.ExtendedRegisterForm()
    if form.validate_on_submit():
        flash(_("User %(username)s created", username=form.email.data), "success")

        admin_role = user_datastore.find_or_create_role('admin')
        user_role = user_datastore.find_or_create_role('user')
        user = user_datastore.create_user(email=form.email.data, password=encrypt_password(form.password.data), locale=form.locale.data, active=1, roles=[admin_role, user_role])
        user_datastore.commit()
        login_user(user)
        return redirect(url_for('settings'))
    if not db.session.query(models.User).first():
        return render_template('setup.html', form=form, title=_('Setup'), data_dir=config.DATA_DIR)
    else:
        return redirect(url_for("importer"))

@app.route("/import", methods=("GET", "POST"))
@login_required
@roles_required('admin')
def importer():
    if not g.plex.test():
        flash(_("Unable to connect to PMS. Please check your settings"), "error")

    form = forms.PlexImportForm()
    if form.validate_on_submit():
        import threading
        importer = threading.Thread(target=helper.importFromPlex, args=(g.plex, db))
        importer.start()
        flash(_("Successfully started import of viewed Media from PMS"), "success")
        return  redirect(url_for('index'))
    return render_template('import.html', form=form, title=_("Import"), action_text=_('Import Media'))

@app.route("/charts")
@login_required
def charts():
    #all10 = db.session.query(models.Processed.count as count, models.Processed).group_by(models.Processed.title).order_by(db.func.count(models.Processed.title).desc()).limit(10)
    all10 = db.session.query(db.func.count(models.Processed.title), models.Processed).group_by(models.Processed.title).having(db.func.count(models.Processed.title) > 0).order_by(db.func.count(models.Processed.title).desc(), models.Processed.time.desc()).limit(10)
    movie10 = db.session.query(db.func.count(models.Processed.title), models.Processed).filter(db.or_(models.Processed.orig_title_ep == None, models.Processed.orig_title_ep == "")).group_by(models.Processed.title).having(db.func.count(models.Processed.title) > 0).order_by(db.func.count(models.Processed.title).desc(), models.Processed.time.desc()).limit(10)
    show_top10 = db.session.query(db.func.count(models.Processed.orig_title), models.Processed).group_by(models.Processed.orig_title).having(db.func.count(models.Processed.orig_title) > 0).order_by(db.func.count(models.Processed.orig_title).desc(), models.Processed.time.desc()).limit(10)
    ep_top10 = db.session.query(db.func.count(models.Processed.title), models.Processed).group_by(models.Processed.title).having(db.func.count(models.Processed.title) > 0).order_by(db.func.count(models.Processed.title).desc(), models.Processed.time.desc()).limit(10)

    return render_template('charts.html', all_top10=all10, movie_top10=movie10, show_top10=show_top10, ep_top10=ep_top10, title=_('Charts'))

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

    return render_template('info.html', info=info, history=views, parent=parent, episodes=episodes, title=_('Info'))


@app.route("/history")
@login_required
def history():
    return render_template('history.html', title=_('History'))

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
    if not config.CACHE_IMAGES:
        return g.plex.get_thumb_data(filename)
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
# @roles_required('admin')
@login_required
def users():
    users = db.session.query(db.func.count(models.Processed.user), models.Processed).group_by(models.Processed.user).all()
    return render_template('users.html', users=users, title=_('Users'))


@app.route('/user/<name>')
@login_required
def user(name):
    usr = db.session.query(models.Processed).filter(models.Processed.user == name == name).first()
    platform_plays = db.session.query(db.func.count(models.Processed.platform), models.Processed).filter(models.Processed.user == name).group_by(models.Processed.platform).all()
    recent = db.session.query(models.Processed).filter(models.Processed.user == name).order_by(models.Processed.time.desc()).limit(12)
    stats = helper.calculate_plays(db, models, name)
    history = db.session.query(models.Processed).filter(models.Processed.user == name).order_by(models.Processed.time.desc()).all()
    return render_template('user.html', stats=stats, platforms=platform_plays, recently=recent, history=history, user=usr, title=usr.user)

@app.route('/logs')
@login_required
@roles_required('admin')
def logs():
    f = open(os.path.join(config.DATA_DIR, "plexivity.log"), "r")
    content = f.readlines()
    f.close()
    log_content = reversed(content[-200:])
    return render_template('logs.html', log=log_content)

@app.route("/settings", methods=("GET", "POST"))
@login_required
@roles_required('admin')
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
        g.plex.update_settings(config.PMS_HOST, int(config.PMS_PORT))
   # p = False

    for x in form._fields:
        if x != "csrf_token":
            form[x].data = config.configval[x]

    return render_template('settings.html', form=form, title=_('Settings'), config=config)

@app.route("/test-notify")
@login_required
@roles_required('admin')
def notify():
    from app import notify
    info = {
        "ntype": "test"
    }
    if notify.notify(info):
        flash(_("Test notification successfully send"), "success")
    else:
        flash(_("unable to send test notification"), "error")

    return redirect(url_for("settings"))
