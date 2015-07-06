#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import platform
import sys
from configobj import ConfigObj
import json

def getUserDir():
    try:
        import pwd
        os.environ['HOME'] = pwd.getpwuid(os.geteuid()).pw_dir
    except:
        pass

    return os.path.expanduser('~')

def getDataDir():

    # Windows
    if os.name == 'nt':
        return os.path.join(os.environ['APPDATA'], 'plexivity')

    user_dir = getUserDir()

    # OSX
    if 'darwin' in platform.platform().lower():
        return os.path.join(user_dir, 'Library', 'Application Support', 'plexivity')

    # FreeBSD
    if 'freebsd' in sys.platform:
        return os.path.join('/usr/local/', 'plexivity', 'data')

    # Linux
    return os.path.join(user_dir, '.plexivity')

if "PLEXIVITY_DATA" in os.environ:
    data_dir = os.environ["PLEXIVITY_DATA"]
else:
    data_dir = getDataDir()

if not os.path.isdir(data_dir):
    os.makedirs(data_dir)

CONFIG_FILE= os.path.join(data_dir, "config.ini")
CFG = ConfigObj(CONFIG_FILE, interpolation=False)

def CheckSection(sec):
    """ Check if INI section exists, if not create it """
    try:
        CFG[sec]
        return True
    except:
        CFG[sec] = {}
        return False

def check_setting_str(config, cfg_name, item_name, def_val, log=True):
    try:
        my_val = config[cfg_name][item_name]
    except Exception, e:
        my_val = def_val
        try:
            config[cfg_name][item_name] = my_val
        except:
            config[cfg_name] = {}
            config[cfg_name][item_name] = my_val
    return my_val


def check_setting_int(config, cfg_name, item_name, def_val):
    try:
        my_val = int(config[cfg_name][item_name])
    except:
        my_val = def_val
        try:
            config[cfg_name][item_name] = my_val
        except:
            config[cfg_name] = {}
            config[cfg_name][item_name] = my_val
    return my_val

CheckSection('General')
DATA_DIR = data_dir
PORT = check_setting_int(CFG, 'General', 'PORT', 8080)
START_MESSAGE = check_setting_str(CFG, 'General', 'START_MESSAGE', "%(user)s is currently watching %(title)s")
NOTIFY_START = check_setting_int(CFG, 'General', 'NOTIFY_START', 1)
PAUSE_MESSAGE = check_setting_str(CFG, 'General', 'PAUSE_MESSAGE', "%(user)s paused %(title)s")
NOTIFY_PAUSE = check_setting_int(CFG, 'General', 'NOTIFY_PAUSE', 1)
RESUME_MESSAGE = check_setting_str(CFG, 'General', 'RESUME_MESSAGE', "%(user)s resumed %(title)s")
NOTIFY_RESUME = check_setting_int(CFG, 'General', 'NOTIFY_RESUME', 1)
STOP_MESSAGE = check_setting_str(CFG, 'General', 'STOP_MESSAGE', "%(user)s has stopped watching %(title)s")
NOTIFY_STOP = check_setting_int(CFG, 'General', 'NOTIFY_STOP', 1)
RECENTLYADDED_MESSAGE = check_setting_str(CFG, 'General', 'RECENTLYADDED_MESSAGE', "new %(type)s: '%(title)s', %(length)s [%(added)s]")
NOTIFY_RECENTLYADDED = check_setting_int(CFG, 'General', 'NOTIFY_RECENTLYADDED', 1)
SCAN_INTERVAL = check_setting_int(CFG, 'General', 'SCAN_INTERVAL', 120)
CACHE_IMAGES = check_setting_int(CFG, 'General', 'CACHE_IMAGES', 1)
DEBUG = check_setting_int(CFG, 'General', 'DEBUG', 0)
SHOW_LIBRARY_STATS = check_setting_int(CFG, 'General', 'SHOW_LIBRARY_STATS', 1)

CheckSection('Advanced')
EXCLUDE_USERS = check_setting_str(CFG, 'Advanced', 'EXCLUDE_USERS', ['user1','user2'])
USER_NAME_MAP = json.loads(check_setting_str(CFG, 'Advanced', 'USER_NAME_MAP', json.dumps({'Local':'MyName', 'anotheruser': 'AnotherName'})))
EXCLUDE_SECTIONS =  check_setting_str(CFG, 'Advanced', 'EXCLUDE_SECTIONS', ["100","200"])

