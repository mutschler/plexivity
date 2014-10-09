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

    for session in live:
        logger.debug(session)
        userID = session.find('User').get('id')
        if not userID:
            userID = "Local"

        db_key = "%(id)s_%(key)s_%(userid)s" % { "id": session.get('id'), "key": session.get('key'), "userid": userID }
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
            if playing[k.session_id]:
                ntype = "start"

            paused = get_paused(k.session_id)
            info = info_from_xml(k.xml, ntype, start_epoch, stop_epoch, paused)

            logger.debug(info)

            logger.debug("sending notification for: %s : %s" % (info["user"], info["orig_title_ep"]))

            if notify(info):
                set_notified(k.session_id)

    else:
        did_unnotify = 1

    ## notify stopped
    ## redo this! currently everything started is set to stopped?
    if did_unnotify:
        started = get_started()
        for k in started:
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
                notify(info)
                k.notified = 1
                db.session.merge(k)
                db.session.commit()

    ## notify start/now playing
    logger.debug("processing live content")
    for k in live:
        start_epoch = datetime.datetime.now()
        stop_epoch = "" #not stopped yet
        xml_string = ET.tostring(k)
        info = info_from_xml(k, "start", start_epoch, stop_epoch, 0)
        info["decoded"] = 1

        logger.debug(info)

        userID = info["userID"]
        if not userID:
            userID = "Local"

        db_key = "%(id)s_%(key)s_%(userid)s" % { "id": k.get('id'), "key": k.get('key'), "userid": userID }

        ## ignore content already been notified

        if started:
            for x in started:
                if x.session_id == db_key:
                    state_change = process_update(k, db_key)

                if state_change:
                    logger.debug("%s: %s: state changed [%s] notify called" % (info["user"], info["title"], info["state"]))
                    notify(info)
        else:
            #unnotified insert to db and notify
            process_start(xml_string, db_key, info)
            notify(info)
            set_notified(db_key)

def set_notified(db_key):
    res = get_from_db(db_key)
    res.notified = 1
    db.session.merge(res)
    db.session.commit()

def process_start(xml_string, db_key, info):
    new = models.Processed()
    new.session_id = db_key
    new.title = info["title"]
    new.platform = info["platform"]
    new.user = info["user"]
    new.orig_title = info["orig_title"]
    new.orig_title_ep = info["orig_title_ep"]
    new.duration = info["raw_length"]
    #new.genre = info["genre"]
    new.episode = info["episode"]
    new.season = info["season"]
    new.summary = info["summary"]
    new.rating = info["rating"]
    new.year = info["year"]
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

    status_change = 0

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
            status_change = 1
            logger.debug("Video State: %s [prev: %s]" % (state, prev_state))

        cur = db.session.query(models.Processed).filter(models.Processed.session_id == session_id).first()

        now = datetime.datetime.now()
        if state and "paused" in state:
            if not p_epoch:
                extra = "%s, paused = %s" % (extra, now)
                logger.debug("Marking as Paused on %s [%s]" % (now, now))
                status_change = 1
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
                status_change = 1
                cur.paused = None
                cur.paused_counter = p_counter

        logger.debug("total paused duration: %s [p_counter seconds]" % p_counter)

        cur.xml = ET.tostring(xml)
        db.session.merge(cur)
        db.session.commit()

    return status_change

def notify(info):
    #notify all providers with the given stuff...
    logger.debug("IMPLEMENT NOTIFY STUFF HERE")

    if info["state"] == "playing" and config.NOTIFY_START:
        message = config.START_MESSAGE % info
    elif info["state"] == "stopped" and config.NOTIFY_STOP:
        message = config.STOP_MESSAGE % info
    elif info["state"] == "paused" and config.NOTIFY_PAUSE:
        message = config.PAUSE_MESSAGE % info
    else:
        message = False

    if message:
        if config.NOTIFY_PUSHOVER:
            from app.providers import pushover
            pushover.send_notification(message)

        if config.NOTIFY_PUSHBULLET:
            from app.providers import pushbullet
            pushbullet.send_notification(message)

        if config.NOTIFY_MAIL:
            from app.providers import mail
            mail.send_notification(message)

    return False


def info_from_xml(xml, ntype, start_epoch, stop_epoch, paused=0):
    if not type(xml).__module__ == "xml.etree.ElementTree":
        xml = ET.fromstring(xml)

    state = "unknown"
    if "watched" in ntype or "stop" in ntype:
        state = "stopped"
    else:
        state = xml.find("Player").get("state")
        if "buffering" in state:
            state = "playing"

    ma_id = xml.find('Player').get('machineIdentifier')
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

    percent_complete = "%.0f" % float( float(xml.get("viewOffset")) / float(xml.get("duration")) * 100 )

    title = xml.get("title")
    if xml.find("Player").get("title"):
        platform = xml.find("Player").get("title")
    else:
        platform = xml.find("Player").get("platform")

    length = int(xml.get("duration")) / 1000
    orig_user = xml.find("User").get("title")
    if not orig_user:
        orig_user = "Local"

    userID = xml.find("User").get("id")
    if not userID:
        userID = "Local"

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
        "user": orig_user,
        "type": xml.get("type"),
        "genre": genre,
        "userID": userID,
        "orig_user": orig_user,
        "title": title,
        "orig_title": orig_title,
        "orig_title_ep": orig_title_ep,
        "episode": episode,
        "season": season,
        "platform": platform,
        "time": time,
        "stop_time": stop_time,
        "start_time": start_time,
        "rating": rating,
        "year": year,
        "platform": platform,
        "summary": summary,
        "duration": duration,
        "length": length,
        "raw_length": int(xml.get("duration")),
        "ntype": ntype,
        "progress": viewOffset,
        "percent_complete": percent_complete,
        "time_left": time_left,
        "viewOffset": xml.get("viewOffset"),
        "state": state,
        "transcoded": isTranscoded,
        "streamtype": streamType,
        "streamtype_extended": streamTypeExtended,
        "transInfo": transInfo,
        "machineIdentifier": ma_id,
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
        total += datetime.datetime.now() - result.paused

    if not total:
        total = 0

    return total

def get_unnotified():
    logger.info(u"getting unnotified entrys from database")
    result = db.session.query(models.Processed).filter(models.Processed.notified == None ).all()
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
                print message
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
