#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from app import config
from app.logger import logger

def send_notification(message):
    logger.info(u"sending notification to Boxcar: %s" % message)
    args = {'notification[long_message]': message, 'notification[title]': "plexivity", 'notification[sound]': 'bird-1', 'user_credentials': config.BOXCAR_TOKEN}
    status = requests.post("https://new.boxcar.io/api/notifications", data=args, timeout=2)
    if status.ok:
        logger.info(u"Notification to Boxcar successfully send")
        return True