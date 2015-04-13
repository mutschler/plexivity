#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app.logger import logger
from app import config, plex, models, db

import xml.etree.ElementTree as ET

import datetime

logger = logger.getChild('notify')

def task():
    p = plex.Server(config.PMS_HOST, config.PMS_PORT)

    live = p.currentlyPlaying()
    started = get_started()
    playing = dict()

    recentlyAdded = p.recentlyAdded()

    if len(recentlyAdded):
        logger.debug("processing recently added media")

    for x in recentlyAdded:
        check = db.session.query(models.RecentlyAdded).filter(models.RecentlyAdded.item_id == x.get("ratingKey")).first()
        if check:
            logger.debug("already notified for recently added '%s'" % check.title)
            continue

        if x.get("type") == "season" or x.get("type") == "epsiode":
            fullseason = p.episodes(x.get("ratingKey"))
            for ep in fullseason:
                if x.get("addedAt") == ep.get("addedAt"):
                    xml = p.getInfo(ep.get("ratingKey")).find("Video")
        else:
            xml = p.getInfo(x.get('ratingKey')).find("Video")

        if not xml:
            logger.error("error loading xml for recently added entry")
            continue

        info = info_from_xml(xml, "recentlyadded", 1, 1, 0)
        info["added"] = datetime.datetime.fromtimestamp(float(x.get("addedAt"))).strftime("%Y-%m-%d %H:%M")

        if notify(info):
            logger.info(u"adding %s to recently added table" % info["title"])
            new = models.RecentlyAdded()
            new.item_id = x.get("ratingKey")
            new.time = datetime.datetime.now()
            new.filename = xml.find("Media").find("Part").get("file")
            new.title = info["title"]
            new.debug = "%s" % info
            db.session.merge(new)
            db.session.commit()

    if not len(live):
        logger.debug("seems like nothing is currently played")

    for session in live:
        logger.debug(session)
        userID = session.find('User').get('id')
        if not userID:
            userID = "Local"

        db_key = "%(id)s_%(key)s_%(userid)s" % { "id": session.get('sessionKey'), "key": session.get('key'), "userid": userID }
        playing[db_key] = 1

    did_unnotify = 0
    un_done = get_unnotified()

    if un_done:
        logger.debug("processing unnitified entrys")

        for k in un_done:
            start_epoch = k.time
            stop_epoch = k.stopped
            if not stop_epoch:
                stop_epoch = datetime.datetime.now()

            ntype = "stop"
            if k.session_id in playing:
                ntype = "start"

            paused = get_paused(k.session_id)
            info = info_from_xml(k.xml, ntype, start_epoch, stop_epoch, paused)

            logger.debug(info)

            logger.debug("sending notification for: %s : %s" % (info["user"], info["orig_title_ep"]))

            #TODO: fix this.... for now just dont notify again!
            if notify(info):
                k.notified = 1

            #make sure we have a stop time if we are not playing this anymore!
            if ntype == "stop":
                k.stopped = stop_epoch
            db.session.merge(k)
            set_notified(k.session_id)

    else:
        did_unnotify = 1

    ## notify stopped
    ## redo this! currently everything started is set to stopped?
    if did_unnotify:
        logger.info("processing recently started and checking for stopped")
        started = get_started()
        for k in started:
            logger.debug("checking if %s is in playling list" % k.session_id)
            if not k.session_id in playing:
                logger.debug("%s is stopped!" % k.session_id)
                start_epoch = k.time
                stop_epoch = datetime.datetime.now()

                xml = ET.fromstring(k.xml)
                xml.find("Player").set('state', 'stopped')
                process_update(xml, k.session_id)

                paused = get_sec_paused(k.session_id)
                info = info_from_xml(k.xml, "stop", start_epoch, stop_epoch, paused)
                k.stopped = datetime.datetime.now()
                k.paused = None
                k.notified = 0

                #set_stopped(started[k.session_id, stop_epoch)
                #https://github.com/ljunkie/plexWatch/blob/master/plexWatch.pl#L552

                info["decoded"] = 1
                if notify(info):
                    k.notified = 1
                db.session.merge(k)
                db.session.commit()

    ## notify start/now playing
    logger.debug("processing live content")
    was_started = dict()
    for k in live:

        if k.get('type') == "clip":
            logger.info("Skipping Video-Clip like trailers, specials, scenes, interviews etc..")
            continue

        start_epoch = datetime.datetime.now()
        stop_epoch = "" #not stopped yet
        xml_string = ET.tostring(k)
        info = info_from_xml(k, "start", start_epoch, stop_epoch, 0)
        info["decoded"] = 1

        logger.debug(info)

        userID = info["userID"]
        if not userID:
            userID = "Local"

        db_key = "%(id)s_%(key)s_%(userid)s" % { "id": k.get('sessionKey'), "key": k.get('key'), "userid": userID }

        logger.debug("plex returned a live element: %s " % db_key)
        ## ignore content already been notified

        #TODO: get_startet should return a dict accessable by db_key
        #so we can check: if x in startet: check for change, if not mark as started now

        #first go through all started stuff and check for status change
        if started:
            logger.debug("we still have not stopped entrys in our database")
            for x in started:
                logger.debug("processing entry %s " % x.session_id)
                state_change = False

                if x.session_id == db_key:
                    logger.debug("that was a match! check for status changes")
                    #already in database only check for status changes!
                    state_change = process_update(k, db_key)
                    was_started[db_key] = x

                if state_change:
                    info["ntype"] = state_change
                    logger.debug("%s: %s: state changed [%s] notify called" % (info["user"], info["title"], info["state"]))
                    notify(info)

        #also check if there is a element in the db which may be a resumed play from up to 24 hours ago

        if not db_key in was_started:
            logger.debug("trying to search for similar plays which stopped in the last 24 hours")
            view_offset = k.get("viewOffset")
            max_time = datetime.datetime.now() - datetime.timedelta(hours=24)
            like_what = "%" + k.get('key') + "_" + userID
            restarted = db.session.query(models.Processed).filter(models.Processed.session_id.like(like_what)).filter(models.Processed.time > max_time).filter(models.Processed.view_offset <= view_offset).filter(models.Processed.stopped != None).first()

            if restarted:
                logger.debug("seems like someone repeated an stopped play, updating db key from %s to %s" % (restarted.session_id, db_key))
                restarted.session_id = db_key
                restarted.stopped = None
                db.session.commit()
                state_change = process_update(k, db_key)
                was_started[db_key] = restarted
                info["ntype"] = "resume"
                notify(info)

        #if still not processed till now, its a new play!
        logger.debug("we got those entrys which already where in the database: %s " % was_started)
        if not db_key in was_started:
            logger.info("seems like this is a new entry: %s" % db_key)
            #unnotified insert to db and notify
            process_start(xml_string, db_key, info)
            if notify(info):
                set_notified(db_key)

