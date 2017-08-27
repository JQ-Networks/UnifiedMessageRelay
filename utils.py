#!/use/bin/env python3

import os
import sys
import threading
import traceback
import requests
from base64 import b64encode, b64decode
from cqsdk import RE_CQ_SPECIAL, \
    RcvdPrivateMessage, RcvdGroupMessage, RcvdDiscussMessage, \
    SendPrivateMessage, SendGroupMessage, SendDiscussMessage, \
    GroupMemberDecrease, GroupMemberIncrease
from bot_constant import *
import telegram
import global_vars

CQ_IMAGE_ROOT = os.path.join(CQ_ROOT, r'data/image')
CQ_GROUP_LIST_ROOT = os.path.join(CQ_ROOT, r'app/org.dazzyd.cqsocketapi/GroupListCache')


def info(*args, **kwargs):
    print("================ INFO  ================", file=sys.stderr)
    print(*args, **kwargs, file=sys.stderr)


def error(*args, **kwargs):
    print("================ ERROR ================", file=sys.stderr)
    print(*args, **kwargs, file=sys.stderr)


def read_hex(bytes_arr, start_index, length):
    result = 0
    end_index = start_index + length
    if end_index >= len(bytes_arr):
        end_index = len(bytes_arr) - 1
    for i in range(start_index, end_index):
        result = (result << 8) + int(bytes_arr[i])
    return result


def read_string(bytes_arr, start_index, length):
    name_bytes = bytes_arr[start_index:start_index + length]
    name_str = name_bytes.decode('gbk', 'ignore')
    return name_str


def read_group_member_list(filename):
    content = ''
    with open(os.path.join(CQ_GROUP_LIST_ROOT, filename), 'r', encoding='utf-8') as f:
        content = f.read()
    content_bytes = b64decode(content)
    
    obj_struct = [
        {'key': 'group_id'         , 'type': 'int', 'length': 8 },
        {'key': 'qq_id'            , 'type': 'int', 'length': 8 },
        {'key': 'nickname'         , 'type': 'str'              },
        {'key': 'group_card'       , 'type': 'str'              },
        {'key': 'sex'              , 'type': 'int', 'length': 4 },
        {'key': 'age'              , 'type': 'int', 'length': 4 },
        {'key': ''                 , 'type': 'int', 'length': 2 },
        {'key': 'join_group_time'  , 'type': 'int', 'length': 4 },
        {'key': 'last_message_time', 'type': 'int', 'length': 4 },
        {'key': ''                 , 'type': 'int', 'length': 2 },
        {'key': 'group_permission' , 'type': 'int', 'length': 4 },
        {'key': ''                 , 'type': 'int', 'length': 4 },
        {'key': 'special_title'    , 'type': 'str'              },
        {'key': 'unknown_value1'   , 'type': 'int', 'length': 4 },
        {'key': ''                 , 'type': 'int', 'length': 2 },
        {'key': 'unknown_value2'   , 'type': 'int', 'length': 4 }
    ]
    i = 6
    result = []
    while i < len(content_bytes):
        obj, i = fill_obj_by_struct(content_bytes, obj_struct, i)
        result.append(obj)
    # print(result)
    namelist = {}
    for item in result:
        key = str(item['qq_id'])
        value = item['nickname']
        if len(item['group_card']) > 0:
            value = item['group_card']
        namelist[key] = value
    # print(namelist)
    return namelist


def parse_member_info(bytes_arr):
    obj = {}
    obj_struct = [
        {'key': 'group_id'                  , 'type': 'int', 'length': 8},
        {'key': 'qq_id'                     , 'type': 'int', 'length': 8},
        {'key': 'nickname'                  , 'type': 'str'             },
        {'key': 'group_card'                , 'type': 'str'             },
        {'key': 'sex'                       , 'type': 'int', 'length': 4},
        {'key': 'age'                       , 'type': 'int', 'length': 4},
        {'key': 'district'                  , 'type': 'str'             },
        {'key': 'join_group_time'           , 'type': 'int', 'length': 4},
        {'key': 'last_message_time'         , 'type': 'int', 'length': 4},
        {'key': 'group_level'               , 'type': 'str'             },
        {'key': 'group_permission'          , 'type': 'int', 'length': 4},
        {'key': ''                          , 'type': 'int', 'length': 4},
        {'key': 'special_title'             , 'type': 'str'             },
        {'key': 'special_title_expired_time', 'type': 'int', 'length': 4},
        {'key': 'allow_modify_group_card'   , 'type': 'int', 'length': 4}
    ]
    
    i = 0
    obj, _ = fill_obj_by_struct(bytes_arr, obj_struct, i)
    print(obj)
    return obj


def fill_obj_by_struct(bytes_arr, obj_struct, from_index):
    i = from_index
    obj = {}
    for item in obj_struct:
        if item['type'] == 'int':
            value = read_hex(bytes_arr, i, item['length'])
            if len(item['key']) > 0:
                obj[item['key']] = value
            i += item['length']
        elif item['type'] == 'str':
            str_len = read_hex(bytes_arr, i, 2)
            i += 2
            value = read_string(bytes_arr, i, str_len)
            if len(item['key']) > 0:
                obj[item['key']] = value
            i += str_len
    return obj, i


def mkdir(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass


def match(text, keywords):
    for keyword in keywords:
        if keyword in text:
            return True
    return False


def reply(qqbot, message, text):
    reply_msg = None
    if isinstance(message, RcvdPrivateMessage):
        reply_msg = SendPrivateMessage(
            qq=message.qq,
            text=text,
            )
    if isinstance(message, RcvdGroupMessage):
        reply_msg = SendGroupMessage(
            group=message.group,
            text=text,
            )
    if isinstance(message, RcvdDiscussMessage):
        reply_msg = SendDiscussMessage(
            discuss=message.discuss,
            text=text,
            )
    if reply_msg:
        qqbot.send(reply_msg)
        print("↘", message)
        print("↗", reply_msg)


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
    return '(forwarded from ' + result + ')'


def get_reply_to(reply_to_message: telegram.Message):
    """
    Combine replied user's first name and last name and format into (reply to from xxx)
    :param reply_to_message: the replied message
    :return: combined (reply to from xxx)
    """
    if not reply_to_message or not reply_to_message.from_user:
        return ''
    reply_to = get_full_user_name(reply_to_message.from_user)
    if reply_to_message.from_user.id == tg_bot_id:
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
    return '(reply to ' + reply_to + ')'
