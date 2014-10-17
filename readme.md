#plexivity

plexivity is a simple alternative for [plexWatch](https://github.com/ljunkie/plexWatch). It connects with your Plex Media Server and is able to notify you on activity. Sadly plexWatch requires some native compiled 3rd Party extensions wich can not easyly be intalled on some systems (like Synology for example) so i decided to build my own app for that purpose.

##Requirements:
* PMS 0.9.8.x +
* PlexPass subscription ( everything but recently added content )
* Python 2.7

##Features

* easy web setup guide
* login protected web interface
* notifications for watching, stopped and pause
* fully localisation support [help translate plexivity](https://www.transifex.com/projects/p/plexivity/)
* customizable notification messages

## Supportet Notification Providers

* Boxcar (v2)
* Pushover
* Pushbullet
* Mail
* Phillips Hue (currently in alpha/development)

##Resources

plexivity uses the following Projects/Librarys:

- [Flask](http://flask.pocoo.org/)
- [Flask-Login](https://github.com/maxcountryman/flask-login)
- [Flask-SQLAlchemy](https://github.com/mitsuhiko/flask-sqlalchemy)
- [Flask-Babel](https://github.com/mitsuhiko/flask-babel/)
- [Flask-Script](https://github.com/smurfix/flask-script)
- [Flask-Migrate](https://github.com/miguelgrinberg/Flask-Migrate)
- [Flask-Mail](https://github.com/mattupstate/flask-mail/)
- [APScheduler](https://bitbucket.org/agronholm/apscheduler/)
- [requests](https://github.com/kennethreitz/requests)
- [Bootstrap](http://getbootstrap.com/)

### development install:

plexivity is currently still in early development

Install virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/en/latest/index.html


    mkvirtualenv plexivity
    pip install -r requirements.txt
    python manage.py db upgrade
    python manage.py runserver