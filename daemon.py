#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import queue
import threading
import coloredlogs
import time
from logging.handlers import RotatingFileHandler
from cqhttp import Error

from telegram.ext import CommandHandler, Updater

# region log

coloredlogs.install(fmt='[%(name)s][%(levelname)s] (%(filename)s:%(lineno)d):\n%(message)s\n', level='DEBUG')


# rotate file handler: max size: 1MB, so always enable debug mode is ok

rotate_handler = RotatingFileHandler(
    'bot.log', maxBytes=1048576, backupCount=3)
standardFormatter = logging.Formatter(
    '[%(name)s][%(levelname)s] (%(filename)s:%(lineno)d):\n%(message)s\n')
rotate_handler.setFormatter(standardFormatter)

# log main thread
logger = logging.getLogger("CTBMain")
# logger.setLevel(logging.DEBUG)
logger.addHandler(rotate_handler)

# log plugins
logger_plugins = logging.getLogger("CTBPlugin")
# logger_plugins.setLevel(logging.DEBUG)
logger.addHandler(rotate_handler)

# log telegram Bot library

# via https://pypi.python.org/pypi/python-telegram-bot#logging
logger_telegram = logging.getLogger('telegram')
# logger_telegram.setLevel(logging.DEBUG)
logger_telegram.addHandler(rotate_handler)

# endregion

# load config
try:
    from bot_constant import *
    import utils
    import global_vars
    from cqhttp import CQHttp
    from DaemonClass import Daemon
    from message_persistence import MessageDB
except ImportError as e:
    logger.addHandler(logging.StreamHandler())
    logger.critical("Can't import %s, please check it again." % e.name)
    exit(1)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


class MainProcess(Daemon):
    def run(self):
        global_vars.create_variable('mdb', MessageDB('message.db'))
        qq_bot = CQHttp(api_root=API_ROOT,
                        access_token=ACCESS_TOKEN,
                        secret=SECRET)
        global_vars.create_variable('callback_queue', queue.Queue())
        global_vars.qq_bot = qq_bot
        global_vars.tg_bot_id = int(TOKEN.split(':')[0])

        updater = Updater(TOKEN)
        global_vars.create_variable('job_queue', updater.job_queue)
        global_vars.tg_bot = updater.bot
        # Get the dispatcher to register handlers
        dp = updater.dispatcher
        global_vars.dp = dp
        dp.add_error_handler(error)

        updater.start_polling(poll_interval=1.0, timeout=200)

        threaded_server = threading.Thread(
            target=qq_bot.run,
            kwargs=dict(host=HOST, port=PORT),
            daemon=True)
        threaded_server.start()

        should_wait = True
        while should_wait:
            try:
                bot_status = qq_bot.get_status()
                should_wait = False
            except Exception as e:
                logger.warning('Could not reach Coolq-http-api, keep waiting...')
                time.sleep(1)
        logger.debug('Coolq-http-api status: ok')

        import plugins  # load all plugins

        # Block until the you presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


def main():
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
        daemon.start()
    elif args.command == 'stop':
        daemon.stop()
    elif args.command == 'restart':
        daemon.restart()
    elif args.command == 'run':
        # logger.setLevel(logging.DEBUG)
        # logger_plugins.setLevel(logging.DEBUG)
        # logger_telegram.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        logger.addHandler(stream_handler)
        logger_plugins.addHandler(stream_handler)
        logger_telegram.addHandler(stream_handler)
        logger.info('Now running in debug mode...')
        daemon.run()


if __name__ == '__main__':
    main()
