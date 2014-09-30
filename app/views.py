from app import app
from app import helper

from flask import url_for, render_template

app.jinja_env.globals.update(helper=helper)

@app.route("/")
def index():
	#return url_for('static', filename=helper.playerImage("iPhone"))
	return render_template('index.html')

@app.route("/login")
def login():
	pass

@app.route("/logout")
def logout():
	pass

@app.route("/settings")
def settings():
	pass