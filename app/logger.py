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
rotation = logging.handlers.RotatingFileHandler(os.path.join(config.DATA_DIR, "plexivity.log"), maxBytes=2 * 1024 * 1024, backupCount=5)
rotation.setFormatter(formatter)
logger.addHandler(rotation)

flask_logger = logging.getLogger('flask')
flask_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
flask_rotation = logging.handlers.RotatingFileHandler(os.path.join(config.DATA_DIR, "webserver.log"), maxBytes=5 * 1024 * 1024, backupCount=1)
flask_rotation.setFormatter(flask_formatter)
flask_rotation.setLevel(logging.WARNING)

if config.DEBUG:
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

logger.setLevel(logging.DEBUG)