CheckSection('PMS')
PMS_HOST = check_setting_str(CFG, 'PMS', 'PMS_HOST', 'localhost')
PMS_PORT = check_setting_int(CFG, 'PMS', 'PMS_PORT', 32400)
PMS_USER = check_setting_str(CFG, 'PMS', 'PMS_USER', 'username')
PMS_PASS = check_setting_str(CFG, 'PMS', 'PMS_PASS', 'password')
PMS_SSL = check_setting_int(CFG, 'PMS', 'PMS_SSL', 0)

CheckSection('Mail')
NOTIFY_MAIL = check_setting_int(CFG, 'Mail', 'NOTIFY_MAIL', 0)
MAIL_SERVER = check_setting_str(CFG, 'Mail', 'MAIL_SERVER', 'mail.example.com')
MAIL_LOGIN = check_setting_str(CFG, 'Mail', 'MAIL_LOGIN', "mail@example.com")
MAIL_PASSWORD = check_setting_str(CFG, 'Mail', 'MAIL_PASSWORD', "mypassword")
MAIL_PORT = check_setting_int(CFG, 'Mail', 'MAIL_PORT', 25)
MAIL_FROM = check_setting_str(CFG, 'Mail', 'MAIL_FROM', "mail@example.com")
MAIL_RECIPIENT = check_setting_str(CFG, 'Mail', 'MAIL_RECIPIENT', "mail@example.com")

CheckSection('Pushover')
NOTIFY_PUSHOVER = check_setting_int(CFG, 'Pushover', 'NOTIFY_PUSHOVER', 0)
PUSHOVER_USER = check_setting_str(CFG, 'Pushover', 'PUSHOVER_USER', "")
PUSHOVER_TOKEN = check_setting_str(CFG, 'Pushover', 'PUSHOVER_TOKEN', "")

CheckSection('Scripts')
USE_PPSCRIPTS = check_setting_int(CFG, 'Scripts', 'USE_PPSCRIPTS', 0)
PP_SCRIPTS = check_setting_str(CFG, 'Scripts', 'PP_SCRIPTS', ["/path/to/scirpt.sh"])
PP_SCRIPTS_LOGGING = check_setting_int(CFG, 'Scripts', 'PP_SCRIPTS_LOGGING', 1)

CheckSection('Pushbullet')
NOTIFY_PUSHBULLET = check_setting_int(CFG, 'Pushbullet', 'NOTIFY_PUSHBULLET', 0)
PUSHBULLET_KEY = check_setting_str(CFG, 'Pushbullet', 'PUSHBULLET_KEY', "")

CheckSection('Hue')
NOTIFY_HUE = check_setting_int(CFG, 'Hue', 'NOTIFY_HUE', 0)
BRIDGE_IP = check_setting_str(CFG, 'Hue', 'BRIDGE_IP', "")
HUE_USERNAME = check_setting_str(CFG, 'Hue', 'HUE_USERNAME', "")

CheckSection('Boxcar')
NOTIFY_BOXCAR = check_setting_int(CFG, 'Boxcar', 'NOTIFY_BOXCAR', 0)
BOXCAR_TOKEN = check_setting_str(CFG, 'Boxcar', 'BOXCAR_TOKEN', "")

CheckSection('Twitter')
NOTIFY_TWITTER = check_setting_int(CFG, 'Twitter', 'NOTIFY_TWITTER', 0)
TWITTER_USE_DM = check_setting_int(CFG, 'Twitter', 'TWITTER_USE_DM', 0)
TWITTER_DM_USER = check_setting_str(CFG, 'Twitter', 'TWITTER_DM_USER', "userToDM")
TWITTER_ACCESS_TOKEN = check_setting_str(CFG, 'Twitter', 'TWITTER_ACCESS_TOKEN', "")
TWITTER_ACCESS_TOKEN_SECRET = check_setting_str(CFG, 'Twitter', 'TWITTER_ACCESS_TOKEN_SECRET', "")

CheckSection('Flask')
PASSWORD_SALT = check_setting_str(CFG, 'Flask', 'PASSWORD_SALT', os.urandom(20).encode('base_64').strip())
SECRET_KEY = check_setting_str(CFG, 'Flask', 'SECRET_KEY', os.urandom(20).encode('base_64').strip())

SYS_ENCODING="UTF-8"

