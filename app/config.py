#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from configobj import ConfigObj


CONFIG_FILE= os.path.join(os.getcwd(), "config.ini")
CFG = ConfigObj(CONFIG_FILE)

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
    except:
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

CheckSection('PMS')
PMS_HOST = check_setting_str(CFG, 'PMS', 'PMS_HOST', 'localhost')
PMS_PORT = check_setting_int(CFG, 'PMS', 'PMS_PORT', 32400)
PMS_USER = check_setting_str(CFG, 'PMS', 'PMS_USER', 'username')
PMS_PASS = check_setting_str(CFG, 'PMS', 'PMS_PASS', 'password')
PMS_SSL = check_setting_int(CFG, 'PMS', 'PMS_SSL', 0)

CheckSection('Mail')
MAIL_SERVER = check_setting_str(CFG, 'Mail', 'MAIL_SERVER', 'mail.example.com')
MAIL_LOGIN = check_setting_str(CFG, 'Mail', 'MAIL_LOGIN', "mail@example.com")
MAIL_PASSWORD = check_setting_str(CFG, 'Mail', 'MAIL_PASSWORD', "mypassword")
MAIL_PORT = check_setting_int(CFG, 'Mail', 'MAIL_PORT', 25)
MAIL_FROM = check_setting_str(CFG, 'Mail', 'MAIL_FROM', "library automailer <mail@example.com>")


SYS_ENCODING="UTF-8"

configval={}
configval["DATA_DIR"] = DATA_DIR
configval["PORT"] = PORT
configval["MAIL_SERVER"] = MAIL_SERVER
configval["MAIL_FROM"] = MAIL_FROM
configval["MAIL_PORT"] = MAIL_PORT
configval["MAIL_LOGIN"] = MAIL_LOGIN
configval["MAIL_PASSWORD"] = MAIL_PASSWORD
configval["PMS_HOST"] = PMS_HOST
configval["PMS_PORT"] = PMS_PORT
configval["PMS_USER"] = PMS_USER
configval["PMS_PASS"] = PMS_PASS
configval["PMS_SSL"] = PMS_SSL

def save_config(configval):
    new_config = ConfigObj()
    new_config.filename = CONFIG_FILE
    new_config['General'] = {}
    new_config['General']['DATA_DIR'] = configval["DATA_DIR"]
    new_config['General']['PORT'] = configval["PORT"]
    new_config['Mail'] = {}
    new_config['Mail']['MAIL_PORT'] = int(configval["MAIL_PORT"])
    new_config['Mail']['MAIL_SERVER'] = configval["MAIL_SERVER"]
    new_config['Mail']['MAIL_FROM'] = configval["MAIL_FROM"]
    new_config['Mail']['MAIL_LOGIN'] = configval["MAIL_LOGIN"]
    new_config['Mail']['MAIL_PASSWORD'] = configval["MAIL_PASSWORD"]
    new_config['PMS'] = {}
    new_config['PMS']['PMS_HOST'] = configval["PMS_HOST"]
    new_config['PMS']['PMS_PORT'] = int(configval["PMS_PORT"])
    new_config['PMS']['PMS_USER'] = configval["PMS_USER"]
    new_config['PMS']['PMS_PASS'] = configval["PMS_PASS"]
    new_config['PMS']['PMS_SSL'] = int(configval["PMS_SSL"])
    new_config.write()
    return "Saved"

save_config(configval)
