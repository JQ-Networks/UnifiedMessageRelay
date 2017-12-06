#!/use/bin/env python3

import os
import sys
import threading
import traceback
import requests
from cqsdk import SendGroupMessage
from bot_constant import *
import telegram
import global_vars
import re
from typing import Union

CQ_IMAGE_ROOT = os.path.join(CQ_ROOT, r'data/image')
CQ_GROUP_LIST_ROOT = os.path.join(CQ_ROOT, r'app/org.dazzyd.cqsocketapi/GroupListCache')


def info(*args, **kwargs):
    print("================ INFO  ================", file=sys.stderr)
    print(*args, **kwargs, file=sys.stderr)


def error(*args, **kwargs):
    print("================ ERROR ================", file=sys.stderr)
    print(*args, **kwargs, file=sys.stderr)


class FileDownloader(threading.Thread):
    def __init__(self, url, path, requests_kwargs={}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url
        self.path = path
        self.requests_kwargs = requests_kwargs

    def run(self):
        try:
            self.download()
        except:
            error("[FileDownloader]", "Catch exception on downloading.")
            traceback.print_exc()

    def download(self):
        if os.path.exists(self.path):
            print("[FileDownloader]", "Exists", self.path)
            return
        r = requests.get(self.url, **self.requests_kwargs)
        with open(self.path, 'wb') as f:
            f.write(r.content)


# Message attributing functions
# Below this line is the user name processing function used by mybot.py

def get_full_user_name(user: telegram.User):
    """
    Combine user's first name and last name
    :param user: the user which you want to extract name from
    :return: combined user name
    """
    if not user:
        return ''
    name = user.first_name
    if user.last_name:
        name += ' ' + user.last_name
    return name


def get_forward_from(message: telegram.Message):
    """
    Combine forwarded user's first name and last name and format into (forwarded from xxx)
    :param message: the forwarded message
    :return: combined (forwarded from xxx)
    """
    if not message.forward_from:
        return ''
    result = get_full_user_name(message.forward_from)
    if message.forward_from.id == global_vars.tg_bot_id:
        if message.caption:
            message_text = message.caption
        elif message.text:
            message_text = message.text
        else:
            message_text = ''
        right_end = message_text.find(':')
        if right_end != -1:
            result = message_text[:right_end]
        # msg_parts = message_text.split(':')
        # if len(msg_parts) >= 2:
        #     result = msg_parts[0]
    return '(↩' + result + ')'


def get_reply_to(reply_to_message: telegram.Message):
    """
    Combine replied user's first name and last name and format into (reply to from xxx)
    :param reply_to_message: the replied message
    :return: combined (reply to from xxx)
    """
    if not reply_to_message or not reply_to_message.from_user:
        return ''
    reply_to = get_full_user_name(reply_to_message.from_user)
    if reply_to_message.from_user.id == global_vars.tg_bot_id:
        if reply_to_message.caption:
            message_text = reply_to_message.caption
        elif reply_to_message.text:
            message_text = reply_to_message.text
        else:
            message_text = ''
        right_end = message_text.find(':')
        if right_end != -1:
            reply_to = message_text[:right_end]
        # message_parts = message_text.split(':')
        # if len(message_parts) >= 2:
        #     reply_to = message_parts[0]
    return '(→' + reply_to + ')'


def get_forward_index(qq_group_id=None, qq_discuss_id=None, tg_group_id=None):  # TODO: reconstruction
    """
    Get forward index from FORWARD_LIST
    :param qq_group_id: optional, the qq group id, either this or tg_group_id must be valid
    :param tg_group_id: optional, the telegram group id, either this or qq_group_id must be valid
    :return: qq_group_id, tg_group_id, forward_index
    """
    for idx, forward in enumerate(FORWARD_LIST):
        if forward['TG'] == tg_group_id or forward['QQ'] == qq_group_id:
            return forward['QQ'], forward['TG'], idx
    return 0, 0, -1  # -1 is not found


def decode_cq_escape(text):
    return text.replace('&amp;', '&').replace('&#91;', '[').replace('&#93;', ']').replace('&#44;', ',')


EMOJI_LIST = [10000035] + \
             list(range(10000048, 10000058)) + \
             [126980, 127183, 127344, 127345, 127358, 127359, 127374] + \
             list(range(127377, 127387)) + \
             [127489, 127490, 127514, 127535] + \
             list(range(127538, 127547)) + \
             [127568, 127569] + \
             list(range(127744, 127777)) + \
             list(range(127792, 127798)) + \
             list(range(127799, 127869)) + \
             list(range(127872, 127892)) + \
             list(range(127904, 127941)) + \
             list(range(127942, 127947)) + \
             list(range(127968, 127985)) + \
             list(range(128000, 128063)) + \
             [128064] + \
             list(range(128066, 128248)) + \
             [128249, 128250, 128251, 128252] + \
             list(range(128256, 128318)) + \
             list(range(128336, 128360)) + \
             list(range(128507, 128577)) + \
             list(range(128581, 128592)) + \
             list(range(128640, 128710)) + \
             [8252, 8265, 8482, 8505] + \
             list(range(8596, 8602)) + \
             [8617, 8618, 8986, 8987] + \
             list(range(9193, 9197)) + \
             [9200, 9203, 9410, 9642, 9643, 9654, 9664] + \
             list(range(9723, 9727)) + \
             [9728, 9729, 9742, 9745, 9748, 9749, 9757, 9786] + \
             list(range(9800, 9812)) + \
             [9824, 9827, 9829, 9830, 9832, 9851, 9855, 9875, 9888, 9889, 9898, 9899, 9917, 9918, 9924, 9925, 9934, 9940, 9962, 9970, 9971, 9973, 9978, 9981, 9986, 9989] + \
             list(range(9992, 9997)) + \
             [9999, 10002, 10004, 10006, 10024, 10035, 10036, 10052, 10055, 10060, 10062, 10067, 10068, 10069, 10071, 10084, 10133, 10134, 10135, 10145, 10160, 10175, 10548, 10549, 11013, 11014, 11015, 11035, 11036, 11088, 11093, 12336, 12349, 12951, 12953, 58634]


def emoji_to_cqemoji(text):
    """
    according to coolq rules, chars in EMOJI_LIST should be encoded.
    :param text:
    :return:
    """
    new_text = ''
    for char in text:
        if (8252 <= ord(char) < 12287 or 126980 < ord(char) < 129472) and ord(char) in EMOJI_LIST:
            new_text += "[CQ:emoji,id=" + str(ord(char)) + "]"
        else:
            new_text += char
    return new_text


def trim_emoji(text):
    """
    some api cannot use cqemoji, so trim it
    :param text:
    :return:
    """
    new_text = ''
    for char in text:
        if (8252 <= ord(char) < 12287 or 126980 < ord(char) < 129472) and ord(char) in EMOJI_LIST:
            pass
        else:
            new_text += char
    return new_text


def cq_send(update: telegram.Update, text: str, qq_group_id: int, edited: bool = False):
    """
    send telegram message to qq with forward of reply support
    :param update: telegram.Update
    :param text: text to send, in coolq format
    :param qq_group_id: which group to send
    :param edited: add '✎' icon
    """
    if edited:
        sender_name = get_full_user_name(update.edited_message.from_user)
        forward_from = get_forward_from(update.edited_message)
        reply_to = get_reply_to(update.edited_message.reply_to_message)
    else:
        sender_name = get_full_user_name(update.message.from_user)
        forward_from = get_forward_from(update.message)
        reply_to = get_reply_to(update.message.reply_to_message)

    # get real sender from telegram message
    if forward_from and update.message.forward_from.id == global_vars.tg_bot_id:
        left_start = text.find(': ')
        if left_start != -1:
            text = text[left_start + 2:]
    text = emoji_to_cqemoji(text)

    if edited:
        edit_mark = ' ✎ '
    else:
        edit_mark = ''

    global_vars.qq_bot.send(SendGroupMessage(
        group=qq_group_id,
        text=sender_name + reply_to + forward_from + edit_mark + ': ' + text
    ))


def get_qq_name(qq_number: int, forward_index: int):
    """
    convert qq number into group card or nickname(if don't have a group card)
    :param qq_number: qq number
    :param forward_index: index of FORWARD_LIST
    :return: group card, nickname(if no group card set), or qq number(if both not found)
    """
    for group_member in global_vars.group_members[forward_index]:
        # group_member: CQGroupMemberInfo
        if group_member.QQID == qq_number:
            return group_member.Card if group_member.Card else group_member.Nickname
    return str(qq_number)


priority = re.compile(r'_(\d+)_*')


def get_plugin_priority(name):
    """
    calculate the priority of the plugin
    :param name: plugin's __name__
    :return: calculated priority
    """
    return int(priority.findall(name)[0])


def send_all(forward_index, message):
    """
    forward message to all other sessions
    :param message:
    :return:
    """
    pass


def send_all_except_current(forward_index: int, message: Union[list, str], qq_group_id: int = 0,
                            qq_discuss_id: int = 0, qq_user: int=None, tg_group_id: int = 0,
                            tg_user: telegram.User=None, tg_forward_from: telegram.User=None,
                            tg_reply_to:telegram.User=None, edited: bool=False, auto_escape: bool=True):
    pass