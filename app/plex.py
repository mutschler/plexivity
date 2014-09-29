#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from xml2json import xml2json


class Server(object):
    def __init__(self, host, port):
        if host.startswith("http://"):
            self.host = host.replace("http://", "")
        else:
            self.host = host
        self.port = port
        self.url = "http://%s:%d/" % (host, port)


    def _request(self, url):
        result = requests.get("%s%s" % (self.url, url))
        if result:
            json = xml2json(result.content, strip_ns=False)
            return json


    def currentlyPlaying(self):
        server = self._request("status/sessions")
        response = list()
        if server and int(server["MediaContainer"]["@size"]) == 1:
            response.append(server["MediaContainer"]["Video"])
        elif server:
            response = server["MediaContainer"]
        else:
            return False

        return response