configval={}
configval["PORT"] = PORT
configval["DEBUG"] = DEBUG
configval["SHOW_LIBRARY_STATS"] = SHOW_LIBRARY_STATS
configval["CACHE_IMAGES"] = CACHE_IMAGES
configval["RECENTLYADDED_MESSAGE"] = RECENTLYADDED_MESSAGE
configval["NOTIFY_RECENTLYADDED"] = NOTIFY_RECENTLYADDED
configval["START_MESSAGE"] = START_MESSAGE
configval["NOTIFY_START"] = NOTIFY_START
configval["STOP_MESSAGE"] = STOP_MESSAGE
configval["NOTIFY_STOP"] = NOTIFY_STOP
configval["PAUSE_MESSAGE"] = PAUSE_MESSAGE
configval["NOTIFY_PAUSE"] = NOTIFY_PAUSE
configval["RESUME_MESSAGE"] = RESUME_MESSAGE
configval["NOTIFY_RESUME"] = NOTIFY_RESUME
configval["SCAN_INTERVAL"] = SCAN_INTERVAL
configval["MAIL_SERVER"] = MAIL_SERVER
configval["MAIL_FROM"] = MAIL_FROM
configval["MAIL_PORT"] = MAIL_PORT
configval["MAIL_LOGIN"] = MAIL_LOGIN
configval["MAIL_PASSWORD"] = MAIL_PASSWORD
configval["MAIL_RECIPIENT"] = MAIL_RECIPIENT
configval["NOTIFY_MAIL"] = NOTIFY_MAIL
configval["PMS_HOST"] = PMS_HOST
configval["PMS_PORT"] = PMS_PORT
configval["PMS_USER"] = PMS_USER
configval["PMS_PASS"] = PMS_PASS
configval["PMS_SSL"] = PMS_SSL
configval["PUSHOVER_USER"] = PUSHOVER_USER
configval["PUSHOVER_TOKEN"] = PUSHOVER_TOKEN
configval["NOTIFY_PUSHOVER"] = NOTIFY_PUSHOVER
configval["NOTIFY_PUSHBULLET"] = NOTIFY_PUSHBULLET
configval["PUSHBULLET_KEY"] = PUSHBULLET_KEY
configval["BRIDGE_IP"] = BRIDGE_IP
configval["HUE_USERNAME"] = HUE_USERNAME
configval["NOTIFY_HUE"] = NOTIFY_HUE
configval["BOXCAR_TOKEN"] = BOXCAR_TOKEN
configval["NOTIFY_BOXCAR"] = NOTIFY_BOXCAR
configval["PASSWORD_SALT"] = PASSWORD_SALT
configval["SECRET_KEY"] = SECRET_KEY
configval["EXCLUDE_USERS"] = EXCLUDE_USERS
configval["USER_NAME_MAP"] =json.dumps(USER_NAME_MAP)
configval["NOTIFY_TWITTER"] = NOTIFY_TWITTER
configval["TWITTER_ACCESS_TOKEN"] = TWITTER_ACCESS_TOKEN
configval["TWITTER_ACCESS_TOKEN_SECRET"] = TWITTER_ACCESS_TOKEN_SECRET
configval["TWITTER_USE_DM"] = TWITTER_USE_DM
configval["TWITTER_DM_USER"] = TWITTER_DM_USER
configval["EXCLUDE_SECTIONS"] = EXCLUDE_SECTIONS
configval["USE_PPSCRIPTS"] = USE_PPSCRIPTS
configval["PP_SCRIPTS"] = PP_SCRIPTS
configval["PP_SCRIPTS_LOGGING"] = PP_SCRIPTS_LOGGING

