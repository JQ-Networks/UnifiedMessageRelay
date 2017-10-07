import global_vars
from cqsdk import *
from CQAnonymousInfo import CQAnonymousInfo
from utils import get_forward_index
from bot_constant import FORWARD_LIST
import base64
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='bot.log',
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


@global_vars.qq_bot.listener((RcvdPrivateMessage, ), 1)  # priority 1
def test(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    return False


@global_vars.qq_bot.listener((RcvdGroupMessage, ), 1)  # priority 1
def test(message: RcvdGroupMessage):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    # if message.from_anonymous:
    #     logging.info(CQAnonymousInfo(base64.b64decode(message.from_anonymous)))
    return False


@global_vars.qq_bot.listener((RcvdDiscussMessage, ), 1)  # priority 1
def test(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    return False


@global_vars.qq_bot.listener((GroupAdminChange, ), 1)  # priority 1
def test(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    return False


@global_vars.qq_bot.listener((GroupMemberDecrease, ), 1)  # priority 1
def test(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    return False


@global_vars.qq_bot.listener((GroupMemberIncrease, ), 1)  # priority 1
def test(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    return False


@global_vars.qq_bot.listener((FriendAdded, ), 1)  # priority 1
def test(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    return False


@global_vars.qq_bot.listener((GroupUpload, ), 1)  # priority 1
def test(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    return False


@global_vars.qq_bot.listener((RcvGroupMemberInfo, ), 1)  # priority 1
def test(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    return False


@global_vars.qq_bot.listener((RcvGroupMemberList, ), 1)  # priority 1
def test(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    return False


@global_vars.qq_bot.listener((RcvStrangerInfo, ), 1)  # priority 1
def test(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    return False


@global_vars.qq_bot.listener((RcvCookies, ), 1)  # priority 1
def test(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    return False


@global_vars.qq_bot.listener((RcvCsrfToken, ), 1)  # priority 1
def test(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    return False


@global_vars.qq_bot.listener((RcvLoginQQ, ), 1)  # priority 1
def test(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    return False


@global_vars.qq_bot.listener((RcvLoginNickname, ), 1)  # priority 1
def test(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if 'Test_mode' in FORWARD_LIST[forward_index] and FORWARD_LIST[forward_index]['Test_mode']:
        logging.info(message)
    return False

