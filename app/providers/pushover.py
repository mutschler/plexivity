import requests
from app import config

def send_notification(message):
    args = {"token": config.PUSHOVER_TOKEN, "user": config.PUSHOVER_USER, "message": message}
    status = requests.post("https://api.pushover.net/1/messages.json", data=args)
    if status.ok:
        print "yeah!"