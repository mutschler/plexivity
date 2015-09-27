# Changelog

## dev (unreleased)


## 0.9.7 (2015-09-27)

### new

* config value for import username. [Raphael Mutschler]

* option to import viewed episodes from PMS. [Raphael Mutschler]

* option to import last plays from Plex Media Server. [Raphael Mutschler]

* options for custom scripts (see #10) [Raphael Mutschler]

### chg

* add import as setup step. [Raphael Mutschler]

* update with latest translations. [Raphael Mutschler]

* change importer to run in background. [Raphael Mutschler]

### fix

* history not updating (should fix #47) [Raphael Mutschler]

* start scheduler on startup (no more need to open browser after startup) [Raphael Mutschler]

* use correct media duration for user stats. [Raphael Mutschler]

* history rendering for imported media. [Raphael Mutschler]


## 0.9.6 (2015-06-05)

### new

* stats for playback by user (all time) [Raphael Mutschler]

* support for setting reverse proxy. [Raphael Mutschler]

* options for excluding and user name mapping in web interface. [Raphael Mutschler]

### fix

* update with latest translations. [Raphael Mutschler]

* setup and settings url's for reverse proxy usage. [Raphael Mutschler]

* json form validation. [Raphael Mutschler]

* enable search function in history. [Raphael Mutschler]


## 0.9.5 (2015-05-08)

### new

* option to exclude sections from logging and notify. [Raphael Mutschler]

* twitter notifications (fixes #38) [Raphael Mutschler]

* monthly plays per user in statistics view (fixes #36) [Raphael Mutschler]

* option for recently added notification (fixes #20) [Raphael Mutschler]

* translations for 'es' and 'nl' (incomplete translations) [Raphael Mutschler]

* option to provide real names for usernames (fixes: #34) [Raphael Mutschler]

* basic api functionality for user and history. [Raphael Mutschler]

* add password recovery function. [Raphael Mutschler]

* display help for notification formatting values. [Raphael Mutschler]

* render SMTP_PASSWORD as password field (appends #30) [Raphael Mutschler]

* option to send a test notification fixes #11. [Raphael Mutschler]

* option to change PORT in Webinterface. [Raphael Mutschler]

### chg

* use server side processing for history view. [Raphael Mutschler]

* remove DATA_DIR from config. [Raphael Mutschler]

* load available locales dynamically on startup. [Raphael Mutschler]

### fix

* stream modal in standalone mode. [Raphael Mutschler]

* add password reset templates. [Raphael Mutschler]

* add missing .mo files. [Raphael Mutschler]

* update with latest transfex translations. [Raphael Mutschler]

* admin view stuff. [Raphael Mutschler]

* style fixes and added isotope (fix #6) [Raphael Mutschler]

* append args when db is created !typo. [Raphael Mutschler]


## 0.9.3 (2014-12-05)

### new

* show data dir info on setup. [Raphael Mutschler]

* french translation (60%) [Raphael Mutschler]

* admin interface with search history function. [Raphael Mutschler]

### chg

* Data is now saved in system default data dirs or PLEXIVITY_DATA env variable. [Raphael Mutschler]

* update translations to latest version. [Raphael Mutschler]

* add admin view to delete History entries and cached files. [Raphael Mutschler]

### fix

* time calculation for sheduler when using utc. [Raphael Mutschler]

* timezone detection error and &quot;local&quot; timezone fallback to UTC. [Raphael Mutschler]

* startup script. [Raphael Mutschler]


## 0.9.2 (2014-11-12)

### new

* resume option for stopped and resumed plays (in less than 24 hours) [Raphael Mutschler]

### chg

* chg: updated requirements @dev. [Raphael Mutschler]

* added media type to history view. [Raphael Mutschler]

* update translation files. [Raphael Mutschler]

* activate notification types on settings page. [Raphael Mutschler]


## 0.9.1 (2014-10-28)

### new

* option for resume notification and custom resume message (fix #9) [Raphael Mutschler]

### chg

* include title of current page. [Raphael Mutschler]

### fix

* settings option for resume string. [Raphael Mutschler]

* default notification strings. [Raphael Mutschler]


## 0.9 (2014-10-21)

### new

* option to disable library stats/overview on frontpage. [Raphael Mutschler]

* plexivity options to daemonize the app. [Raphael Mutschler]

* plexivity.py to for easy server starting. [Raphael Mutschler]

* added config value for image cacheing. [Raphael Mutschler]

* added rgb support to hue.convert_color function. [Raphael Mutschler]

* locale db field for user. [Raphael Mutschler]

### chg

* console logging only in debug mode. [Raphael Mutschler]

* added option to select locale on setup. [Raphael Mutschler]

* ajax load for recently added. [Raphael Mutschler]

### fix

* user play calculation for non stopped items. [Raphael Mutschler]

* order max hourly plays by hour. [Raphael Mutschler]


