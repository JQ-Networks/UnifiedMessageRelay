#!/use/bin/env python3

import os
import threading
import traceback
import requests
from bot_constant import *
import telegram
import global_vars
import re
from typing import Union
from cq_utils import qq_emoji_list, qq_sface_list, cq_get_pic_url, cq_download_pic,\
    cq_location_regex, CQ_IMAGE_ROOT
import logging

logger = logging.getLogger("CTBMain.utils")


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
            logger.error("[FileDownloader]Catch exception on downloading.")
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

    if message.forward_from.id == global_vars.tg_bot_id:
        if message.caption:
            message_text = message.caption
        elif message.text:
            message_text = message.text
        else:
            message_text = ''
        right_end = message_text.find(':')
        if right_end != -1:  # from qq
            result = message_text[:right_end]
        else:  # self generated command text, etc.
            result = ''
    else:
        result = get_full_user_name(message.forward_from)
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


def get_forward_index(qq_group_id=None,
                      qq_discuss_id=None,
                      tg_group_id=None):
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


def get_qq_name(qq_number: int,
                forward_index: int):
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
    return locations[0],\
           locations[1],\
           locations[2],\
           locations[3]


def text_reply(text):
    """
    simplify pure text reply
    :param text:  text reply
    :return: general message list
    """
    return [{
        'type': 'text',
        'data': {'text': text}
    }]


def send_from_tg_to_qq(forward_index: int,
                       message: list,
                       tg_user: telegram.User=None,
                       tg_forward_from: telegram.Message=None,
                       tg_reply_to: telegram.Message=None,
                       edited: bool=False,
                       auto_escape: bool=True):
    """
    send message from telegram to qq
    :param forward_index: forward group index
    :param message: message in cq-http-api like format
    :param tg_user: telegram user who send this message
    :param tg_forward_from: who the message is forwarded from
    :param tg_reply_to:  who the message is replied to
    :param edited: the status of edition
    :param auto_escape: if contain coolq code, pass False
    :return: qq message id (not implemented)
    """
    logger.debug("tg -> qq: " + str(message))
    sender_name = get_full_user_name(tg_user)
    forward_from = get_forward_from(tg_forward_from)
    reply_to = get_reply_to(tg_reply_to)

    if edited:  # if edited, add edit mark
        edit_mark = ' ✎ '
    else:
        edit_mark = ''

    message_attribute = sender_name + reply_to + forward_from + edit_mark + ': '

    if message_attribute:  # insert extra info at beginning
        message.insert(0, {
            'type': 'text',
            'data': {'text': message_attribute}
        })

    if FORWARD_LIST[forward_index].get('QQ'):
        if isinstance(FORWARD_LIST[forward_index]['QQ'], int):  # single QQ group
            global_vars.qq_bot.send_group_msg(group_id=FORWARD_LIST[forward_index]['QQ'], message=message,
                                              auto_escape=auto_escape)
        else:  # multiple QQ group as a list
            for group in FORWARD_LIST[forward_index]['QQ']:
                global_vars.qq_bot.send_group_msg(group_id=group, message=message, auto_escape=auto_escape)

    if FORWARD_LIST[forward_index].get('DISCUSS'):
        if isinstance(FORWARD_LIST[forward_index]['DISCUSS'], int):  # single QQ discuss
            global_vars.qq_bot.send_discuss_msg(discuss_id=FORWARD_LIST[forward_index]['DISCUSS'], message=message,
                                                auto_escape=auto_escape)
        else:  # multiple QQ discuss as a list
            for discuss in FORWARD_LIST[forward_index]['DISCUSS']:
                global_vars.qq_bot.send_discuss_msg(discuss_id=discuss, message=message, auto_escape=auto_escape)


