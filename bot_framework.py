#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import logging
import threading
import traceback

from enum import Enum
from telegram.ext import Updater, MessageHandler, Filters

logging.basicConfig(filename='bot.log', level=logging.INFO)

# global_vars.set_tg_bot_id(int(TOKEN.split(':')[0]))


TG_TYPES = ('photo', 'video', 'audio', 'document', 'sticker', 'text')


class TgTypes(Enum):  # only useful for auto completion
    photo = 'photo'
    video = 'video'
    audio = 'audio'
    document = 'document'
    sticker = 'sticker'
    text = 'text'


class TGMessageHandler:
    def __init__(self, type, handler):
        self.type = type
        self.handler = handler


class TGBot:
    def __init__(self, token):
        self.listeners = {}
        for _type in TG_TYPES:
            self.listeners[_type] = []
        self.job_queue = None
        self.tg_bot = None
        self.token = token
        self.updater = None

    def start(self):
        threaded_server = threading.Thread(
            target=self.server.serve_forever,
            daemon=True)
        threaded_server.start()

        # wait for socket thread to init
        time.sleep(1)

    def serve_forever(self):
        self.updater = Updater(self.token)
        self.job_queue = self.updater.job_queue
        self.tg_bot = self.updater.bot
        # global_vars.set_tg_bot(self.tg_bot)

        # Get the dispatcher to register handlers
        dp = self.updater.dispatcher

        dp.add_handler(MessageHandler(Filters.text | Filters.command, self.message_handler_generator('text')))
        dp.add_handler(MessageHandler(Filters.sticker, self.message_handler_generator('sticker')))
        dp.add_handler(MessageHandler(Filters.audio, self.message_handler_generator('audio')))
        dp.add_handler(MessageHandler(Filters.photo, self.message_handler_generator('photo')))
        dp.add_handler(MessageHandler(Filters.document, self.message_handler_generator('document')))
        dp.add_handler(MessageHandler(Filters.video, self.message_handler_generator('video')))
        # Start the Bot
        self.updater.start_polling(poll_interval=1.0, timeout=200)

        # Block until the you presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()

    def message_handler_generator(self, tg_type):
        def message_handler(bot, update):
            original_self = self
            # tg_group_id = update.message.chat_id  # telegram group id
            # if tg_group_id > 0:
            #     return  # chat id > 0 means private chat, ignore
            #
            # qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
            # if forward_index == -1:
            #     return

            for listener in original_self.listeners[tg_type]:
                try:
                    if listener.handler(update):
                        break
                except:
                    traceback.print_exc()
        return message_handler

    def listener(self, tg_type):
        def decorator(handler):
            self.listeners.append(TGMessageHandler(tg_type, handler))
        return decorator


if __name__ == '__main__':
    tgbot = TGBot('123123123:test')


    @tgbot.listener(TgTypes.text)
    def log(update):
        print(update.message)

    tgbot.start()
    input()
