import logging

import global_vars
import telegram
from main.command import command_listener

from main.utils import get_forward_index, recall_message

logger = logging.getLogger("CTB.Plugin." + __name__)
logger.debug(__name__ + " loading")


@command_listener('recall', 'del', tg_only=True, description='recall a message')
def recall(tg_group_id: int,
           tg_user: telegram.User,
           tg_message_id: int,
           tg_reply_to: telegram.Message):
    forward_index = get_forward_index(tg_group_id=tg_group_id)
    if forward_index == -1:
        return

    result = recall_message(forward_index, tg_reply_to)

    if result == -1:
        text = 'Please refer to a message.'
    elif result == -2:
        text = 'Message not recallable.'
    elif result == -3:
        text = 'Recalling messages from other QQ users is not supported.',
    elif result == -4:
        text = 'Message sent more than two minutes ago. Recalling failed.'
    else:
        text = 'Message recalled.'

    global_vars.tg_bot.sendMessage(chat_id=tg_group_id,
                                   text=text,
                                   reply_to_message_id=tg_message_id)
