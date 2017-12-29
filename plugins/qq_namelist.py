from bot_constant import FORWARD_LIST
import global_vars
from utils import send_both_side
from command import command_listener
import telegram
import logging


logger = logging.getLogger("CTBPlugin." + __name__)
logger.debug(__name__ + " loading")

global_vars.create_variable('group_members', [[]] * len(FORWARD_LIST))


def reload_all_qq_namelist():
    for i in range(len(FORWARD_LIST)):
        global_vars.group_members[i] = global_vars.qq_bot.get_group_member_list(group_id=FORWARD_LIST[i]['QQ'])


@command_listener('update namelist', 'name', description='update namelist for current group')
def update_namelist(forward_index: int,
                    tg_group_id: int=None,
                    tg_user: telegram.User=None,
                    tg_message_id: int=None,
                    tg_reply_to: telegram.Message=None,
                    qq_group_id: int=None,
                    qq_discuss_id: int=None,
                    qq_user: int=None):

    global_vars.group_members[forward_index] = global_vars.qq_bot.get_group_member_list(group_id=FORWARD_LIST[forward_index]['QQ'])

    message = 'QQ name list reloaded.'

    return send_both_side(forward_index,
                          message,
                          qq_group_id,
                          qq_discuss_id,
                          tg_group_id,
                          tg_message_id)


reload_all_qq_namelist()