def divide_qq_message(forward_index: int,
                      message: list):
    """
    divide QQ's rich text into telegram compatible messages
    :param forward_index: forward group index
    :param message: raw coolq message
    :return: divided list
    """

    _pending_text = ''
    _pending_image = ''

    def _share(data):
        nonlocal _pending_text
        _pending_text = '分享了<a href="' + data['url'] + '">' + data['title'] + '</a>'

    def _rich(data):
        nonlocal _pending_text
        if data.get('url'):
            if data['url'].startswith('mqqapi'):
                lat, lon, name, addr = extract_mqqapi(data['url'])
                _pending_text = data['text']
                global_vars.tg_bot.sendLocation(chat_id=FORWARD_LIST[forward_index]['TG'],
                                                latitude=float(lat),
                                                longitude=float(lon))
            else:
                _pending_text = '<a href="' + data['url'] + '">' + data['text'] + '</a>'
        else:
            _pending_text = data['text']

    def _dice(data):
        nonlocal _pending_text
        _pending_text = '掷出了 <b>' + data['type'] + '</b>'

    def _rps(data):
        nonlocal _pending_text
        _pending_text = '出了 <b>' + {'1': '石头', '2': '剪刀', '3': '布'}[data['type']] + '</b>'

    def _shake(data):
        nonlocal _pending_text
        _pending_text = '发送了一个抖动'

    def _music(data):
        nonlocal _pending_text
        _pending_text = '分享了<a href="https://y.qq.com/n/yqq/song/' + data['id'] + '_num.html"> qq 音乐</a>'

    def _record(data):  # not implemented
        nonlocal _pending_text
        _pending_text = '说了句话，请到电报查看'

    def _image(data):
        nonlocal _pending_text
        nonlocal _pending_image
        if _pending_image:
            if _pending_text:
                message_list.append({'image': _pending_image, 'text': _pending_text})
                _pending_text = ''
            else:
                message_list.append({'image': _pending_image})

        elif _pending_text:
            message_list.append({'text': _pending_text})
            _pending_text = ''
        _pending_image = data['file']

    def _text(data):
        nonlocal _pending_text
        _pending_text += data['text'].strip().replace('<', '&lt;').replace('>', '&gt;')

    def _at(data):
        nonlocal _pending_text
        _qq_number = int(data['qq'])
        if _qq_number == QQ_BOT_ID:
            _pending_text += ' @bot '
        else:
            _pending_text = '@' + get_qq_name(_qq_number, forward_index)

    def _face(data):
        nonlocal _pending_text
        _qq_face = int(data['id'])
        if _qq_face in qq_emoji_list:
            _pending_text += qq_emoji_list[_qq_face]
        else:
            _pending_text += '\u2753'  # ❓

    def _bface(data):
        nonlocal _pending_text
        _pending_text += '\u2753'  # ❓

    def _sface(data):
        nonlocal _pending_text
        qq_face = int(data['id']) & 255
        if qq_face in qq_sface_list:
            _pending_text += qq_sface_list[qq_face]
        else:
            _pending_text += '\u2753'  # ❓

    switch = {
        'share': _share,
        'rich': _rich,
        'dice': _dice,
        'rps': _rps,
        'shake': _shake,
        'music': _music,
        'record': _record,
        'image': _image,
        'text': _text,
        'at': _at,
        'face': _face,
        'bface': _bface,
        'sface': _sface
    }

    message_list = list()
    for message_part in message:
        if message_part['type'] in switch:
            switch[message_part['type']](message_part['data'])
        else:
            logger.debug('unknown coolq message part: ' + message_part)

    if _pending_text:
        if _pending_image:
            message_list.append({'image': _pending_image,
                                 'text': _pending_text})
        else:
            message_list.append({'text': _pending_text})
    elif _pending_image:
        message_list.append({'image': _pending_image})

    return message_list


def send_from_qq_to_tg(forward_index: int,
                       message: list,
                       qq_group_id: int = 0,
                       qq_discuss_id: int = 0,
                       qq_user: int=None):
    """
    send message from qq to telegram
    :param forward_index: forward group index
    :param message: message in cq-http-api like format
    :param qq_group_id: which group this message came from, can be None if qq_discuss_id is not None
    :param qq_discuss_id: which discuss this message came from, can be None if qq_group_id is not None
    :param qq_user:  which user sent this message
    :return: telegram.Message list (not implemented)
    """
    logger.debug('qq -> tg: ' + str(message))

    message_list = divide_qq_message(forward_index, message)
    message_count = len(message_list)

    for idx, message_part in enumerate(message_list):
        if message_count == 1:
            message_index_attribute = ''
        else:
            message_index_attribute = '(' + str(idx + 1) + '/' + str(message_count) + ')'
        if message_part.get('image'):
            filename = message_part['image']

            cq_get_pic_url(filename)
            cq_download_pic(filename)
            pic = open(os.path.join(CQ_IMAGE_ROOT, filename), 'rb')

            if message_part.get('text'):
                full_msg = get_qq_name(qq_user, forward_index) + ': ' \
                           + message_index_attribute + message_part['text']
            else:
                full_msg = get_qq_name(qq_user, forward_index) + ': ' + message_index_attribute

            if filename.lower().endswith('gif'):  # gif pictures send as document
                global_vars.tg_bot.sendDocument(FORWARD_LIST[forward_index]['TG'], pic, caption=full_msg)
            else:  # jpg/png pictures send as photo
                global_vars.tg_bot.sendPhoto(FORWARD_LIST[forward_index]['TG'], pic, caption=full_msg)

        else:
            # only first message could be pure text
            if qq_user:
                full_msg_bold = '<b>' + get_qq_name(qq_user, forward_index) + '</b>: ' + \
                                message_index_attribute +\
                                message_list[0]['text']
            else:
                full_msg_bold = message_index_attribute + message_list[0]['text']
            global_vars.tg_bot.sendMessage(FORWARD_LIST[forward_index]['TG'], full_msg_bold, parse_mode='HTML')


def send_all_except_current(forward_index: int,
                            message: list,
                            qq_group_id: int = 0,
                            qq_discuss_id: int = 0,
                            qq_user: int=None,
                            tg_group_id: int = 0,
                            tg_user: telegram.User=None,
                            tg_forward_from: telegram.Message=None,
                            tg_reply_to: telegram.Message=None,
                            edited: bool=False,
                            auto_escape: bool=True):
    """
    send message from one chat to all others (multi-forward not fully implemented)
    :param forward_index: forward group index
    :param message: message in cq-http-api like format
    :param qq_group_id: which group this message came from, can be None if qq_discuss_id is not None
    :param qq_discuss_id: which discuss this message came from, can be None if qq_group_id is not None
    :param qq_user:  which user sent this message
    :param tg_user: telegram user who send this message
    :param tg_group_id: telegram group id
    :param tg_forward_from: who the message is forwarded from
    :param tg_reply_to:  who the message is replied to
    :param edited: the status of edition
    :param auto_escape: if contain coolq code, pass False
    :return: (not implemented)
    """
    if tg_group_id:
        send_from_tg_to_qq(forward_index, message, tg_user, tg_forward_from, tg_reply_to, edited, auto_escape)

    else:
        send_from_qq_to_tg(forward_index, message, qq_group_id, qq_discuss_id, qq_user)
