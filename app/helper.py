#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET
import logging
import datetime

from flask.ext.babel import gettext as _
from apscheduler.schedulers.background import BackgroundScheduler

from app import logger
from app import config, plex, notify, db, models
import pytz

sched_logger = logging.getLogger("apscheduler")
sched_logger.addHandler(logger.rotation)
sched_logger.setLevel(logging.DEBUG)
logger = logger.logger.getChild('helper')

def generateSSLCert():
    if not os.path.exists(os.path.join(config.DATA_DIR, 'plexivity.key')) or not os.path.exists(os.path.join(config.DATA_DIR, 'plexivity.crt')):
        logger.warning("plexivity was started with ssl support but no cert was found, trying to generating cert and key now")
        try:
            from OpenSSL import crypto, SSL
            from socket import gethostname

            
            # create a key pair
            k = crypto.PKey()
            k.generate_key(crypto.TYPE_RSA, 1024)
    
            # create a self-signed cert
            cert = crypto.X509()
            cert.get_subject().C = "US"
            cert.get_subject().ST = "plex land"
            cert.get_subject().L = "plex land"
            cert.get_subject().O = "plexivity"
            cert.get_subject().OU = "plexivity"
            cert.get_subject().CN = gethostname()
            cert.set_serial_number(1000)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(10*365*24*60*60)
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(k)
            cert.sign(k, 'sha1')
    
            open(os.path.join(config.DATA_DIR, 'plexivity.crt'), "wt").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
            open(os.path.join(config.DATA_DIR, 'plexivity.key'), "wt").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
            logger.info("ssl cert and key generated and saved to: %s" % config.DATA_DIR)
        except:
            logger.error("unable to generate ssl key and cert")

def startScheduler():
    db.create_all()
    #create default roles!
    if not db.session.query(models.Role).filter(models.Role.name == "admin").first():
        admin_role = models.Role(name='admin', description='Administrator Role')
        user_role = models.Role(name='user', description='User Role')
        db.session.add(admin_role)
        db.session.add(user_role)
        db.session.commit()
        
    try:
        import tzlocal

        tz = tzlocal.get_localzone()
        logger.info("local timezone: %s" % tz)
    except:
        tz = None

    if not tz or tz.zone == "local":
        logger.error('Local timezone name could not be determined. Scheduler will display times in UTC for any log'
                 'messages. To resolve this set up /etc/timezone with correct time zone name.')
        tz = pytz.utc
    #in debug mode this is executed twice :(
    #DONT run flask in auto reload mode when testing this!
    scheduler = BackgroundScheduler(logger=sched_logger, timezone=tz)
    scheduler.add_job(notify.task, 'interval', seconds=config.SCAN_INTERVAL, max_instances=1,
                      start_date=datetime.datetime.now(tz) + datetime.timedelta(seconds=2))
    scheduler.start()
    sched = scheduler
    #notify.task()


