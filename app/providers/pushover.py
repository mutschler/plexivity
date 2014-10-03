import requests
from app import config
from app.logger import logger

def send_notification(message):
    logger.info(u"sending notification to Pushover")
    args = {"token": config.PUSHOVER_TOKEN, "user": config.PUSHOVER_USER, "message": message}
    status = requests.post("https://api.pushover.net/1/messages.json", data=args)
    if status.ok:
        logger.info(u"Notification to Pushover successfully send")