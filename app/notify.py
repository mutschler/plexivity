from app import config, plex, models, db
import datetime

def getSessions():
    print "yeah"
    import logging
    logging.basicConfig()
    p = plex.Server(config.PMS_HOST, config.PMS_PORT)
    sessions = p.currentlyPlaying()

    for session in sessions:
        if not db.session.query(models.Processed).filter(models.Processed.session_id == session.get("sessionKey")).first():
            if session.get("type") == "episode":
                title = '%s - "%s"' % (session.get("grandparentTitle"), session.get("title"))
            else:
                title = session.get("title")

            offset = int(session.get("viewOffset")) / 1000 / 60
            username = session.find("User").get("title")
            platform = session.find("Player").get("platform")
            product = session.find("Player").get("product")
            player_title = session.find("Player").get("product")

            if session.find("Player").get("state") == "playing":
                message = config.START_MESSAGE % {"username": username, "platform": platform, "title": title, "product": product, "player_title": player_title, "offset": offset}
                print message
                import xml.etree.ElementTree as ET
                if config.NOTIFY_PUSHOVER:
                    from app.providers import pushover
                    pushover.send_notification(message)
                    current = models.Processed()
                    current.session_id = session.get("sessionKey")
                    current.time = datetime.datetime.now()
                    current.user = username
                    current.platform = platform
                    current.xml = ET.tostring(sessions)
                    current.notified = 1
                    db.session.add(current)
                    db.session.commit()
