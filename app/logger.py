import os
import logging
import logging.handlers

from app import config

ERROR = logging.ERROR
WARNING = logging.WARNING
MESSAGE = logging.INFO
DEBUG = logging.DEBUG

logger = logging.getLogger('plexivity')
formatter = logging.Formatter('%(asctime)s %(name)s\t %(levelname)-8s: %(message)s', '%d.%m.%Y %H:%M:%S')
rotation = logging.handlers.RotatingFileHandler(os.path.join(config.DATA_DIR, "plexivity.log"), maxBytes=5 * 1024 * 1024, backupCount=5)
rotation.setFormatter(formatter)
logger.addHandler(rotation)

if config.DEBUG:
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

logger.setLevel(logging.DEBUG)