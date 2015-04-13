from app import config
from app.logger import logger
import tweepy

logger = logger.getChild("twitter")

def send_notification(message):
    auth = tweepy.OAuthHandler("T4NRPcEtUrCEU58FesRmRtkdW", "zmpbytgPpSbro6RZcXsKgYQoz24zLH3vYZHOHAAs5j33P4eoRg")
    auth.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    try:
        api.auth.get_username()
    except:
        logger.error(u"check your twitter credits!")
        return False

    logger.info(u"sending notification to twitter: %s" % message)
    if config.TWITTER_USE_DM:
        status = api.send_direct_message(user=config.TWITTER_DM_USER, text=message)
    else:
        status = api.update_status(status=message)
    if status:
        logger.info(u"Notification to twitter successfully send: %s" % status.text)
        return True
    else:
        logger.error(u"unable to send twitter notification: %s" % status)
        return False