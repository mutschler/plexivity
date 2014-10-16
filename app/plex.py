#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

from app import config
from app.logger import logger
from xml2json import xml2json


logger = logger.getChild('plex')


class Server(object):
    def __init__(self, host, port):
        if host.startswith("http://"):
            self.host = host.replace("http://", "")
        else:
            self.host = host
        self.port = port
        self.session = requests.session()
        self.url = "http://%s:%d/" % (host, port)
        self.token = False
        self.status = 0

    def test(self):
        status = self._request("status")
        if status != False:
            self.status = 1
        else:
            self.status = 0

        return self.status

    def _request(self, url, args=dict()):
        if self.token:
            args["X-Plex-Token"] = self.token

        try:
            result = self.session.get("%s%s" % (self.url, url), params=args)
            logger.debug(u"PLEX => requested url: %(url)s" % {"url": url})
            logger.debug(u"PLEX => requests args: %s" % args)

            if result.status_code == 401 and config.PMS_USER != "username" and config.PMS_PASS != "password":
                logger.debug(u"PLEX => request failed, trying with auth")
                self.session.headers.update({'X-Plex-Client-Identifier': 'plexivity'})
                self.session.headers.update({'Content-Length': 0})

                self.session.auth = (config.PMS_USER, config.PMS_PASS)
                x = self.session.post("https://my.plexapp.com/users/sign_in.xml")
                if x.ok:
                    json = xml2json(x.content, strip_ns=False)
                    self.token = json["user"]["authentication-token"]
                    args["X-Plex-Token"] = self.token
                    logger.debug(u"PLEX => auth successfull, requesting url %(url)s again" % {"url": url})
                    result = self.session.get("%s%s" % (self.url, url), params=args)
                else:
                    return False

            if result and "xml" in result.headers['content-type']:
                import xml.etree.ElementTree as ET
                #json = xml2json(result.content, strip_ns=False)
                json = ET.fromstring(result.content)
                return json
            elif result.ok:
                return result.content
            else:
                logger.error(u"PLEX => there was an error with the request")
                return False

        except requests.ConnectionError:
            logger.error(u"PLEX => could not connect to Server!!!")
            return False

    def getThumb(self, url):
        if self.token:
            return "http://%(host)s:%(port)s%(url)s?X-Plex-Token=%(token)s" % {"host": self.host, "port": self.port,
                                                                               "url": url, "token": self.token}
        else:
            return "http://%(host)s:%(port)s%(url)s" % {"host": self.host, "port": self.port, "url": url}

    def get_thumb_data(self, url):
        #/photo/:/transcode?url=http://127.0.0.1:".$plexWatch['pmsHttpPort']."".$xml->Video['art']."&width=1920&height=1080";
        args = {
            "url": "http://127.0.0.1:%(port)s/%(url)s" % {"port": self.port, "url": url}
        }
        if "/art/" in url:
            args["width"] = 1920
            args["height"] = 1080
        else:
            args["width"] = 480
            args["height"] = 694
        transcode_url = "photo/:/transcode"  #?url=http://127.0.0.1:%(port)s/%(url)s" % {"port": self.port,"url": url}

        #?url=http://127.0.0.1:%(port)s/%(url)s&width=%(width)s&height=%(height)s" % {"port": self.port,"url": url, "width": width, "height": height}
        return self._request(transcode_url, args)

    def currentlyPlaying(self):
        return self._request("status/sessions")

    def getSections(self):
        return self._request("library/sections")

    def episodes(self, mediaId):
        return self._request("library/metadata/%s/children" % mediaId)

    def recentlyAdded(self, count=6):
        args = {"X-Plex-Container-Start": 0, "X-Plex-Container-Size": count}
        return self._request("library/recentlyAdded", args)

    def getInfo(self, mediaId):
        return self._request("library/metadata/%s" % mediaId)

    def update_settings(self, host, port):
        self.host = host
        self.port = port
        self.session = requests.session()
        self.url = "http://%s:%d/" % (host, port)
        return True

    def libraryStats(self):
        sections = self.getSections()
        for section in sections:
            section.set("extra", self._request("library/sections/%s/all" % section.get("key")))

        return sections