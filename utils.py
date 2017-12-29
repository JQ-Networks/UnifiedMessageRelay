#!/use/bin/env python3

import os
import threading
import traceback
import requests
from bot_constant import *
import telegram
import global_vars
import re
from cq_utils import qq_emoji_list, qq_sface_list, cq_get_pic_url, cq_download_pic,\
    cq_location_regex, CQ_IMAGE_ROOT
import logging
import datetime

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
        right_end = message_text.find('💬')
        if right_end != -1:  # from qq
            result = message_text[:right_end]
        else:  # self generated command text, etc.
            result = ''
    else:
        result = get_full_user_name(message.forward_from)
    return '(↩️' + result + ')'


def get_reply_to(reply_to_message: telegram.Message, forward_index: int):
    """
    Combine replied user's first name and last name and format into (reply to from xxx)
    :param reply_to_message: the replied message
    :param forward_index: forward index
    :return: combined (reply to from xxx)
    """
    if not reply_to_message or not reply_to_message.from_user:
        return ''
    reply_to = get_full_user_name(reply_to_message.from_user)
    if reply_to_message.from_user.id == global_vars.tg_bot_id:
        tg_message_id = reply_to_message.message_id
        saved_message = global_vars.mdb.retrieve_message(tg_message_id, forward_index)
        if not saved_message:
            return ''
        qq_number = saved_message[2]
        if not qq_number:  # message is bot command (tg side)
            return ''
        reply_to = get_qq_name_encoded(qq_number, forward_index)
    return '(➡️' + reply_to + ')'


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


def encode_html(encode_string: str):
    """
    used for telegram parse_mode=HTML
    :param encode_string: string to encode
    :return: encoded string
    """

    return encode_string.strip().replace('<', '&lt;').replace('>', '&gt;')


def get_qq_name_encoded(qq_number: int,
                        forward_index: int):
    """
    get encoded qq name
    :param qq_number:
    :param forward_index:
    :return:
    """
    return encode_html(get_qq_name(qq_number, forward_index)).replace('(', '').replace(')', '')\
        .replace('➡️', '').replace('↩️', '')

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


def extract_universal_mark(message: str) -> (str, str, str, bool, str):
    """
    message with attributes
    :param message:
    :return: sender, forward_from, reply_to, edited, trimmed message
    """

    if '💬' not in message:
        return '', '', '', False, message

    forward_regex = re.compile(r'\(↩(.*?)\).*?(?=💬 )')
    reply_regex = re.compile(r'\(➡️(.*?)\).*?(?=💬 )')
    send_regex = re.compile(r'^(.*?)💬 ')

    sender = ''
    forward_from = ''
    reply_to = ''
    edited = False

    def extract_forward(match):
        nonlocal forward_from
        forward_from = match.group(1)
        return ''

    def extract_reply(match):
        nonlocal reply_to
        reply_to = match.group(1)
        return ''

    def extract_send(match):
        nonlocal sender
        sender = match.group(1).strip()
        return ''

    message = forward_regex.sub(extract_forward, message, count=1)
    message = reply_regex.sub(extract_reply, message, count=1)
    if '✎ 💬 ' in message:
        edited = True
        message = message.replace('✎', '', 1)
    message = send_regex.sub(extract_send, message, count=1)

    return sender, forward_from, reply_to, edited, message


