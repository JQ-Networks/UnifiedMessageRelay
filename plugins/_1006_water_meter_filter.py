import global_vars
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.ext import MessageHandler, Filters
import telegram
from utils import get_forward_index, get_plugin_priority
import logging


logger = logging.getLogger("CTBPlugin." + __name__)
logger.debug(__name__ + " loading")


def tg_water_meter(bot: telegram.Bot,
                   update: telegram.Update):
    if update.message:
        message: telegram.Message = update.message
    else:
        message: telegram.Message = update.edited_message

    tg_group_id = message.chat_id  # telegram group id
    forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    logger.debug("Water meter processing")
    if message.forward_from_chat:
        if message.forward_from_chat.type == 'channel':
            logger.debug("message is forward from channel")
            if update.message.forward_from_chat.id in global_vars.filter_list['channels']:
                logger.debug("message is blocked")
                global_vars.drive_mode_on(forward_index,
                                          tg_user=message.from_user,
                                          tg_group_id=tg_group_id,
                                          tg_message_id=message.message_id)
                raise DispatcherHandlerStop()

    for keyword in global_vars.filter_list['keywords']:
        if message.caption:
            if keyword in message.caption:
                logger.debug("message is blocked")
                global_vars.drive_mode_on(forward_index,
                                          tg_user=message.from_user,
                                          tg_group_id=tg_group_id,
                                          tg_message_id=message.message_id)
                raise DispatcherHandlerStop()
        elif message.text:
            if keyword in message.text:
                logger.debug("message is blocked")
                global_vars.drive_mode_on(forward_index,
                                          tg_user=message.from_user,
                                          tg_group_id=tg_group_id,
                                          tg_message_id=message.message_id)
                raise DispatcherHandlerStop()


global_vars.dp.add_handler(MessageHandler(Filters.all & Filters.group,
                                          tg_water_meter),
                           get_plugin_priority(__name__))
