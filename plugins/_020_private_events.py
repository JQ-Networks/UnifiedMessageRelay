import logging

import global_vars
from bot_constant import FORWARD_LIST, QQ_BOT_ID

from main.utils import get_plugin_priority, get_qq_name_encoded

logger = logging.getLogger("CTB." + __name__)
logger.debug(__name__ + " loading")


@global_vars.qq_bot.on_event('friend_add', group=get_plugin_priority(__name__))
def handle_group_upload(context):
    user_id = context.get('user_id')

    logger.debug(context)

    qq_name = get_qq_name_encoded(user_id)

    result = f'<b>{qq_name}</b> sent a 📎group file: {file["name"]}. Please view it on QQ.'
    global_vars.tg_bot.sendMessage(chat_id=FORWARD_LIST[forward_index]['TG'],
                                   text=result,
                                   parse_mode='HTML')

    return ''