from app import app
from app import helper, plex, config

from flask import url_for, render_template, g
import json

app.jinja_env.globals.update(helper=helper)


@app.route("/")
def index():
    #return url_for('static', filename=helper.playerImage("iPhone"))
    return render_template('index.html')


@app.route("/stats")
def stats():
    #return url_for('static', filename=helper.playerImage("iPhone"))
    return render_template('stats.html', stats=g.plex.libraryStats(), activity=g.plex.currentlyPlaying(), new=g.plex.recentlyAdded())


@app.route("/stats/activity")
def activity():
    #return url_for('static', filename=helper.playerImage("iPhone"))
    return render_template('activity.html', activity=g.plex.currentlyPlaying())


@app.route("/info/<id>")
def info(id):
    return render_template('info.html', info=g.plex.getInfo(id))
    return json.dumps(g.plex.getInfo(id))

@app.route("/login")
def login():
    pass


@app.route("/logout")
def logout():
    pass


@app.route("/settings")
def settings():
    pass