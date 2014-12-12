#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db

from flask.ext.security import UserMixin, RoleMixin

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255))
    locale = db.Column(db.String(2), default="en")
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String())
    current_login_ip = db.Column(db.String())
    login_count = db.Column(db.Integer())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def is_active(self):
        return self.active

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def __unicode__(self):
        return self.email

    def __repr__(self):
        return '<User %r %s %s>' % (self.id, self.email, self.locale)


class Processed(db.Model):
    __tablename__ = "processed"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Text)
    time = db.Column(db.DateTime)
    user = db.Column(db.Text)
    platform = db.Column(db.Text)
    title = db.Column(db.Text)
    orig_title = db.Column(db.Text)
    orig_title_ep = db.Column(db.Text)
    episode = db.Column(db.Integer)
    season = db.Column(db.Integer)
    year = db.Column(db.Text)
    rating = db.Column(db.Text)
    genre = db.Column(db.Text)
    summary = db.Column(db.Text)
    notified = db.Column(db.Integer)
    stopped = db.Column(db.DateTime)
    paused = db.Column(db.DateTime)
    paused_counter = db.Column(db.Integer)
    xml = db.Column(db.Text)
    ip_address = db.Column(db.Text)
    duration = db.Column(db.Integer)
    view_offset = db.Column(db.Integer)
    progress = db.Column(db.Integer) # (view_offset / duration) * 100 helper.getPercentage()


class RecentlyAdded(db.Model):
    __tablename__ = "recently_added"

    item_id = db.Column(db.Text, primary_key=True)
    time = db.Column(db.DateTime)
    debug = db.Column(db.Text)
    file = db.Column(db.Integer)
    twitter = db.Column(db.Integer)
    growl = db.Column(db.Integer)
    prowl = db.Column(db.Integer)
    GNTP = db.Column(db.Integer)
    EMAIL = db.Column(db.Integer)
    pushover = db.Column(db.Integer)
    boxcar = db.Column(db.Integer)
    boxcar_v2 = db.Column(db.Integer)


class Grouped(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Text)
    time = db.Column(db.DateTime)
    user = db.Column(db.Text)
    platform = db.Column(db.Text)
    title = db.Column(db.Text)
    orig_title = db.Column(db.Text)
    orig_title_ep = db.Column(db.Text)
    episode = db.Column(db.Integer)
    season = db.Column(db.Integer)
    year = db.Column(db.Text)
    rating = db.Column(db.Text)
    genre = db.Column(db.Text)
    summary = db.Column(db.Text)
    notified = db.Column(db.Integer)
    stopped = db.Column(db.DateTime)
    paused = db.Column(db.DateTime)
    paused_counter = db.Column(db.Integer)
    xml = db.Column(db.Text)
    ip_address = db.Column(db.Text)