def set_notified(db_key):
    logger.debug("setting %s to notified" % db_key)
    res = get_from_db(db_key)
    res.notified = 1
    db.session.merge(res)
    db.session.commit()

def process_start(xml_string, db_key, info):
    new = models.Processed()
    new.session_id = db_key
    new.title = info["title"]
    new.platform = info["platform"]
    new.user = info["orig_user"]
    new.orig_title = info["orig_title"]
    new.orig_title_ep = info["orig_title_ep"]
    new.duration = info["raw_length"]
    new.view_offset = info["viewOffset"]
    #new.genre = info["genre"]
    new.episode = info["episode"]
    new.season = info["season"]
    new.summary = info["summary"]
    new.rating = info["rating"]
    new.year = info["year"]
    new.progress = info["progress"]
    new.ratingKey = info["ratingKey"]
    new.parentRatingKey = info["parentRatingKey"]
    new.grandparentRatingKey = info["grandparentRatingKey"]
    new.time = datetime.datetime.now()
    new.xml = xml_string
    db.session.add(new)
    db.session.commit


def set_stopped(session_id, stop_epoch):
    if session_id:
        time = datetime.datetime.now()
        res = db.session.query(models.Processed).filter(models.Processed.session_id == session_id).first()
        res.stopped = time
        res.paused = None
        res.notified = 0
        db.session.commit()
    #https://github.com/ljunkie/plexWatch/blob/master/plexWatch.pl#L1636

