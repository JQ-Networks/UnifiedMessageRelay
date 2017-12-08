from bot_constant import FORWARD_LIST
import global_vars
from utils import get_forward_index, send_all_except_current
from command import command_listener
from log_calls import log_calls
import telegram

global_vars.create_variable('group_members', [[]] * len(FORWARD_LIST))


@log_calls()
def reload_all_qq_namelist():
    for i in range(len(FORWARD_LIST)):
        global_vars.group_members[i] = global_vars.qq_bot.get_group_member_list(FORWARD_LIST[i]['QQ'])


@command_listener('update namelist', 'un', description='update namelist for current group')
def update_namelist(forward_index: int, tg_group_id: int=None, tg_user: telegram.User=None,
                    tg_message_id: int=None, qq_group_id: int=None, qq_discuss_id: int=None, qq_user: int=None):

    global_vars.group_members[forward_index] = global_vars.qq_bot.get_group_member_list(FORWARD_LIST[forward_index]['QQ'])

    message = 'QQ群名片已重新加载'

    if tg_group_id:
        send_all_except_current(forward_index, message, tg_group_id=tg_group_id)
        global_vars.tg_bot.sendMessage(text=message, reply_to_message_id=tg_message_id)
    elif qq_group_id:
        send_all_except_current(forward_index, message, qq_group_id=qq_group_id)
        return {'reply': message}
    else:
        send_all_except_current(forward_index, message, qq_discuss_id=qq_discuss_id)
        return {'reply': message}


# reload_all_qq_namelist()
