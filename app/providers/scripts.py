#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from app import config
from app.logger import logger
from subprocess import Popen, PIPE

logger = logger.getChild("scripts")

def log_lines(script, line):

	if not script:
		l = logger.getChild("UNKNOWN")
	else:
		sname = os.path.basename(script)
		sname, ext = os.path.splitext(sname)
		l = logger.getChild(sname)

	if line.startswith("[INFO]"):
		line = line.replace("[INFO]", "")
		l.info(line.strip())
	elif line.startswith("[DEBUG]"):
		line = line.replace("[DEBUG]", "")
		l.debug(line.strip())
	elif line.startswith("[WARNING]"):
		line = line.replace("[WARNING]","")
		l.warning(line.strip())
	elif line.startswith("[ERROR]"):
		line = line.replace("[ERROR]","")
		l.error(line.strip())
	else:
		l.info(line.strip())

def run_scripts(info, message):
	os.environ['PLX_MESSAGE'] = message
	for x in info:
		try:
			os.environ['PLX_%s' % x.upper()] = '%s' % info[x]
		except:
			os.environ['PLX_%s' % x.upper()] = 'n/a'
			logger.warning("unable to set env variable for PLX_%s, setting to 'n/a'" % (x.upper()))
			continue
			#logger.warning("unable to set env variable for PLX_%s = %s" % (x.upper(), info[x]))

	for script in config.PP_SCRIPTS:
		if not os.path.exists(script):
			logger.warning("%s does not exist", script)
			continue

		logger.info("executing script: [%s]" % script)
		p = Popen([script], stdout=PIPE, stderr=None)
		if config.PP_SCRIPTS_LOGGING:
			for line in p.stdout:
				log_lines(script, line)

		p.communicate()
		
		if p.returncode == 0:
			logger.info("script executed successfull: [%s]" % script)
		else:
			logger.warning("script: [%s] failed with code: %s" % (script, p.returncode))