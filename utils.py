#!/use/bin/env python3

import os
import sys
import threading
import traceback
import requests
from bot_constant import *
import telegram
import global_vars
import re
from typing import Union
from cq_utils import qq_emoji_list, qq_sface_list, cq_get_pic_url, cq_download_pic,\
    cq_location_regex, CQ_IMAGE_ROOT, error
from log_calls import log_calls

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
    if not message:
        return ''
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
            return idx
    return -1  # -1 is not found


def get_qq_name(qq_number: int, forward_index: int):
    """
    convert qq number into group card or nickname(if don't have a group card)
    :param qq_number: qq number
    :param forward_index: index of FORWARD_LIST
    :return: group card, nickname(if no group card set), or qq number(if both not found)
    """
    for group_member in global_vars.group_members[forward_index]:
        if group_member['user_id'] == qq_number:
            return group_member['card'] if group_member.get('card') else group_member['nickname']
    return str(qq_number)


priority = re.compile(r'_(\d+)_*')


def get_plugin_priority(name):
    """
    calculate the priority of the plugin
    :param name: plugin's __name__
    :return: calculated priority
    """
    return int(priority.findall(name)[0])


def extract_mqqapi(link):
    locations = cq_location_regex.findall(link)  # [('lat', 'lon', 'name', 'addr')]
    return locations[0], locations[1], locations[2], locations[3]


def send_all(forward_index, message):
    """
    currently not used
    forward message to all other sessions
    :param message:
    :return:
    """
    pass


