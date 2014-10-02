from app import app
from app import helper, plex, config

from flask import url_for, render_template, g, redirect, flash
from flask.ext.babel import gettext as _
import json

app.jinja_env.globals.update(helper=helper)


@app.route("/")
def index():
    #check for plex connection else redirect to settings page and show a error message!
    if not g.plex.status:
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

@app.route("/login")
def login():
    pass


@app.route("/logout")
def logout():
    pass


@app.route("/settings")
def settings():
    return render_template('index.html')