def get_sec_paused(session_id):
    result = get_from_db(session_id)
    total = 0
    if result:
        total = result.paused_counter
        if result.paused and not result.stopped:
            total = datetime.datetime.now() + datetime.timedelta(seconds=result.paused)

    return total

def get_from_db(session_id):
    logger.debug("loading database entry for %s" % session_id)
    return db.session.query(models.Processed).filter(models.Processed.session_id == session_id).first()

def process_update(xml, session_id):
    #xml = ET obj
    z, sess, key = session_id.split("_")

    # check for valid xml
    if not xml.get("title"):
        return False
    if not xml.get("key"):
        return False

    status_change = False

    if session_id:

        ## get paused status -- needed for real time watched
        extra = ""
        p_counter = 0

        state = xml.find("Player").get("state")
        if "buffering" in state:
            state = "playing"

        p = db.session.query(models.Processed).filter(models.Processed.session_id == session_id).first()
        p_counter = p.paused_counter
        if not p_counter:
            p_counter = 0

        p_epoch = p.paused
        if p_epoch:
            prev_state = "paused"
        else:
            prev_state = "playing"

        if state and prev_state != state:
            #status_change = 1
            logger.debug("Video State: %s [prev: %s]" % (state, prev_state))

        cur = db.session.query(models.Processed).filter(models.Processed.session_id == session_id).first()

        now = datetime.datetime.now()
        if state and "paused" in state:
            if not p_epoch:
                extra = "%s, paused = %s" % (extra, now)
                logger.debug("Marking as Paused on %s [%s]" % (now, now))
                status_change = "pause"
                cur.paused = now
            else:
                p_counter += (now - p_epoch).total_seconds() #debug display no update!
                logger.debug("Already marked as Paused on %s" % p_epoch)

        else:
            if p_epoch:
                sec = (now - p_epoch).total_seconds()
                p_counter += sec
                extra = "%s,paused = null" % extra
                extra = "%s,paused_counter = %s" % (extra, p_counter)
                logger.debug("removeing Paused state and setting paused counter to %s seconds [this duration %s sec]" % ( p_counter, sec ) )
                status_change = "resume"
                cur.paused = None
                cur.paused_counter = p_counter

        logger.debug("total paused duration: %s [p_counter seconds]" % p_counter)

        cur.xml = ET.tostring(xml)
        db.session.merge(cur)
        db.session.commit()

    return status_change

def notify(info):

    if "orig_user" in info and info["orig_user"] in config.EXCLUDE_USERS:
        logger.info("'%s' is set as an EXCLUDE_USER, i'm not sending a notification!" % info["orig_user"])
        return True

    #notify all providers with the given stuff...
    logger.debug("notify called with args: %s" % info)

    if info["ntype"] == "recentlyadded" and config.NOTIFY_RECENTLYADDED:
        try:
            message = config.RECENTLYADDED_MESSAGE % info
        except KeyError:
            logger.error("Unable to map info to your recently added notification string. Please check your settings!")
    elif info["ntype"] == "start" and config.NOTIFY_START:
        try:
            message = config.START_MESSAGE % info
        except KeyError:
            logger.error("Unable to map info to your start notification string. Please check your settings!")
    elif info["ntype"] == "stop" and config.NOTIFY_STOP:
        try:
            message = config.STOP_MESSAGE % info
        except KeyError:
            logger.error("Unable to map info to your stop notification string. Please check your settings!")
    elif info["ntype"] == "pause" and config.NOTIFY_PAUSE:
        try:
            message = config.PAUSE_MESSAGE % info
        except KeyError:
            logger.error("Unable to map info to your pause notification string. Please check your settings!")
    elif info["ntype"] == "resume" and config.NOTIFY_RESUME:
        try:
            message = config.RESUME_MESSAGE % info
        except KeyError:
            logger.error("Unable to map info to your resume notification string. Please check your settings!")
    elif info["ntype"] == "test":
        message = "plexivity notification test"
    else:
        message = False

    status = False

    if config.NOTIFY_HUE:
        from app.providers import hue
        status = hue.send_notification(info)

    if message:
        if config.NOTIFY_PUSHOVER:
            from app.providers import pushover
            status = pushover.send_notification(message)

        if config.NOTIFY_PUSHBULLET:
            from app.providers import pushbullet
            status = pushbullet.send_notification(message)

        if config.NOTIFY_MAIL:
            from app.providers import mail
            status = mail.send_notification(message)

        if config.NOTIFY_BOXCAR:
            from app.providers import boxcar
            status = boxcar.send_notification(message)

        if config.NOTIFY_TWITTER:
            from app.providers import twitter
            status = twitter.send_notification(message)

        return status

    return False


