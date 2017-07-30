#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from collections import namedtuple
import re
from pprint import pprint
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, \
    ConversationHandler, RegexHandler, MessageHandler, Filters
from image_operations import *
from short_url import *
from utils import CQ_IMAGE_ROOT, error, reply
from bot_constant import *
from qq_emoji_list import *
from special_sticker_list import *
from cqsdk import CQBot, CQAt, CQImage, RcvdPrivateMessage, RcvdGroupMessage,\
SendGroupMessage


from logger import *
logging.basicConfig(
    filename='bot.log',
    level=logging.DEBUG
)


def message_from_telegram(bot, update):
    """
    处理从 tg 发送过来的消息
    :param bot:
    :param update:
    :return:
    """
    logging.debug(update)
    pprint(update)  # print raw message

    telegram_group_id = update.message.chat_id  # telegram group id
    if telegram_group_id > 0:
        return  # chat id > 0 means private chat, ignore

    qq_group_id = 0  # qq group number
    forward_index = -1  # index of FORWARD_LIST
    for idx, (qq, tg, sticker, drive) in FOWARD_LIST:
        if tg == telegram_group_id:
            qq_group_id = qq
            forward_index = idx
            break
    if qq_group_id == 0:
        return  # no forward rule, return

    sender_name = update.message.from.first_name





def main():
    global job_queue

    updater = Updater(TOKEN)
    job_queue = updater.job_queue

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, ))