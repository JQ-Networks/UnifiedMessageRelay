import logging

import global_vars
import telegram
from telegram.ext import MessageHandler, Filters
from telegram.ext.dispatcher import DispatcherHandlerStop

from main.utils import get_forward_index, get_plugin_priority

logger = logging.getLogger("CTB." + __name__)
logger.debug(__name__ + " loading")


def tg_water_meter(bot: telegram.Bot,
                   update: telegram.Update):
    if update.message:
        message: telegram.Message = update.message
    else:
        message: telegram.Message = update.edited_message

    tg_group_id = message.chat_id  # telegram group id
    forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    if message.forward_from_chat and message.forward_from_chat.type == 'channel':
        if update.message.forward_from_chat.id in global_vars.filter_list['channels']:
            logger.debug('Message ignored: matched water meter channels')
            global_vars.drive_mode_on(forward_index,
                                      tg_user=message.from_user,
                                      tg_group_id=tg_group_id,
                                      tg_message_id=message.message_id)
            raise DispatcherHandlerStop()

    message_text = ''
    if message.caption:
        message_text = message.caption
    elif message.text:
        message_text = message.text
    if message.from_user.id in global_vars.filter_list['users']:
        logger.debug('Message ignored: matched filtered user')
        raise DispatcherHandlerStop()
    if not message_text:
        return
    for keyword in global_vars.filter_list['keywords']:
        if keyword in message_text:
            logger.debug('Message ignored: matched water meter keywords')
            update.message.reply_text("Keyword detected, won't forward to QQ Group(keyword: " + keyword + ")")
            raise DispatcherHandlerStop()


global_vars.dp.add_handler(MessageHandler(Filters.all & Filters.group,
                                          tg_water_meter,
                                          edited_updates=True),
                           get_plugin_priority(__name__))