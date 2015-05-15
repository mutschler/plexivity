import requests
from app import config
from app.logger import logger

logger = logger.getChild("pushover")

def send_notification(message):
    logger.info(u"sending notification to Pushover: %s" % message)
    args = {"token": config.PUSHOVER_TOKEN, "user": config.PUSHOVER_USER, "message": message}
    status = requests.post("https://api.pushover.net/1/messages.json", data=args)
    if status.ok and status.json()["status"] == 1:
        logger.info(u"Notification to Pushover successfully send with response %s" % status.content)
        return True
    else:
        logger.error(u"Unable to send notification to pushover: %s" % status.content)
        return False