def info_from_xml(xml, ntype, start_epoch, stop_epoch, paused=0):
    if not type(xml).__module__ == "xml.etree.ElementTree":
        xml = ET.fromstring(xml)

    state = "unknown"
    if "watched" in ntype or "stop" in ntype:
        state = "stopped"
    elif "recentlyadded" in ntype:
        state = "recentlyadded"
    else:
        state = xml.find("Player").get("state")
        if "buffering" in state:
            state = "playing"

    try:
        ma_id = xml.find('Player').get('machineIdentifier')
    except:
        ma_id = "n/a"

    ratingKey = xml.get("ratingKey")
    parentRatingKey = xml.get("parentRatingKey")

    viewOffset = 0
    if xml.get('viewOffset'):
        if int(xml.get('viewOffset'))/1000 < 90:
            viewOffset = 0
        else:
            viewOffset = int(xml.get('viewOffset'))/1000

    ## Transcoded Info
    isTranscoded = 0
    transInfo = ''
    streamType = 'D'
    streamTypeExtended = "Direct Play"
    if xml.find("TranscodeSession") != None:
        isTranscoded = 1
        transInfo = xml.find("TranscodeSession")
        streamType = "T"
        streamTypeExtended = "Audio: %(audio)s Video: %(video)s" % { "audio": xml.find("TranscodeSession").get("audioDecision"), "video": xml.find("TranscodeSession").get("videoDecision") }

    ## Time left Info
    time_left = "unknown"
    if xml.get("duration") and xml.get("viewOffset"):
        time_left = (int(xml.get("duration"))/1000)-(int(xml.get("viewOffset"))/1000)

    ## Start/Stop Time
    start_time = ""
    stop_time = ""
    grandparentRatingKey = ""
    time = start_epoch

    duration_raw = ""
    if time and stop_epoch:
        duration = stop_epoch - time
    else:
        duration = datetime.datetime.now() - time

    #set duration
    duration_raw = duration

    #exclude paused time
    if paused:
        duration = duration - datetime.timedelta(seconds=paused)

    if not ntype == "recentlyadded":
        percent_complete = "%.0f" % float( float(xml.get("viewOffset")) / float(xml.get("duration")) * 100 )
    else:
        percent_complete = "n/a"

    title = xml.get("title")

    if not ntype == "recentlyadded":
        raw_length = int(xml.get("duration"))
        orig_user = xml.find("User").get("title")

        if xml.find("Player").get("title"):
            platform = xml.find("Player").get("title")
        else:
            platform = xml.find("Player").get("platform")

        if not orig_user:
            orig_user = "Local"

        userID = xml.find("User").get("id")
        if not userID:
            userID = "Local"
    else:
        orig_user = "n/a"
        userID = "n/a"
        platform = "n/a"
        raw_length = int(xml.find("Media").get("duration")) if len(xml.find("Media")) else 0

    length = "%d %s" % ((raw_length / 1000) / 60 , "min")
    year = xml.get("year")
    rating = xml.get("contentRating")
    summary = xml.get("summary")

    genres = list()
    for x in xml.findall("Genre"):
        genres.append(x.get("tag"))

    genre = "|".join(genres)

    orig_title = title
    orig_title_ep = ""
    episode = ""
    season = ""
    if xml.get("grandparentTitle"):
        orig_title = xml.get("grandparentTitle")
        orig_title_ep = title
        grandparentRatingKey = xml.get("grandparentRatingKey")

        title = "%s - %s" % ( orig_title, title )
        episode = xml.get("index")
        season = xml.get("parentIndex")

        if int(season) and int(episode):
            title = "%s - s%02de%02d" % (title, int(season), int(episode))

    info = {
        "added": datetime.datetime.fromtimestamp(float(xml.get("addedAt"))).strftime("%Y-%m-%d %H:%M") if xml.get("addedAt") else "n/a",
        "user": config.USER_NAME_MAP[orig_user] if orig_user in config.USER_NAME_MAP else orig_user,
        "type": xml.get("type"),
        "genre": genre or "n/a",
        "userID": userID or "n/a",
        "orig_user": orig_user,
        "title": title or "n/a",
        "orig_title": orig_title or "n/a",
        "orig_title_ep": orig_title_ep or "n/a",
        "episode": episode,
        "season": season,
        "time": time,
        "stop_time": stop_time,
        "start_time": start_time,
        "rating": rating or "n/a",
        "year": year,
        "platform": platform or "n/a",
        "summary": summary or "n/a",
        "duration": duration,
        "length": length or "n/a",
        "raw_length": raw_length,
        "ntype": ntype,
        "progress": viewOffset,
        "percent_complete": percent_complete,
        "time_left": time_left,
        "viewOffset": xml.get("viewOffset"),
        "state": state,
        "transcoded": isTranscoded or "n/a",
        "streamtype": streamType or "n/a",
        "streamtype_extended": streamTypeExtended or "n/a",
        "transInfo": transInfo or "n/a",
        "machineIdentifier": ma_id or "n/a",
        "ratingKey": ratingKey,
        "parentRatingKey": parentRatingKey,
        "grandparentRatingKey": grandparentRatingKey
    }

    return info




