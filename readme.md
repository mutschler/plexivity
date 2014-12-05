#plexivity

plexivity is a simple to use WebApp for your Plex Media Server Statistics. It can be seen as an alternative for [plexWatch](https://github.com/ljunkie/plexWatch) with [plexWatchWeb](https://github.com/ecleese/plexWatchWeb/). It connects with your Plex Media Server and is able to notify you on activity.

Sadly plexWatch requires some native compiled 3rd Party extensions wich can not easyly be intalled on some systems (like Synology for example) so i decided to build my own app for that purpose.

you can find some Screenshots here: http://blog.raphaelmutschler.de/plexivity-0-9/

##Requirements:
* PMS 0.9.8.x +
* PlexPass subscription
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

plexivity still in development

Install virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/en/latest/index.html

    mkvirtualenv plexivity
    pip install -r requirements.txt
    python manage.py db upgrade
    python manage.py runserver

On default this will fire up a webserver on 127.0.0.1 and port 5000 if you like to change that, just give an host and port with -h and -p like this:

    python manage.py runserver -h 0.0.0.0 -p 12345

PS: i hardly recommend you to run it in development mode instead of useing the (still littlebit buggy) plexivitiy.py