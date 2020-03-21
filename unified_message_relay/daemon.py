#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from .Lib.DaemonClass import Daemon


class MainProcess(Daemon):
    def run(self, debug_mode):
        from .Core.UMRManager import UMRManager
        UMRManager.run()


def main():
    # ARGS
    argP = argparse.ArgumentParser(
        description="QQ <-> Telegram Bot Framework & Forwarder", formatter_class=argparse.RawTextHelpFormatter)
    cmdHelpStr = """
start   - start bot as a daemon
stop    - stop bot
restart - restart bot
run     - run as foreground Debug mode. every log will print to screen and log to file.
"""
    argP.add_argument("command", type=str, action="store",
                      choices=['start', 'stop', 'restart', 'run'], help=cmdHelpStr)
    daemon = MainProcess('/tmp/coolq-telegram-bot.pid')
    args = argP.parse_args()
    if args.command == 'start':
        daemon.start(debug_mode=True)
    elif args.command == 'stop':
        daemon.stop()
    elif args.command == 'restart':
        daemon.restart(debug_mode=True)
    elif args.command == 'run':
        # Run as foreground mode
        daemon.run(debug_mode=True)


if __name__ == '__main__':
    main()
