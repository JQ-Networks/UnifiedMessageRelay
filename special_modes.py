from bot_constant import *
from cqsdk import SendGroupMessage
import global_vars


def get_forward_index(qq_group_id=0, tg_group_id=0):
    """
    Get forward index from FORWARD_LIST
    :param qq_group_id: optional, the qq group id, either this or tg_group_id must be valid
    :param tg_group_id: optional, the telegram group id, either this or qq_group_id must be valid
    :return: qq_group_id, tg_group_id, forward_index
    """
    for idx, (qq, tg, sticker, drive) in enumerate(FORWARD_LIST):
        if tg == tg_group_id or qq == qq_group_id:
            return qq, tg, idx
    return 0, 0, -1  # -1 is not found


def set_sticker_link_mode(forward_index, status, tg_group_id, qq_group_id):
    """
    set sticker link mode on/off
    :param forward_index: the index of FORWARD_LIST
    :param status: True: enable, False: disable
    :param bot:
    :param tg_group_id:
    :param qq_group_id:
    """
    if status:
        msg = 'Telegram Sticker图片链接已启用'
    else:
        msg = 'Telegram Sticker图片链接已禁用'
    FORWARD_LIST[forward_index][3] = status
    global_vars.tg_bot.sendMessage(tg_group_id, msg)
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))


def get_sticker_link_mode(forward_index):
    return FORWARD_LIST[forward_index][3]


def set_drive_mode(forward_index, status, tg_group_id, qq_group_id):
    """
    set drive mode on/off
    :param forward_index: the index of FORWARD_LIST
    :param status: True: enable, False: disable
    :param bot:
    :param tg_group_id:
    :param qq_group_id:
    """
    if status:
        msg = 'Telegram向QQ转发消息已暂停'
    else:
        msg = 'Telegram向QQ转发消息已重启'
    FORWARD_LIST[forward_index][2] = status
    global_vars.tg_bot.sendMessage(tg_group_id, msg)
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))


def get_drive_mode(forward_index):
    return FORWARD_LIST[forward_index][2]
