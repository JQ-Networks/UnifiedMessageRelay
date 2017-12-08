import global_vars

import json
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.ext import MessageHandler, Filters
import telegram
from utils import get_forward_index, get_plugin_priority
from debug import debug_decorator


@debug_decorator
def tg_water_meter(bot, update):
    if update.message:
        message: telegram.Message = update.message
    else:
        message: telegram.Message = update.edited_message

    tg_group_id = message.chat_id  # telegram group id
    forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    if message.forward_from_chat:
        if message.forward_from_chat.type == 'channel':
            if update.message.forward_from_chat.id in global_vars.filter_list['channels']:
                global_vars.drive_mode_on(forward_index, tg_user=message.from_user, tg_group_id=tg_group_id,
                                          tg_message_id=message.id)
                raise DispatcherHandlerStop()

    for keyword in global_vars.filter_list['keywords']:
        if message.caption:
            if keyword in message.caption:
                global_vars.drive_mode_on(forward_index, tg_user=message.from_user, tg_group_id=tg_group_id,
                                          tg_message_id=message.id)
                raise DispatcherHandlerStop()
        elif message.text:
            if keyword in message.text:
                global_vars.drive_mode_on(forward_index, tg_user=message.from_user, tg_group_id=tg_group_id,
                                          tg_message_id=message.id)
                raise DispatcherHandlerStop()


global_vars.dp.add_handler(MessageHandler(Filters.all, tg_water_meter), get_plugin_priority(__name__))