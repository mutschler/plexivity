#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from configobj import ConfigObj


CONFIG_FILE= os.path.join(os.getcwd(), "config.ini")
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
DATA_DIR = check_setting_str(CFG, 'General', 'DATA_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PORT = check_setting_int(CFG, 'General', 'PORT', 8083)
START_MESSAGE = check_setting_str(CFG, 'General', 'START_MESSAGE', "%(username)s is currently watching %(title)s")
NOTIFY_START = check_setting_int(CFG, 'General', 'NOTIFY_START', 1)
PAUSE_MESSAGE = check_setting_str(CFG, 'General', 'PAUSE_MESSAGE', "%(username)s paused %(title)s")
NOTIFY_PAUSE = check_setting_int(CFG, 'General', 'NOTIFY_PAUSE', 1)
STOP_MESSAGE = check_setting_str(CFG, 'General', 'STOP_MESSAGE', "%(username)s has stopped watching %(title)s")
NOTIFY_STOP = check_setting_int(CFG, 'General', 'NOTIFY_STOP', 1)

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
MAIL_FROM = check_setting_str(CFG, 'Mail', 'MAIL_FROM', "plexivity <mail@example.com>")

CheckSection('Pushover')
NOTIFY_PUSHOVER = check_setting_int(CFG, 'Pushover', 'NOTIFY_PUSHOVER', 1)
PUSHOVER_USER = check_setting_str(CFG, 'Pushover', 'PUSHOVER_USER', "")
PUSHOVER_TOKEN = check_setting_str(CFG, 'Pushover', 'PUSHOVER_TOKEN', "")

SYS_ENCODING="UTF-8"

configval={}
configval["DATA_DIR"] = DATA_DIR
configval["PORT"] = PORT
configval["START_MESSAGE"] = START_MESSAGE
configval["NOTIFY_START"] = NOTIFY_START
configval["STOP_MESSAGE"] = STOP_MESSAGE
configval["NOTIFY_STOP"] = NOTIFY_STOP
configval["PAUSE_MESSAGE"] = PAUSE_MESSAGE
configval["NOTIFY_PAUSE"] = NOTIFY_PAUSE
configval["MAIL_SERVER"] = MAIL_SERVER
configval["MAIL_FROM"] = MAIL_FROM
configval["MAIL_PORT"] = MAIL_PORT
configval["MAIL_LOGIN"] = MAIL_LOGIN
configval["MAIL_PASSWORD"] = MAIL_PASSWORD
configval["NOTIFY_MAIL"] = NOTIFY_MAIL
configval["PMS_HOST"] = PMS_HOST
configval["PMS_PORT"] = PMS_PORT
configval["PMS_USER"] = PMS_USER
configval["PMS_PASS"] = PMS_PASS
configval["PMS_SSL"] = PMS_SSL
configval["PUSHOVER_USER"] = PUSHOVER_USER
configval["PUSHOVER_TOKEN"] = PUSHOVER_TOKEN
configval["NOTIFY_PUSHOVER"] = NOTIFY_PUSHOVER


def save_config(configval):
    new_config = ConfigObj(interpolation=False)
    new_config.filename = CONFIG_FILE
    new_config['General'] = {}
    new_config['General']['DATA_DIR'] = configval["DATA_DIR"]
    new_config['General']['PORT'] = configval["PORT"]
    new_config['General']['START_MESSAGE'] = configval["START_MESSAGE"]
    new_config['General']['STOP_MESSAGE'] = configval["STOP_MESSAGE"]
    new_config['General']['PAUSE_MESSAGE'] = configval["PAUSE_MESSAGE"]
    new_config['General']['NOTIFY_START'] = configval["NOTIFY_START"]
    new_config['General']['NOTIFY_STOP'] = configval["NOTIFY_STOP"]
    new_config['General']['NOTIFY_PAUSE'] = configval["NOTIFY_PAUSE"]
    new_config['Mail'] = {}
    new_config['Mail']['MAIL_PORT'] = int(configval["MAIL_PORT"])
    new_config['Mail']['MAIL_SERVER'] = configval["MAIL_SERVER"]
    new_config['Mail']['MAIL_FROM'] = configval["MAIL_FROM"]
    new_config['Mail']['MAIL_LOGIN'] = configval["MAIL_LOGIN"]
    new_config['Mail']['MAIL_PASSWORD'] = configval["MAIL_PASSWORD"]
    new_config['Mail']['NOTIFY_MAIL'] = int(configval["NOTIFY_MAIL"])
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
    new_config.write()

save_config(configval)
