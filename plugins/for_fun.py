from command import command_listener
import global_vars
from utils import get_full_user_name, get_forward_index
from telegram.ext.dispatcher import DispatcherHandlerStop
from cqsdk import SendGroupMessage


@command_listener('[dice]', tg_only=True, description='throw a dice')
def send_group_id(tg_group_id, tg_user):
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    if forward_index == -1:
        raise DispatcherHandlerStop()
    username = get_full_user_name(tg_user)
    msg = username + ': [CQ:dice]'
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))


@command_listener('[rps]', tg_only=True, description='rock paper stone')
def send_group_id(tg_group_id, tg_user):
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    if forward_index == -1:
        raise DispatcherHandlerStop()
    username = get_full_user_name(tg_user)
    msg = username + ': [CQ:rps]'
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))

