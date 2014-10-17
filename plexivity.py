import os

from app import config
from app import app
from lib.daemon import Daemon


def run_app(port, debug):
    from subprocess import call
    #make sure database is most recent version!
    call(["python", "manage.py", "db", "upgrade"])
    app.run(host="0.0.0.0", port=port, debug=debug)


class PlexivityDaemon(Daemon):
    def run(self, port, debug):
        # Define your tasks here
        # Anything written in python is permitted
        # For example you can clean up your server logs every hour
        run_app(port, debug)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog='plexivity.py')
    #parser.add_argument('--data_dir', dest = 'data_dir', help = 'Absolute or ~/ path of the data dir')
    #parser.add_argument('--config_file', dest = 'config_file', help = 'Absolute or ~/ path of the settings file (default DATA_DIR/config.ini)')
    parser.add_argument('--daemon', action='store_true',
                        dest='daemon', help='Daemonize the app')
    parser.add_argument('--pid_file',
                        dest='pid_file', help='Path to pidfile needed for daemon')
    parser.add_argument('--stop', action='store_true',
                        dest='stop', help='stop the daemonized app')
    parser.add_argument('--status', action='store_true',
                        dest='status', help='get status of the daemonized app')
    parser.add_argument('--port',
                        dest='port', type=int, help='port to listen on')

    args = parser.parse_args()
    PIDFILE = os.path.join(config.DATA_DIR, "plexivity.pid")

    if args.port:
        port = args.port
    else:
        port = config.PORT

    if args.pid_file:
        PIDFILE = args.pid_file

    daemon = PlexivityDaemon(PIDFILE)

    if args.daemon:
        daemon.start(port, False)

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
        run_app(port, False)