def send_from_tg_to_qq(forward_index: int,
                       message: list,
                       tg_group_id: int,
                       tg_user: telegram.User=None,
                       tg_forward_from: telegram.Message=None,
                       tg_reply_to: telegram.Message=None,
                       edited: bool=False,
                       auto_escape: bool=True) -> int:
    """
    send message from telegram to qq
    :param forward_index: forward group index
    :param message: message in cq-http-api like format
    :param tg_group_id: telegram group id
    :param tg_user: telegram user who send this message
    :param tg_forward_from: who the message is forwarded from
    :param tg_reply_to:  who the message is replied to
    :param edited: the status of edition
    :param auto_escape: if contain coolq code, pass False
    :return: qq message id
    """
    logger.debug("tg -> qq: " + str(message))

    sender_name = get_full_user_name(tg_user)
    reply_to = get_reply_to(tg_reply_to, forward_index)
    if tg_forward_from.forward_from and tg_forward_from.forward_from.id == global_vars.tg_bot_id:
        if message[0]['type'] == 'text':
            sender, forward_from, _, _, message[0]['data']['text'] = extract_universal_mark(message[0]['data']['text'])
        else:
            sender, forward_from, _, _, message[1]['data']['text'] = extract_universal_mark(message[1]['data']['text'])
        if forward_from:
            forward_from = '(↩️' + forward_from + ')'
        else:
            forward_from = '(↩️' + sender + ')'
    else:
        forward_from = get_forward_from(tg_forward_from)
    if edited:  # if edited, add edit mark
        edit_mark = ' ✎ '
    else:
        edit_mark = ''

    message_attribute = sender_name + reply_to + forward_from + edit_mark + '💬 '

    if sender_name:  # insert extra info at beginning
        message.insert(0, {
            'type': 'text',
            'data': {'text': message_attribute}
        })

    if FORWARD_LIST[forward_index].get('QQ'):
        return global_vars.qq_bot.send_group_msg(group_id=FORWARD_LIST[forward_index]['QQ'],
                                                 message=message,
                                                 auto_escape=auto_escape)['message_id']

    if FORWARD_LIST[forward_index].get('DISCUSS'):
        return global_vars.qq_bot.send_discuss_msg(discuss_id=FORWARD_LIST[forward_index]['DISCUSS'],
                                                   message=message,
                                                   auto_escape=auto_escape)['message_id']


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
        _pending_text += encode_html(data['text'])

    def _at(data):
        nonlocal _pending_text
        _qq_number = int(data['qq'])
        if _qq_number == QQ_BOT_ID:
            _pending_text += ' @bot '
        else:
            _pending_text += ' @' + get_qq_name_encoded(_qq_number, forward_index) + ' '

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
            logger.info('unknown coolq message part: ' + message_part)

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
                       qq_user: int=None) -> list:
    """
    send message from qq to telegram
    :param forward_index: forward group index
    :param message: message in cq-http-api like format
    :param qq_group_id: which group this message came from, can be None if qq_discuss_id is not None
    :param qq_discuss_id: which discuss this message came from, can be None if qq_group_id is not None
    :param qq_user:  which user sent this message
    :return: telegram.Message list
    """
    logger.debug('qq -> tg: ' + str(message))

    message_list = divide_qq_message(forward_index, message)
    forward_from = ''
    if 'text' in message_list[0]:
        sender, forward_from, _, _, message_list[0]['text'] = extract_universal_mark(message_list[0]['text'])
        if forward_from:
            forward_from = '(↩️' + forward_from + ')'
        elif sender:
            forward_from = '(↩️' + sender + ')'
        if not message_list[0]['text'].strip():
            del message_list[0]

    message_count = len(message_list)

    telegram_message_id_list = list()

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
                full_msg = get_qq_name_encoded(qq_user, forward_index) + forward_from + '💬 ' \
                           + message_index_attribute + message_part['text']
            else:
                full_msg = get_qq_name_encoded(qq_user, forward_index) + forward_from + '💬 ' + message_index_attribute

            if filename.lower().endswith('gif'):  # gif pictures send as document
                _msg: telegram.Message = global_vars.tg_bot.sendDocument(FORWARD_LIST[forward_index]['TG'],
                                                                         pic,
                                                                         caption=full_msg)
            else:  # jpg/png pictures send as photo
                _msg: telegram.Message = global_vars.tg_bot.sendPhoto(FORWARD_LIST[forward_index]['TG'],
                                                                      pic,
                                                                      caption=full_msg)

        else:
            # only first message could be pure text
            if qq_user:
                full_msg_bold = '<b>' + get_qq_name_encoded(qq_user, forward_index) + '</b>' + forward_from + '💬 ' + \
                                message_index_attribute +\
                                message_list[0]['text']
            else:
                full_msg_bold = message_index_attribute + message_list[0]['text']
            _msg: telegram.Message = global_vars.tg_bot.sendMessage(FORWARD_LIST[forward_index]['TG'],
                                                                    full_msg_bold,
                                                                    parse_mode='HTML')
        telegram_message_id_list.append(_msg.message_id)
    return telegram_message_id_list


def send_both_side(forward_index: int,
                   message: str,
                   qq_group_id: int = 0,
                   qq_discuss_id: int = 0,
                   tg_group_id: int = 0,
                   tg_message_id: int = 0):
    """
    bot command only, send notification to both side
    :param forward_index: forward group index
    :param message: message in str
    :param qq_group_id: which qq group to send
    :param qq_discuss_id: which qq discuss to send
    :param tg_group_id: which tg group to send
    :param tg_message_id: which tg message to reply
    :return:
    """
    if tg_group_id:
        send_from_tg_to_qq(forward_index,
                           text_reply(message),
                           tg_group_id=tg_group_id)
        global_vars.tg_bot.sendMessage(chat_id=tg_group_id,
                                       text=message,
                                       reply_to_message_id=tg_message_id)
    elif qq_group_id:
        send_from_qq_to_tg(forward_index,
                           text_reply(message),
                           qq_group_id=qq_group_id)
        return {'reply': message}
    else:
        send_from_qq_to_tg(forward_index,
                           text_reply(message),
                           qq_discuss_id=qq_discuss_id)
        return {'reply': message}


def recall_message(forward_index: int,
                   tg_message: telegram.Message):
    """
    recall qq message(only bot sent message can be recalled in two minutes)
    :param forward_index: group forward index
    :param tg_message: telegram message
    :return:
    -1: message empyt
    -2: message not found in database
    -3: message was from other qq
    -4: message has expired two minutes
    0: success
    """
    if not tg_message:
        return -1

    tg_reply_id = tg_message.message_id
    saved_message = global_vars.mdb.retrieve_message(tg_reply_id, forward_index)
    global_vars.mdb.delete_message(tg_reply_id, forward_index)
    if not saved_message:
        return -2

    qq_number = saved_message[2]
    if qq_number:  # 0 means from tg, >0 means from qq
        return -3
    timestamp = tg_message.date
    if datetime.datetime.now() - timestamp > datetime.timedelta(minutes=2):
        return -4
    else:
        qq_message_id = saved_message[1]
        global_vars.qq_bot.delete_msg(message_id=qq_message_id)
        return 0
