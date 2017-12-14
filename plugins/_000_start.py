from telegram.ext import CommandHandler
import global_vars
from utils import get_plugin_priority
import logging


logger = logging.getLogger("CTBPlugin." + __name__)
logger.debug(__name__ + " loading")


def start(bot, update):
    update.message.reply_text('This is a QQ <-> Telegram Relay bot, '
                              'source code is available on [Github](https://github.com/jqqqqqqqqqq/coolq-telegram-bot)'
                              , parse_mode='Markdown')


global_vars.dp.add_handler(CommandHandler('start', start), group=get_plugin_priority(__name__))
