#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bot_constant import *
import global_vars

from telegram.ext import Updater, CommandHandler

import logging
from logging.handlers import RotatingFileHandler
from DaemonClass import Daemon
import threading
import sys
from message_persistence import MessageDB

from cqhttp import CQHttp

# region log

# log main thread
logger = logging.getLogger("CTBMain")
logger.setLevel(logging.DEBUG)
rHandler = RotatingFileHandler(
    'bot.log', maxBytes=1048576, backupCount=3)
standardFormatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s - %(module)s(%(filename)s) : %(message)s")
rHandler.setFormatter(standardFormatter)
logger.addHandler(rHandler)

# log plugins
logger_plugins = logging.getLogger("CTBPlugin")
logger_plugins.setLevel(logging.DEBUG)
logger.addHandler(rHandler)

# log telegram

logger_telegram = logging.getLogger()
logger_telegram.setLevel(logging.DEBUG)
logger_telegram.addHandler(rHandler)

# endregion


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


class MainProcess(Daemon):
    def run(self):
        global_vars.create_variable('mdb', MessageDB('message'))
        for key, value in global_vars.mdb.items():
            logger.debug(key, value)

        qq_bot = CQHttp(api_root=API_ROOT,
                        access_token=ACCESS_TOKEN,
                        secret=SECRET)

        global_vars.qq_bot = qq_bot
        global_vars.tg_bot_id = int(TOKEN.split(':')[0])

        updater = Updater(TOKEN)
        job_queue = updater.job_queue
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

        import plugins  # load all plugins

        # Block until the you presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


def main():
    daemon = MainProcess('/tmp/coolq-telegram-bot.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'run' == sys.argv[1]:
            logger.setLevel(logging.DEBUG)
            logger_plugins.setLevel(logging.DEBUG)
            sH=logging.StreamHandler()
            sH.setFormatter(standardFormatter)
            logger.addHandler(sH)
            logger_plugins.addHandler(sH)
            logger_telegram.addHandler(sH)
            logger.info('Now running in debug mode...')
            daemon.run()
        else:
            logger.error('error processing command')
            print("usage: %s start|stop|restart|run" % sys.argv[0])
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart|run" % sys.argv[0])
        sys.exit(2)


if __name__ == '__main__':
    main()
