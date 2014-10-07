from app import config, plex, models, db
import datetime

def getSessions():
    p = plex.Server(config.PMS_HOST, config.PMS_PORT)
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
