import global_vars
from utils import get_forward_index
from telegram.ext import MessageHandler, Filters
from telegram.ext.dispatcher import DispatcherHandlerStop
import datetime


def ignore_old_message(bot, update):  # ignore old message that are more than 60s ago
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))

    if (datetime.datetime.now() - update.message.date).total_seconds() > 60:
        raise DispatcherHandlerStop()


global_vars.dp.add_handler(MessageHandler(Filters.all, ignore_old_message), 5)  # priority 5