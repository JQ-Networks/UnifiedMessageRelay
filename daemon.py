#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import queue
import sys
import threading
import time
import traceback
from logging.handlers import RotatingFileHandler

import coloredlogs
from telegram.ext import Updater

# region log

coloredlogs.install(
    fmt='[%(name)s][%(levelname)s] (%(filename)s:%(lineno)d):\n%(message)s\n', level='DEBUG')

# get and conf root logger
rootLogger = logging.getLogger('CTB')
rootLogger.setLevel('DEBUG')

# log main thread
logger = logging.getLogger("CTB.Main")


def log_except_hook(*exc_info):
    # root log hook
    global rootLogger
    exHookLogger = rootLogger.getChild('root')
    text = "".join(traceback.format_exception(*exc_info))
    exHookLogger.error("Unhandled exception: %s", text)


sys.excepthook = log_except_hook

# endregion

# load config
try:
    from bot_constant import *
    from main import utils
    import global_vars
    from cqhttp import CQHttp
    from main.DaemonClass import Daemon
    from main.message_persistence import MessageDB
    from main.file_persistence import FileDB
except ImportError as e:
    # logger.addHandler(logging.StreamHandler())
    logger.critical("Can't import [%s], please check it again." % e.name)
    exit(1)


# log telegram Bot library
# via https://pypi.python.org/pypi/python-telegram-bot#logging
logger_telegram = logging.getLogger('telegram')
# logger_telegram.setLevel(logging.DEBUG)

logger_cqhttp = logging.getLogger('CQHTTP')
if DEBUG_MODE:
    logger_cqhttp.setLevel(logging.DEBUG)
else:
    rootLogger.setLevel(logging.WARNING)


def setup_rotate_handler(logPath: str):
    """
    will save log file in logPath
    :param logPath: path to save log
    :return:
    """
    global rootLogger, logger_telegram
    # rotate file handler: max size: 1MB, so always enable debug mode is ok
    rotate_handler = RotatingFileHandler(
        'bot.log', maxBytes=1048576, backupCount=3)
    standardFormatter = logging.Formatter(
        '[%(asctime)s][%(name)s][%(levelname)s] (%(filename)s:%(lineno)d):\n%(message)s\n')
    rotate_handler.setFormatter(standardFormatter)
    rootLogger.addHandler(rotate_handler)
    logger_telegram.addHandler(rotate_handler)
    logger_cqhttp.addHandler(rotate_handler)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


class MainProcess(Daemon):
    def run(self, debug_mode):
        # TODO Use a variable to set where db file will save.
        global_vars.create_variable('mdb', MessageDB('message.db'))
        global_vars.create_variable('fdb', FileDB('files.db'))
        qq_bot = CQHttp(api_root=API_ROOT,
                        access_token=ACCESS_TOKEN,
                        secret=SECRET,
                        debug_mode=debug_mode)
        global_vars.create_variable('callback_queue', queue.Queue())
        global_vars.qq_bot = qq_bot
        global_vars.tg_bot_id = int(TOKEN.split(':')[0])

        if PROXY_URL:
            updater = Updater(TOKEN, request_kwargs={'proxy_url': PROXY_URL})
        else:
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
                logger.warning(
                    'Could not reach Coolq-http-api, keep waiting...')
                time.sleep(1)
        logger.info('Coolq-http-api status: ok')
        coolq_version = global_vars.qq_bot.get_version_info()['coolq_edition']
        global_vars.create_variable("JQ_MODE", coolq_version == 'pro')
        logger.info(f'Coolq {coolq_version} detected')

        import plugins  # load all plugins

        # Block until the you presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


def main():
    # TODO Use a variable to set where log files will save.
    setup_rotate_handler('bot.log')

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
    global_vars.daemon = daemon # made plugins can stop daemon.
    args = argP.parse_args()
    if args.command == 'start':
        daemon.start(debug_mode=DEBUG_MODE)
    elif args.command == 'stop':
        daemon.stop()
    elif args.command == 'restart':
        daemon.restart(debug_mode=DEBUG_MODE)
    elif args.command == 'run':
        # Run as foreground mode
        logger.debug('Now running in debug mode...')
        daemon.run(debug_mode=True)


if __name__ == '__main__':
    main()