def send_all_except_current(forward_index: int, message: Union[list, str], qq_group_id: int = 0,
                            qq_discuss_id: int = 0, qq_user: int=None, tg_group_id: int = 0,
                            tg_user: telegram.User=None, tg_forward_from: telegram.Message=None,
                            tg_reply_to:telegram.Message=None, edited: bool=False, auto_escape: bool=True):
    if tg_group_id:
        sender_name = get_full_user_name(tg_user)
        forward_from = get_forward_from(tg_forward_from)
        reply_to = get_reply_to(tg_reply_to)

        if edited:
            edit_mark = ' ✎ '
        else:
            edit_mark = ''

        if forward_from and tg_forward_from.from_user.id == global_vars.tg_bot_id:
            if isinstance(message, str):
                left_start = message.find(': ')
                if left_start != -1:
                    message = message[left_start + 2:]
            else:
                if message[0]['data'].get('text'):
                    left_start = message[0]['data']['text'].find(': ')
                    if left_start != -1:
                        message[0]['data']['text'] = message[0]['data']['text'][left_start + 2:]
                elif len(message) == 2:
                    if message[1]['data'].get('text'):
                        left_start = message[1]['data']['text'].find(': ')
                        if left_start != -1:
                            message[1]['data']['text'] = message[1]['data']['text'][left_start + 2:]

        if isinstance(message, str):
            message = sender_name + reply_to + forward_from + edit_mark + ': ' + message
        else:
            if message[0]['data'].get('text'):
                message[0]['data']['text'] = sender_name + reply_to + forward_from + edit_mark + ': ' + message[0]['data']['text']
            elif len(message) == 2:
                if message[1]['data'].get('text'):
                    message[1]['data']['text'] = sender_name + reply_to + forward_from + edit_mark + ': ' + message[1]['data']['text']
            else:
                text = sender_name + reply_to + forward_from + edit_mark + ': '
                message.append({
                    'type': 'text',
                    'data': {'text': text}
                })

        if FORWARD_LIST[forward_index].get('QQ'):
            if isinstance(FORWARD_LIST[forward_index]['QQ'], int):
                global_vars.qq_bot.send_group_msg(group_id=FORWARD_LIST[forward_index]['QQ'], message=message, auto_escape=auto_escape)
            else:
                for group in FORWARD_LIST[forward_index]['QQ']:
                    global_vars.qq_bot.send_group_msg(group_id=group, message=message, auto_escape=auto_escape)

        if FORWARD_LIST[forward_index].get('DISCUSS'):
            if isinstance(FORWARD_LIST[forward_index]['DISCUSS'], int):
                global_vars.qq_bot.send_discuss_msg(discuss_id=FORWARD_LIST[forward_index]['DISCUSS'], message=message, auto_escape=auto_escape)
            else:
                for discuss in FORWARD_LIST[forward_index]['DISCUSS']:
                    global_vars.qq_bot.send_discuss_msg(discuss_id=discuss, message=message, auto_escape=auto_escape)

    else:

        pending_text = ''
        pending_image = ''

        message_list = list()
        if isinstance(message, str):  # message from qq will never be str, due to settings of cq http api
            pass  # this if is only used for warning removal
        else:
            for message_part in message:
                if message_part['type'] == 'share':
                    pending_text = '分享了<a href="' + message_part['data']['url'] + '">' + message_part['data']['title'] + '</a>'
                elif message_part['type'] == 'rich':
                    if message_part['data'].get('url'):
                        if message_part['data']['url'].startswith('mqqapi'):
                            lat, lon, name, addr = extract_mqqapi(message_part['data']['url'])
                            pending_text = message_part['data']['text']
                            global_vars.tg_bot.sendLocation(chat_id=FORWARD_LIST[forward_index]['TG'],
                                                            latitude=float(lat), longitude=float(lon))

                        else:
                            pending_text = '<a href="' + message_part['data']['url'] + '">' + \
                                   message_part['data']['text'] + '</a>'
                    else:
                        pending_text = message_part['data']['text']
                elif message_part['type'] == 'dice':
                    pending_text = '掷出了 <b>' + message_part['data']['type'] + '</b>'
                elif message_part['type'] == 'rps':
                    pending_text = '出了 <b>' + {'1': '石头', '2': '剪刀', '3': '布'}[message_part['data']['type']] + '</b>'
                elif message_part['type'] == 'shake':  # not available in group and discuss
                    pending_text = '发送了一个抖动'
                elif message_part['type'] == 'music':
                    pending_text = '分享了<a href="https://y.qq.com/n/yqq/song/' + message_part['data'][
                        'id'] + '_num.html"> qq 音乐</a>'
                elif message_part['type'] == 'record':
                    pending_text = '说了句话，懒得转了'
                elif message_part['type'] == 'image':
                    if pending_image:
                        if pending_text:
                            message_list.append({'image': pending_image, 'text': pending_text})
                            pending_text = None
                        else:
                            message_list.append({'image': pending_image})

                    elif pending_text:
                        message_list.append({'text': pending_text})
                        pending_text = ''
                    pending_image = message_part['data']['file']
                elif message_part['type'] == 'text':
                    pending_text += message_part['data']['text'].strip().replace('<', '&lt;').replace('>', '&gt;')
                elif message_part['type'] == 'at':
                    qq_number = int(message_part['data']['qq'])
                    if qq_number == QQ_BOT_ID:
                        pending_text += ' @bot '
                    else:
                        pending_text = '@' + get_qq_name(qq_number, forward_index)
                elif message_part['type'] == 'face':
                    qq_face = int(message_part['data']['id'])
                    if qq_face in qq_emoji_list:
                        pending_text += qq_emoji_list[qq_face]
                    else:
                        pending_text += '\u2753'  # ❓
                elif message_part['type'] == 'bface':
                    pending_text += '\u2753'
                elif message_part['type'] == 'sface':
                    qq_face = int(message_part['data']['id']) & 255
                    if qq_face in qq_sface_list:
                        pending_text += qq_sface_list[qq_face]
                    else:
                        pending_text += '\u2753'  # ❓

            if pending_text:
                if pending_image:
                    message_list.append({'image': pending_image, 'text': pending_text})
                else:
                    message_list.append({'text': pending_text})
            elif pending_image:
                message_list.append({'image': pending_image})

            message_count = len(message_list)

            for idx, message_part in enumerate(message_list):
                if message_part.get('image'):
                    filename = message_part['image']
                    url = cq_get_pic_url(filename)
                    cq_download_pic(filename)
                    pic = open(os.path.join(CQ_IMAGE_ROOT, filename), 'rb')
                    # gif pictures send as document
                    if filename.lower().endswith('gif'):
                        try:
                            if message_part.get('text'):
                                if message_count == 1:
                                    full_msg = get_qq_name(qq_user, forward_index) + ': ' + message_list[0][
                                        'text']
                                else:
                                    full_msg = get_qq_name(qq_user, forward_index) + ': ' \
                                               + '(' + str(idx + 1) + '/' + str(message_count) + ')' + message_part['text']
                                global_vars.tg_bot.sendDocument(FORWARD_LIST[forward_index]['TG'], pic, caption=full_msg)
                            else:
                                global_vars.tg_bot.sendDocument(FORWARD_LIST[forward_index]['TG'], pic)
                        except telegram.error.TelegramError:
                            error(message)
                            traceback.print_exc()

                    # jpg/png pictures send as photo
                    else:
                        try:
                            if message_part.get('text'):
                                if message_count == 1:
                                    full_msg = get_qq_name(qq_user, forward_index) + ': ' + message_list[0][
                                        'text']
                                else:
                                    full_msg = get_qq_name(qq_user, forward_index) + ': ' \
                                               + '(' + str(idx + 1) + '/' + str(message_count) + ')' + message_part['text']
                                global_vars.tg_bot.sendPhoto(FORWARD_LIST[forward_index]['TG'], pic, caption=full_msg)
                            else:
                                global_vars.tg_bot.sendPhoto(FORWARD_LIST[forward_index]['TG'], pic)
                        except telegram.error.TelegramError:
                            error(message)
                            traceback.print_exc()

                else:
                    # only first message could be pure text
                    if message_count == 1:
                        full_msg_bold = '<b>' + get_qq_name(qq_user, forward_index) + '</b>: ' \
                                        + message_list[0]['text']
                    else:
                        full_msg_bold = '<b>' + get_qq_name(qq_user, forward_index) + '</b>: ' \
                                        + '(1/' + str(message_count) + ')' \
                                        + message_part['text']
                    global_vars.tg_bot.sendMessage(FORWARD_LIST[forward_index]['TG'], full_msg_bold, parse_mode='HTML')
