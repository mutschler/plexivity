from app import mail, config
from app.logger import logger
from flask.ext.mail import Message

def send_notification(message):
    logger.info(u"sending notification mail: %s" % message)
    msg = Message("plexivity notification", recipients=[config.MAIL_RECIPIENT], sender=config.MAIL_FROM)
    msg.body = message
    if mail.send(msg):
        logger.info(u"Notification mail successfully send")