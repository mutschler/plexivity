#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app.plex import Server
from app import models


s = Server("192.168.0.55", 32400)

# sessions = s._request("status/sessions")
#
# print sessions
#
#
# if int(sessions["MediaContainer"]["@size"]) > 1:
#
#     for session in sessions["MediaContainer"]["Video"]:
#q
#         if session["Player"]["@state"] == "playing":
#             print "%s is watching %s via %s (%s/100)" % (
#             session["User"]["@title"], session["@title"], session["Player"]["@title"], session["@viewOffset"])
#         #push that shit to my phone :)
#         elif session["Player"]["@state"] == "paused":
#             print "%s paused %s via %s (%s/100)" % (
#             session["User"]["@title"], session["@title"], session["Player"]["@title"], session["@viewOffset"])
#
# else:
#     print sessions["MediaContainer"]["Video"]
#     session = sessions["MediaContainer"]["Video"]
#     print "%s is watching %s via %s %s minutes in)" % (
#             session["User"]["@title"], session["@title"], session["Player"]["@title"], int(session["@viewOffset"])/60)


x= s.currentlyPlaying()

p = models.Processed()
p.title = x[0]["@title"]

models.db.session.commit()