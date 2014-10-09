import requests
from app import config
from app.logger import logger

def send_notification(message):
    logger.info(u"sending notification to Pushbullet: %s" % message)
    args = {"type": "note", "title": message, "body": message}
    status = requests.post("https://api.pushbullet.com/v2/pushes", auth=(config.PUSHBULLET_KEY, ""), data=args)
    if status.ok:
        logger.info(u"Notification to Pushbullet successfully send")