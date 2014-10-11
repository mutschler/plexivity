#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from phue import Bridge, PhueRegistrationException
import time
from app import config
from app.logger import logger

logger = logger.getChild("hue")

def convert_color(hex_value):
	if isinstance(hex_value, basestring):
		r = int(hex_value[1:3], 16)
		g = int(hex_value[3:5], 16)
		b = int(hex_value[5:], 16)

		#print "%s converts to (%s,%s,%s)" % (hex_value, r, g, b)

		#get percentage if 255 = 1 cause of hues fucked up xy settings
		red = float(r) / 255.0
        green = float(g) / 255.0
        blue = float(b) / 255.0

        import colorsys
        h,s,v = colorsys.rgb_to_hsv(red,green,blue)
        # print colorsys.rgb_to_hsv(r,g,b)
        # print "hsv conversion would be: %s %s %s" % (h,s,v)

        # print "hue, sat, bri settings = %s, %s, %s" % (h*65535, s*255, v)

        #do convertion using the Wide RGB D65 conversion formula 
        x = red * 0.649926 + green * 0.103455 + blue * 0.197109
        y = red * 0.234327 + green * 0.743075 + blue * 0.022598
        z = red * 0.0000000 + green * 0.053077 + blue * 1.035763;

        #the final x and y values
        xx = x / (x + y + z)
        yy = y / (x + y + z)

        # print "xy vaules = %s" % [xx, yy]
        return [xx, yy]

def send_notification(info_object):
	if type(info_object) != dict:
		return False
	else:
		return decider(info_object)

def register_bridge(ip=None):
	
	try:
		b = Bridge(ip, config_file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hue.conf"))
		return b.ip
	except PhueRegistrationException:
		# print "Please press link Button on your hue! and try again"
		return False


def flash(device, options):
	options["transitiontime"] = 0

	b = Bridge(config.BRIDGE_IP, config_file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hue.conf"))
	xy = b.get_light(device, "xy")
	b.set_light(device, options)
	logger.debug("flashing light %s for 1 sec" % device)

	time.sleep(1)
	b.set_light(device, "xy", xy)

def decider(info_object):
	"""
	gets passed the COMPLETE info object, so you can decide here which light to do what with.
	"""

	if info_object["user"].lower() == "ruffy" and "rasplex" in info_object["platform"]:
		print info_object
		if info_object["state"] == "paused":
			color = "#B800D9"
			brightness = 255
		else:
			brightness = 30
			color = '#94F26F'
 		#now we dim the fuckind light in the livingroom....
		options = {
			"xy": convert_color(color),
			"transitiontime": 10,
			"bri": brightness
		}

		logger.info("setting HUE options: %s" % options)
		#flash(2, options)
		
		

		b = Bridge(config.BRIDGE_IP, config_file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hue.conf"))

		b.set_light(2, options)


def change_color(device, hex_val, duration=200, options=False):
	if duration > 300:
		duration = 300

	options = {
		"xy": convert_color(hex_val),
		"transitiontime": duration
	}

	

	b.set_light(device, options)

#B800D9
#21D900
#
# print os.path.join(os.path.dirname(os.path.abspath(__file__)), "hue.conf")
#register_bridge()

# print len(sys.argv)
# if len(sys.argv) > 1:
# 	print decider({"user":"ruffy","platform":"rasplex","ntype":"play"})
# else:
# 	print decider({"user":"ruffy","platform":"rasplex","ntype":"stop"})


# def send_notification(message):
#     logger.info(u"sending notification mail: %s" % message)
#     msg = Message("plexivity notification", recipients=[config.MAIL_RECIPIENT], sender=config.MAIL_FROM)
#     msg.body = message
#     if mail.send(msg):
#         logger.info(u"Notification mail successfully send")