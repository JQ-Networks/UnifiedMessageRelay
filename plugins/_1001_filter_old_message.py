import global_vars
from utils import get_plugin_priority
from telegram.ext import MessageHandler, Filters
from telegram.ext.dispatcher import DispatcherHandlerStop
import datetime
import logging
import telegram


logger = logging.getLogger("CTBPlugin." + __name__)
logger.debug(__name__ + " loading")

# Telegram messages will expire in 60 seconds if bot isn't running
# So other chat session won't be spammed when bot stops and then starts
# If you want to keep all message synced, please simply disable this plugin.


def ignore_old_message(bot: telegram.Bot,
                       update: telegram.Update):  # ignore old message that are more than 60s ago

    if (datetime.datetime.now() - update.message.date).total_seconds() > 60:
        logger.debug('Telegram message ignored: sent more than 60 seconds ago')
        raise DispatcherHandlerStop()


global_vars.dp.add_handler(MessageHandler(Filters.all & Filters.group,
                                          ignore_old_message),
                           get_plugin_priority(__name__))
