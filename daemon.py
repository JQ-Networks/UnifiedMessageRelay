#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import queue
import threading
import time
from logging.handlers import RotatingFileHandler
from cqhttp import Error

from telegram.ext import CommandHandler, Updater

# region log

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# The background is set with 40 plus the number of the color, and the foreground with 30

# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


class ColoredLogger(logging.Logger):
    FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s] ($BOLD%%(module)s(filename)s$RESET:%(lineno)d): %(message)s"
    COLOR_FORMAT = formatter_message(FORMAT, True)

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.DEBUG)

        color_formatter = ColoredFormatter(self.COLOR_FORMAT)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        self.addHandler(console)
        return


# rotate file handler: max size: 1MB, so always enable debug mode is ok
rHandler = RotatingFileHandler(
    'bot.log', maxBytes=1048576, backupCount=3)
logging.setLoggerClass(ColoredLogger)

# log main thread
logger = logging.getLogger("CTBMain")
logger.setLevel(logging.DEBUG)
logger.addHandler(rHandler)

# log plugins
logger_plugins = logging.getLogger("CTBPlugin")
logger_plugins.setLevel(logging.DEBUG)
logger.addHandler(rHandler)

# log telegram Bot library

# via https://pypi.python.org/pypi/python-telegram-bot#logging
logger_telegram = logging.getLogger('telegram')
logger_telegram.setLevel(logging.DEBUG)
logger_telegram.addHandler(rHandler)

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

        try:
            bot_status = qq_bot.get_status()
        except Exception as e:
            logger.error('Could not reach Coolq-http-api, please check Coolq plugins.')
            exit(-1)
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
        logger.setLevel(logging.DEBUG)
        logger_plugins.setLevel(logging.DEBUG)
        logger_telegram.setLevel(logging.DEBUG)
        sH = logging.StreamHandler()
        logger.addHandler(sH)
        logger_plugins.addHandler(sH)
        logger_telegram.addHandler(sH)
        logger.info('Now running in debug mode...')
        daemon.run()


if __name__ == '__main__':
    main()
