import logging

import global_vars
import telegram
from bot_constant import FORWARD_LIST
from main.command import command_listener

from main.utils import send_both_side

logger = logging.getLogger("CTB.Plugin." + __name__)
logger.debug(__name__ + " loading")

global_vars.create_variable('group_members', [[]] * len(FORWARD_LIST))


def reload_qq_namelist(forward_index: int):
    global_vars.group_members[forward_index] = global_vars.qq_bot.get_group_member_list(group_id=FORWARD_LIST[forward_index]['QQ'])


def reload_all_qq_namelist():
    for i in range(len(FORWARD_LIST)):
        reload_qq_namelist(i)


# register the two functions to global_vars for accessing from other modules
global_vars.create_variable('reload_qq_namelist', reload_qq_namelist)
global_vars.create_variable('reload_all_qq_namelist', reload_all_qq_namelist)


@command_listener('update namelist', 'name', description='update namelist for current group')
def update_namelist(forward_index: int,
                    tg_group_id: int=None,
                    tg_user: telegram.User=None,
                    tg_message_id: int=None,
                    tg_reply_to: telegram.Message=None,
                    qq_group_id: int=None,
                    qq_discuss_id: int=None,
                    qq_user: int=None):

    reload_qq_namelist(forward_index)

    message = 'QQ name list reloaded.'

    return send_both_side(forward_index,
                          message,
                          qq_group_id,
                          qq_discuss_id,
                          tg_group_id,
                          tg_message_id)


reload_all_qq_namelist()