def importFromPlex(plex, db):
    logger.info("Importing viewed Movies from PMS")
    viewedMovies = plex.getViewedMovies()

    for movie in viewedMovies:
        if db.session.query(models.Processed).filter(models.Processed.session_id.like("%" + movie.get('key') + "%")).first():
            logger.debug("skipping import of '%s' because there already is a entry in database" % movie.get("title"))
            continue

        el = models.Processed()
        el.time = datetime.datetime.fromtimestamp(int(movie.get("lastViewedAt"))) - datetime.timedelta(seconds=(int(movie.get("duration")) / 1000))
        el.stopped = datetime.datetime.fromtimestamp(int(movie.get("lastViewedAt")))
        el.user = config.IMPORT_USERNAME
        el.platform = "Imported"
        el.title = movie.get("title")
        el.orig_title = movie.get("title")
        el.year = movie.get("year")
        el.summary = movie.get("summary")
        el.notified = 1
        el.progress = 100
        el.duration = movie.get("duration")
        el.xml = xml_to_string(movie)
        el.session_id = "im_%s_pt" % movie.get('key') 
        db.session.merge(el)
        db.session.commit()

    logger.info("Importing viewed Episodes from PMS")
    for episode in plex.getViewedEpisodes():
        eptitle = "%s - %s - s%02de%02d" % (episode.get("grandparentTitle"), episode.get("title"), int(episode.get('parentIndex')), int(episode.get('index')))

        if db.session.query(models.Processed).filter(models.Processed.session_id.like("%" + episode.get('key') + "%")).first():
            logger.debug("skipping import of '%s' because there already is a entry in database" % eptitle)
            continue

        el = models.Processed()
        el.time = datetime.datetime.fromtimestamp(int(episode.get("lastViewedAt"))) - datetime.timedelta(seconds=(int(episode.get("duration")) / 1000))
        el.stopped = datetime.datetime.fromtimestamp(int(episode.get("lastViewedAt")))
        el.user = config.IMPORT_USERNAME
        el.platform = "Imported"
        el.title = eptitle
        el.orig_title = episode.get("grandparentTitle")
        el.orig_title_ep = episode.get("title")
        el.year = episode.get("year")
        el.summary = episode.get("summary")
        el.episode = episode.get('index')
        el.season = episode.get('parentIndex')
        el.notified = 1
        el.progress = 100
        el.duration = episode.get("duration")
        el.xml = xml_to_string(episode)
        el.session_id = "im_%s_pt" % episode.get('key') 
        db.session.merge(el)
        db.session.commit()
        
    return True


def calculate_plays(db, models, username):
    to_return = list()
    today = db.session.query(models.Processed).filter(models.Processed.user == username).filter(
        models.Processed.stopped >= datetime.datetime.now() - datetime.timedelta(hours=7))
    week = db.session.query(models.Processed).filter(models.Processed.user == username).filter(
        models.Processed.stopped >= datetime.datetime.now() - datetime.timedelta(days=1))
    month = db.session.query(models.Processed).filter(models.Processed.user == username).filter(
        models.Processed.stopped >= datetime.datetime.now() - datetime.timedelta(days=30))
    alltime = db.session.query(models.Processed).filter(models.Processed.user == username)

    today_time = datetime.timedelta()
    for row in today.all():
        today_time += datetime.timedelta(seconds=row.duration / 1000)
        # if row.paused_counter and row.stopped:
        #     today_time += row.stopped - row.time - datetime.timedelta(seconds=row.paused_counter)
        # elif row.stopped:
        #     today_time += row.stopped - row.time

    week_time = datetime.timedelta()
    for row in week.all():
        week_time += datetime.timedelta(seconds=row.duration / 1000)
        # if row.paused_counter and row.stopped:
        #     week_time += row.stopped - row.time - datetime.timedelta(seconds=row.paused_counter)
        # elif row.stopped:
        #     week_time += row.stopped - row.time

    month_time = datetime.timedelta()
    for row in month.all():
        month_time += datetime.timedelta(seconds=row.duration / 1000)
        # if row.paused_counter and row.stopped:
        #     month_time += row.stopped - row.time - datetime.timedelta(seconds=row.paused_counter)
        # elif row.stopped:
        #     month_time += row.stopped - row.time

    alltime_time = datetime.timedelta()
    for row in alltime.all():
        alltime_time += datetime.timedelta(seconds=row.duration / 1000)
        # if row.paused_counter and row.stopped:
        #     alltime_time += row.stopped - row.time - datetime.timedelta(seconds=row.paused_counter)
        # elif row.stopped:
        #     alltime_time += row.stopped - row.time

    to_return.append({"plays": today.count(), "time": today_time, "name": _("Today")})
    to_return.append({"plays": week.count(), "time": week_time, "name": _("Last Week")})
    to_return.append({"plays": month.count(), "time": month_time, "name": _("Last Month")})
    to_return.append({"plays": alltime.count(), "time": alltime_time, "name": _("All Time")})

    return to_return


def statistics():
    pass


def date_timestamp(date):
    import time

    return time.mktime(date.timetuple())


def load_xml(string):
    xml = ET.fromstring(string)
    return xml


def xml_to_string(xml):
    try:
        return xml.tostring()
    except:
        return ET.tostring(xml)


