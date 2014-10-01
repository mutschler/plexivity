#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import config
import requests
from xml2json import xml2json


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


    def _request(self, url, args=dict()):
        print "request... %s" % url
        if self.token:
            args["X-Plex-Token"] = self.token
        print args
        result = self.session.get("%s%s" % (self.url, url), params=args)
        print result.url

        if result.status_code == 401:
            print "doung auth"
            self.session.headers.update({'X-Plex-Client-Identifier': 'plexivity'})
            self.session.headers.update({'Content-Length': 0})

            self.session.auth = (config.PMS_USER, config.PMS_PASS)
            x = self.session.post("https://my.plexapp.com/users/sign_in.xml")
            if x.ok:
                json = xml2json(x.content, strip_ns=False)
                self.token = json["user"]["authentication-token"]
                args["X-Plex-Token"] = self.token

                print "request again"
                print args
                result = self.session.get("%s%s" % (self.url, url), params=args)

        if result:
            #import xml.etree.ElementTree as ET
            json = xml2json(result.content, strip_ns=False)
            #json = ET.fromstring(result.content)
            return json

    def getThumb(self, url):
        print dir(self)
        print self.token
        if self.token:
            return "http://%(host)s:%(port)s%(url)s?X-Plex-Token=%(token)s" % {"host": self.host, "port": self.port,
                                                                               "url": url, "token": self.token}
        else:
            return "http://%(host)s:%(port)s%(url)s" % {"host": self.host, "port": self.port, "url": url}

    def currentlyPlaying(self):
        server = self._request("status/sessions")
        if server and int(server["MediaContainer"]["@size"]) == 1:
            server["MediaContainer"]["Video"] = [server["MediaContainer"]["Video"]]
            response = server
        elif server:
            response = server
        else:
            return False

        return response

    def getSections(self):
        return self._request("library/sections")

    def recentlyAdded(self, count=6):
        args = {"X-Plex-Container-Start": 0, "X-Plex-Container-Size": count}
        return self._request("library/recentlyAdded", args)

    def getInfo(self, mediaId):
        return self._request("library/metadata/%s" % mediaId)

    def libraryStats(self):
        sections = self.getSections()

        if sections and sections["MediaContainer"]["@size"] > 1:
            for section in sections["MediaContainer"]["Directory"]:
                section["extra"] = self._request("library/sections/%s/all" % section["@key"])["MediaContainer"]

        return sections