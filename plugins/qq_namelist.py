from bot_constant import FORWARD_LIST
import global_vars
from utils import get_forward_index, CQ_GROUP_LIST_ROOT
from cqsdk import SendGroupMessage, GetGroupMemberList, RcvGroupMemberList
from command import command_listener
from CQGroupMemberListInfo import get_group_member_list_info
import os

global_vars.create_variable('group_members', [[]] * len(FORWARD_LIST))

# TODO reconstruct this feature


def reload_all_qq_namelist():
    for forward in FORWARD_LIST:
        global_vars.qq_bot.send(GetGroupMemberList(group=forward['QQ']))


@global_vars.qq_bot.listener(RcvGroupMemberList, 10)  # priority 10
def handle_group_member_list(message):
    with open(os.path.join(CQ_GROUP_LIST_ROOT, message.path.split('\\')[-1]), 'r', encoding='utf-8') as f:
        data = f.read()
    member_list = get_group_member_list_info(data)
    qq_group_id = member_list[0].GroupID
    _, _, forward_index = get_forward_index(qq_group_id=int(qq_group_id))
    global_vars.set_group_members(member_list, index=forward_index)
    return True


@command_listener('[reload namelist]', description='update namelist for current group')
def drive_mode_on(forward_index, tg_group_id, tg_user, qq_group_id, qq):
    global_vars.qq_bot.send(GetGroupMemberList(group=qq_group_id))  # send reload action
    msg = 'QQ群名片已重新加载'
    global_vars.tg_bot.sendMessage(tg_group_id, msg)
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))


reload_all_qq_namelist()
