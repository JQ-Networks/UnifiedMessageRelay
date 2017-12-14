import global_vars
from command import command_listener
import telegram
import logging


logger = logging.getLogger("CTBPlugin." + __name__)
logger.debug(__name__ + " loading")


@command_listener('show group id', 'id', tg_only=True, description='show current telegram group id')
def show_tg_group_id(tg_group_id: int, tg_user: telegram.User, tg_message_id: int):
    msg = 'Telegram group id is: ' + str(tg_group_id)
    global_vars.tg_bot.sendMessage(tg_group_id, msg)


@command_listener('show group id', 'id', qq_only=True, description='show current telegram group id')
def show_qq_group_id(qq_group_id: int, qq_discuss_id:int, qq_user: int):
    if qq_group_id:
        msg = 'QQ group id is: ' + str(qq_group_id)
        return {'reply': msg}
    else:
        msg = 'QQ discuss id is: ' + str(qq_discuss_id)
        return {'reply': msg}