def getPercentage(viewed, duration):
    if not viewed or not duration:
        return 0

    percent = "%2d" % ((float(viewed) / float(duration)) * 100)

    if int(percent) >= 90:
        return 100
    return percent


def cache_file(filename, plex):
    cache_dir = os.path.join(config.DATA_DIR, "cache")
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    cache_file = os.path.join(cache_dir, filename)
    if not os.path.exists(os.path.split(cache_file)[0]):
        os.makedirs(os.path.split(cache_file)[0])
    img_data = plex.get_thumb_data(filename)
    if img_data:
        f = open(cache_file + ".jpg", "wb")
        f.write(img_data)
        f.close()
        return True

    return False


def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime

    now = datetime.now()
    if float(time):
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    else:
        diff = now - now

    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return _("just now")
        if second_diff < 60:
            return _("%(int)s seconds ago", int=second_diff)
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return _("%(int)s minutes ago", int=second_diff / 60)
        if second_diff < 7200:
            return _("an hour ago")
        if second_diff < 86400:
            return _("%(int)s hours ago", int=second_diff / 3600)
    if day_diff == 1:
        return _("Yesterday")
    if day_diff < 7:
        return _("%(int)s days ago", int=day_diff)
    if day_diff < 31:
        return _("%(int)s weeks ago", int=day_diff / 7)
    if day_diff < 365:
        return _("%(int)s months ago", int=day_diff / 30)
    return _("%(int)s years ago", int=day_diff / 365)


def notifyer():
    ### onyl basic tests here
    # TODO: move this to a extra file and include DB support!
    p = plex.Server(config.PMS_HOST, config.PMS_PORT)
    sessions = p.currentlyPlaying()

    for session in sessions:
        if session.get("type") == "episode":
            title = '%s - "%s"' % (session.get("grandparentTitle"), session.get("title"))
        else:
            title = session.get("title")

        offset = int(session.get("viewOffset")) / 1000 / 60
        username = session.find("User").get("title")
        platform = session.find("Player").get("platform")
        product = session.find("Player").get("product")
        player_title = session.find("Player").get("product")

        if session.find("Player").get("state") == "paused":
            message = config.PAUSE_MESSAGE % {"username": username, "platform": platform, "title": title,
                                              "product": product, "player_title": player_title, "offset": offset}
        elif session.find("Player").get("state") == "playing":
            message = config.START_MESSAGE % {"username": username, "platform": platform, "title": title,
                                              "product": product, "player_title": player_title, "offset": offset}
        else:
            message = config.STOP_MESSAGE % {"username": username, "platform": platform, "title": title,
                                             "product": product, "player_title": player_title, "offset": offset}

        if config.NOTIFY_PUSHOVER and message:
            from app.providers import pushover

            pushover.send_notification(message)


def playerImage(platform):
    if platform == "Roku":
        return "images/platforms/roku.png"
    elif platform == "Apple TV":
        return "images/platforms/appletv.png"
    elif platform == "Firefox":
        return "images/platforms/firefox.png"
    elif platform == "Chromecast":
        return "images/platforms/chromecast.png"
    elif platform == "Chrome":
        return "images/platforms/chrome.png"
    elif platform == "Android":
        return "images/platforms/android.png"
    elif platform == "Nexus":
        return "images/platforms/android.png"
    elif platform == "iPad":
        return "images/platforms/ios.png"
    elif platform == "iPhone":
        return "images/platforms/ios.png"
    elif platform == "iOS":
        return "images/platforms/ios.png"
    elif platform == "Plex Home Theater":
        return "images/platforms/pht.png"
    elif platform == "Linux/RPi-XBMC":
        return "images/platforms/xbmc.png"
    elif platform == "Safari":
        return "images/platforms/safari.png"
    elif platform == "Internet Explorer":
        return "images/platforms/ie.png"
    elif platform == "Unknown Browser":
        return "images/platforms/default.png"
    elif platform == "Windows-XBMC":
        return "images/platforms/xbmc.png"
    elif platform == "XboxOne":
        return "images/platforms/xbox1.png"
    elif platform == "Imported":
        return "images/platforms/pms.png"
    else:
        return "images/platforms/default.png"
