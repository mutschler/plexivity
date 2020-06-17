[![License](http://img.shields.io/:license-gpl3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0.html)

## Project no longer maintained 
if you are looking for a replacement checkout [Tautulli](https://github.com/Tautulli/Tautulli)

[![Donate](https://www.paypalobjects.com/de_DE/DE/i/btn/btn_donate_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=296X2XQXKQDD6) 

# plexivity

plexivity is a simple to use WebApp for your Plex Media Server Statistics. It can be seen as an alternative for [plexWatch](https://github.com/ljunkie/plexWatch) with [plexWatchWeb](https://github.com/ecleese/plexWatchWeb/). It connects with your Plex Media Server and is able to notify you on activity.

Sadly plexWatch requires some native compiled 3rd Party extensions wich can not easyly be intalled on some systems (like Synology for example) so i decided to build my own app for that purpose.

you can find some Screenshots here: http://blog.raphaelmutschler.de/plexivity-0-9/

## Requirements:
* PMS 0.9.8.x +
* PlexPass subscription
* Python 2.7

## Features

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
- [Flask-Security](https://github.com/mattupstate/flask-security)
- [Flask-SQLAlchemy](https://github.com/mitsuhiko/flask-sqlalchemy)
- [Flask-Babel](https://github.com/mitsuhiko/flask-babel/)
- [Flask-Script](https://github.com/smurfix/flask-script)
- [Flask-Migrate](https://github.com/miguelgrinberg/Flask-Migrate)
- [Flask-Mail](https://github.com/mattupstate/flask-mail/)
- [Flask-Admin](https://github.com/mrjoes/flask-admin/)
- [APScheduler](https://bitbucket.org/agronholm/apscheduler/)
- [requests](https://github.com/kennethreitz/requests)
- [Bootstrap](http://getbootstrap.com/)
- [Datatables](https://github.com/orf/datatables)

##Data Path

Data direcotrys can be found in this locations:

**Windows**

`C:\Users\yourname\AppData\Roaming\plexivity`

or

`C:\Documents and Settings\yourname\Application Data\plexivity`

**OSX**

`~/Library/Applications Settings/plexivity`

**FreeBSD**

`/usr/local/plexivity/data`

**Linux**

`~/.plexivity`

if you like to use a different Direcotry you can set one by useing the `PLEXIVITY_DATA` environment variable


### production install:

	pip install -r requirements.txt
	python plexivity.py 

you can start plexivity as a deamon by adding `--deamon` to the command above


### SSL Support:

plexivity supports SSL (since version 0.9.8) but to keep up with some environments which do not ship with openssl support out of the box you'll have to install `pyopenssl` manually by running `pip install pyopenssl` and change the `USE_SSL` value in the config file manually to `1`

If you like to provide a specific cert/key combination make sure to copy `plexivity.crt` and `plexivity.key` to your **Data Path** (see above). When those files are missing, plexivity will create them for you when you first start it with SSL support.

If `pyopenssl` is not installed it will automatically fallback to non SSL mode


### development install:

plexivity still in development

Install virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/en/latest/index.html

    mkvirtualenv plexivity
    pip install -r requirements.txt
    python manage.py db upgrade
    python manage.py runserver

On default this will fire up a webserver on 127.0.0.1 and port 5000 if you like to change that, just give an host and port with -h and -p like this:

    python manage.py runserver -h 0.0.0.0 -p 12345

you can find a short development installation video here:
https://asciinema.org/a/12778
