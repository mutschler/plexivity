from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255))

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username


# class History(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(255))
#     titleSort = db.Column(db.String(255))
#     duration = db.Column(db.String(255))
#     type = db.Column(db.String(120))
#     plexID = db.Column(db.Integer, unique=True)
#     progress = db.Column(db.Integer)
#     platform = db.Column(db.String(255))
#     product = db.Column(db.String(255))
#     playerTitle = db.Column(db.String(255))
#     user_name = db.Column(db.Integer(255))
#     user_thumb = db.Column(db.String(255))
#     timestamp = db.Column(db.Integer)

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
