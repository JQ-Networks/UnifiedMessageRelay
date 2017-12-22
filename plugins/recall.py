from command import command_listener
from utils import get_forward_index, send_from_tg_to_qq
from telegram.ext.dispatcher import DispatcherHandlerStop
import telegram
import logging
import global_vars


logger = logging.getLogger("CTBPlugin." + __name__)
logger.debug(__name__ + " loading")


@command_listener('recall', 'del', tg_only=True, description='recall a message')
def recall(tg_group_id: int,
         tg_user: telegram.User,
         tg_message_id: int):
    forward_index = get_forward_index(tg_group_id=tg_group_id)
    if forward_index == -1:
        raise DispatcherHandlerStop()

    saved_message = global_vars.mdb.retrieve_message(tg_message_id, forward_index)
    if not saved_message:
        global_vars.tg_bot.sendMessage(chat_id=tg_group_id,
                                       text='message not recallable.',
                                       reply_to_message_id=tg_message_id)
        return ''
    qq_message_id = saved_message[1]
    global_vars.qq_bot.delete_msg(message_id=qq_message_id)
    global_vars.tg_bot.sendMessage(chat_id=tg_group_id,
                                   text='message recalled.',
                                   reply_to_message_id=tg_message_id)