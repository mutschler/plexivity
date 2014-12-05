#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


from app import app
from lib.daemon import Daemon


def run_app():
    app.run(host="0.0.0.0", port=config.PORT, debug=False)


class PlexivityDaemon(Daemon):
    def run(self):
        # Define your tasks here
        # Anything written in python is permitted
        # For example you can clean up your server logs every hour
        run_app()


if __name__ == "__main__":
    import argparse
    from app import config

    parser = argparse.ArgumentParser(prog='plexivity.py')
    parser.add_argument('--daemon', action='store_true',
                        dest='daemon', help='Daemonize the app')
    parser.add_argument('--pid-file',
                        dest='pid_file', help='Path to pidfile needed for daemon')
    parser.add_argument('--stop', action='store_true',
                        dest='stop', help='stop the daemonized app')
    parser.add_argument('--status', action='store_true',
                        dest='status', help='get status of the daemonized app')
    parser.add_argument('--port',
                        dest='port', type=int, help='port to listen on')
    parser.add_argument('--data-dir',
                        dest='data_dir', help='Path to plexivity data direcotry')
    parser.add_argument('--config-file',
                        dest='config_file', help='Use this config file as default')

    args = parser.parse_args()
    PIDFILE = os.path.join(config.DATA_DIR, "plexivity.pid")

    if args.port:
        port = args.port
        config.PORT = args.port
    else:
        port = config.PORT

    if args.config_file:
        config.CONFIG_FILE = args.config_file

    if args.data_dir:
        config.DATA_DIR = args.data_dir

    if args.pid_file:
        PIDFILE = args.pid_file

    daemon = PlexivityDaemon(PIDFILE)

    if args.daemon:
        daemon.start()

    if args.stop:
        daemon.stop()

    if args.status:
        try:
            pf = file(PIDFILE, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        except SystemExit:
            pid = None

        if pid:
            print 'plexivity is running as pid %s' % pid
        else:
            print 'plexivity is not running.'

    if not args.daemon and not args.status and not args.stop:
        run_app()