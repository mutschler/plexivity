#plexWatch

plexWatch aims to be a simple alternative for (plexWatch)[gizhub link] which i sadly was not able to get running on my Synology due to some 3rd Party dependencies which need to be compiled natively.

##Features

* support for plexWatch database
* adds a nice web interface
* user login
* fully locale support (open for translations)

##Resources

XYZ was heavy inspired by plexWatch and plexWatchWeb and could be descibed as a merge of those two apps in one single python app
i've tried to modulate my database and settings stuff as close to the latest plexWatch Version (0.3.1) but maybe some things will change in the Future.

XYZ makes use of those Projects/Librarys:

- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-Babel
- Flask-Script
- Flask-Migrate
- Flask-Mail
- Flask-Bcrypt
- Flask-Themes

- APScheduler

- towbar (boxcar Push)
-