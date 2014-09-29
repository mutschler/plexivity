#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask("plexivity")
# app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plexivity.db'
db = SQLAlchemy(app)

from app import models, views