def save_config(configval):
    new_config = ConfigObj(interpolation=False)
    new_config.filename = CONFIG_FILE
    new_config['General'] = {}
    new_config['General']['PORT'] = configval["PORT"]
    new_config['General']['START_MESSAGE'] = configval["START_MESSAGE"]
    new_config['General']['STOP_MESSAGE'] = configval["STOP_MESSAGE"]
    new_config['General']['PAUSE_MESSAGE'] = configval["PAUSE_MESSAGE"]
    new_config['General']['RESUME_MESSAGE'] = configval["RESUME_MESSAGE"]
    new_config['General']['RECENTLYADDED_MESSAGE'] = configval["RECENTLYADDED_MESSAGE"]
    new_config['General']['NOTIFY_START'] = int(configval["NOTIFY_START"])
    new_config['General']['NOTIFY_STOP'] = int(configval["NOTIFY_STOP"])
    new_config['General']['NOTIFY_PAUSE'] = int(configval["NOTIFY_PAUSE"])
    new_config['General']['NOTIFY_RESUME'] = int(configval["NOTIFY_RESUME"])
    new_config['General']['NOTIFY_RECENTLYADDED'] = int(configval["NOTIFY_RECENTLYADDED"])
    new_config['General']['SCAN_INTERVAL'] = int(configval["SCAN_INTERVAL"])
    new_config['General']['CACHE_IMAGES'] = int(configval["CACHE_IMAGES"])
    new_config['General']['DEBUG'] = int(configval["DEBUG"])
    new_config['General']['SHOW_LIBRARY_STATS'] = int(configval["SHOW_LIBRARY_STATS"])
    new_config['Advanced'] = {}
    new_config['Advanced']['EXCLUDE_USERS'] = configval["EXCLUDE_USERS"]
    new_config['Advanced']['USER_NAME_MAP'] = configval["USER_NAME_MAP"]
    new_config['Advanced']['EXCLUDE_SECTIONS'] = configval["EXCLUDE_SECTIONS"]
    new_config['Mail'] = {}
    new_config['Mail']['MAIL_PORT'] = int(configval["MAIL_PORT"])
    new_config['Mail']['MAIL_SERVER'] = configval["MAIL_SERVER"]
    new_config['Mail']['MAIL_FROM'] = configval["MAIL_FROM"]
    new_config['Mail']['MAIL_LOGIN'] = configval["MAIL_LOGIN"]
    new_config['Mail']['MAIL_PASSWORD'] = configval["MAIL_PASSWORD"]
    new_config['Mail']['NOTIFY_MAIL'] = int(configval["NOTIFY_MAIL"])
    new_config['Mail']['MAIL_RECIPIENT'] = configval["MAIL_RECIPIENT"]
    new_config['PMS'] = {}
    new_config['PMS']['PMS_HOST'] = configval["PMS_HOST"]
    new_config['PMS']['PMS_PORT'] = int(configval["PMS_PORT"])
    new_config['PMS']['PMS_USER'] = configval["PMS_USER"]
    new_config['PMS']['PMS_PASS'] = configval["PMS_PASS"]
    new_config['PMS']['PMS_SSL'] = int(configval["PMS_SSL"])
    new_config['Pushover'] = {}
    new_config['Pushover']['NOTIFY_PUSHOVER'] = int(configval["NOTIFY_PUSHOVER"])
    new_config['Pushover']['PUSHOVER_USER'] = configval["PUSHOVER_USER"]
    new_config['Pushover']['PUSHOVER_TOKEN'] = configval["PUSHOVER_TOKEN"]
    new_config['Pushbullet'] = {}
    new_config['Pushbullet']['NOTIFY_PUSHBULLET'] = int(configval["NOTIFY_PUSHBULLET"])
    new_config['Pushbullet']['PUSHBULLET_KEY'] = configval["PUSHBULLET_KEY"]
    new_config['Hue'] = {}
    new_config['Hue']['BRIDGE_IP'] = configval["BRIDGE_IP"]
    new_config['Hue']['HUE_USERNAME'] = configval["HUE_USERNAME"]
    new_config['Hue']['NOTIFY_HUE'] = configval["NOTIFY_HUE"]
    new_config['Boxcar'] = {}
    new_config['Boxcar']['BOXCAR_TOKEN'] = configval["BOXCAR_TOKEN"]
    new_config['Boxcar']['NOTIFY_BOXCAR'] = int(configval["NOTIFY_BOXCAR"])
    new_config['Twitter'] = {}
    new_config['Twitter']['NOTIFY_TWITTER'] = int(configval["NOTIFY_TWITTER"])
    new_config['Twitter']['TWITTER_USE_DM'] = int(configval["TWITTER_USE_DM"])
    new_config['Twitter']['TWITTER_DM_USER'] = configval["TWITTER_DM_USER"]
    new_config['Twitter']['TWITTER_ACCESS_TOKEN'] = configval["TWITTER_ACCESS_TOKEN"]
    new_config['Twitter']['TWITTER_ACCESS_TOKEN_SECRET'] = configval["TWITTER_ACCESS_TOKEN_SECRET"]
    new_config['Flask'] = {}
    new_config['Flask']['PASSWORD_SALT'] = configval["PASSWORD_SALT"]
    new_config['Flask']['SECRET_KEY'] = configval["SECRET_KEY"]
    new_config['Scripts'] = {}
    new_config['Scripts']['PP_SCRIPTS'] = configval["PP_SCRIPTS"]
    new_config['Scripts']['USE_PPSCRIPTS'] = int(configval["USE_PPSCRIPTS"])
    new_config['Scripts']['PP_SCRIPTS_LOGGING'] = int(configval["PP_SCRIPTS_LOGGING"])
    new_config.write()

save_config(configval)
