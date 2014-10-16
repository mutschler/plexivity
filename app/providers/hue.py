#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from phue import Bridge, PhueRegistrationException
import time
from app import config
from app.logger import logger

logger = logger.getChild("hue")

def convert_color(color):
	if isinstance(color, basestring):
		#if sting assume we got an hex value
		r = int(color[1:3], 16)
		g = int(color[3:5], 16)
		b = int(color[5:], 16)
		logger.debug("hex code %s converts to rgb(%d, %d, %d)" % (color, r, g, b))
	elif isinstance(color, tuple):
		#if tuple its (r, g, b)
		r, g, b = color

		#get percentage if 255 = 1 cause of hues fucked up xy settings
		red = float(r) / 255.0
        green = float(g) / 255.0
        blue = float(b) / 255.0

        import colorsys
        h,s,v = colorsys.rgb_to_hsv(red, green, blue)
        logger.debug("hsv conversion would be: %s %s %s" % (h,s,v))
        logger.debug("hsb conversion would be: %s %s" % (h*65535, s*255, v))

        #do convertion using the Wide RGB D65 conversion formula 
        x = red * 0.649926 + green * 0.103455 + blue * 0.197109
        y = red * 0.234327 + green * 0.743075 + blue * 0.022598
        z = red * 0.0000000 + green * 0.053077 + blue * 1.035763;

        #the final x and y values
        xx = x / (x + y + z)
        yy = y / (x + y + z)

        logger.debug("xy values: %s %s" % (x, y))
        return [xx, yy]

def send_notification(info_object):
	if type(info_object) != dict:
		return False
	else:
		return decider(info_object)

def get_bridge():
	try:
		b = Bridge(config_file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hue.conf"))
		return b
	except PhueRegistrationException:
		return False

def register_bridge(ip=None):
	
	try:
		b = Bridge(ip, config_file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hue.conf"))
		return b.ip
	except PhueRegistrationException:
		return False


def flash(device, options):
	options["transitiontime"] = 0

	b = Bridge(config.BRIDGE_IP, config_file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hue.conf"))
	xy = b.get_light(device, "xy")
	b.set_light(device, options)
	logger.debug("flashing light %s for 1 sec" % device)

	time.sleep(1)
	b.set_light(device, "xy", xy)

def get_available_lights():
	to_return = list()
	print "tesing bridge"
	if config.BRIDGE_IP and register_bridge(config.BRIDGE_IP):
		b = get_bridge()
		lights = b.get_light_objects()
		for l in lights:
			print dir(l)
			current = {
				"id": l.light_id,
				"name": l.name
			}
			to_return.append(current)
		return to_return
	else:
		return False

	

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
