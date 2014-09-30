#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db, models

def statistics():
	pass

def playerImage(platform):
	if platform == "Roku":
		return "images/platforms/roku.png"
	elif platform == "Apple TV":
		return "images/platforms/appletv.png"
	elif platform == "Firefox":
		return "images/platforms/firefox.png"
	elif platform == "Chromecast":
		return "images/platforms/chromecast.png"
	elif platform == "Chrome":
		return "images/platforms/chrome.png"
	elif platform == "Android":
		return "images/platforms/android.png"
	elif platform == "Nexus":
		return "images/platforms/android.png"
	elif platform == "iPad":
		return "images/platforms/ios.png"
	elif platform == "iPhone":
		return "images/platforms/ios.png"
	elif platform == "iOS":
		return "images/platforms/ios.png"
	elif platform == "Plex Home Theater":
		return "images/platforms/pht.png"
	elif platform == "Linux/RPi-XBMC":
		return "images/platforms/xbmc.png"
	elif platform == "Safari":
		return "images/platforms/safari.png"
	elif platform == "Internet Explorer":
		return "images/platforms/ie.png"
	elif platform == "Unknown Browser":
		return "images/platforms/default.png"
	elif platform == "Windows-XBMC":
		return "images/platforms/xbmc.png"
	else:
		return "images/platforms/default.png"
