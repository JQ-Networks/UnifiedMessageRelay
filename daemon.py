#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bot_constant import *
import global_vars
from cqsdk import CQBot, CQAt, CQImage, RcvdPrivateMessage, RcvdGroupMessage,\
    SendGroupMessage, GetGroupMemberList, RcvGroupMemberList
from telegram.ext import Updater, CommandHandler, InlineQueryHandler,\
    ConversationHandler, RegexHandler, MessageHandler, Filters
import telegram.ext
import logging

logger = logging.getLogger(__name__)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    qq_bot = CQBot(CQ_PORT)
    tg_bot = None
    global_vars.set_qq_bot(qq_bot)
    global_vars.set_tg_bot_id(int(TOKEN.split(':')[0]))

    updater = Updater(TOKEN)
    job_queue = updater.job_queue
    tg_bot = updater.bot
    global_vars.set_tg_bot(tg_bot)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    global_vars.set_dp(dp)
    dp.add_error_handler(error)

    import plugins

    qq_bot.start()
    updater.start_polling(poll_interval=1.0, timeout=200)
    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