def get_paused(session_id):
    logger.info("getting paused time for %s" % session_id)
    result = db.session.query(models.Processed).filter(models.Processed.session_id == session_id).first()
    total = result.paused_counter

    if result.paused and not result.stopped:
        if total:
            total = datetime.timedelta(seconds=total)
            total += datetime.datetime.now() - result.paused
        else:
            total = datetime.datetime.now() - result.paused

    if not total:
        total = 0
    elif type(total) == datetime.timedelta:
        total = total.total_seconds()

    return total

def get_unnotified():
    logger.info(u"getting unnotified entrys from database")
    result = db.session.query(models.Processed).filter(db.or_(models.Processed.notified == None, models.Processed.notified != 1)).all()
    return result

def get_started():
    logger.info(u"getting recently started entrys from database")
    result = db.session.query(models.Processed).filter(models.Processed.time != None).filter(models.Processed.stopped == None).all()
    logger.debug(result)
    return result

def getSessions():
    sessions = p.currentlyPlaying()

    for session in sessions:
        session_id = session.get("key") + "_" + session.find("User").get("id")
        if not db.session.query(models.Processed).filter(models.Processed.session_id == session_id).first():
            if session.get("type") == "episode":
                title = '%s - "%s"' % (session.get("grandparentTitle"), session.get("title"))
            else:
                title = session.get("title")

            offset = int(session.get("viewOffset")) / 1000 / 60
            username = session.find("User").get("title")
            platform = session.find("Player").get("platform")
            product = session.find("Player").get("product")
            player_title = session.find("Player").get("title")

            if session.find("Player").get("state") == "playing":
                message = config.START_MESSAGE % {"username": username, "platform": platform, "title": title, "product": product, "player_title": player_title, "offset": offset}
                import xml.etree.ElementTree as ET
                if config.NOTIFY_PUSHOVER:
                    from app.providers import pushover
                    pushover.send_notification(message)
                    current = models.Processed()
                    current.session_id = session_id
                    current.time = datetime.datetime.now()
                    current.user = username
                    current.platform = player_title
                    current.xml = ET.tostring(session)
                    current.notified = 1
                    current.summary = session.get("summary")
                    current.rating = session.get("contentRating")
                    current.year = session.get("year")
                    current.duration = session.get("duration")
                    current.view_offset = session.get("view_offset")
                    current.title = title

                    if session.get("type") == "episode":
                        current.season = session.get("parentIndex")
                        current.episode = session.get("index")
                        current.orig_title_ep = session.get("title")
                        current.orig_title = session.get("grandparentTitle")

                    db.session.add(current)
                    db.session.commit()
