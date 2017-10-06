import re
from utils import decode_cq_escape

# part message
cq_emoji_regex = re.compile(r'\[CQ:emoji,id=(\d+?)\]')
qq_face_regex = re.compile(r'\[CQ:face,id=(\d+?)\]')
cq_at_regex = re.compile(r'\[CQ:at,qq=(\d+?)\]')
cq_image_regex = re.compile(r'\[CQ:image,file=(.+?)\]')
cq_image_simple_regex = re.compile(r'\[CQ:image.*?\]')

# whole message
cq_shake_regex = re.compile(r'\[CQ:shake\]')
cq_dice_regex = re.compile(r'\[CQ:dice(,type=(\d))?\]')
cq_rps_regex = re.compile(r'\[CQ:rps(,type=(\d))?\]')
cq_rich_regex = re.compile(r'\[CQ:rich,url=(.*),text=(.*)\]', re.DOTALL)
cq_music_regex = re.compile(r'\[CQ:music,type=(.*),id=(\d+)\]', re.DOTALL)
cq_custom_music_regex = re.compile(r'\[CQ:share,type=custom,url=(.*),audio=(.*),title=(.*),content=(.*),image=(.*)\]',
                                   re.DOTALL)
cq_share_regex = re.compile(r'\[CQ:share,url=(.*),title=(.*),content=(.*),image=(.*)\]', re.DOTALL)
cq_record_regex = re.compile(r'\[CQ:record,file=(.*)(,magic=(true|false))?\]')

# unknown
cq_anonymous_regex = re.compile(r'\[CQ:anonymous,ignore=(true|false)\]')

# https://d.cqp.me/Pro/CQ码
# to be continued


def extract_cq_dice(message):
    """
    get dice parameters
    :param message: raw cq message
    :return: dice number
    """
    result = cq_dice_regex.findall(message)[0]
    return decode_cq_escape(result[0])


def extract_cq_rps(message):
    """
    get rps parameters
    :param message: raw cq message
    :return: rps number(stone: 1, scissors: 2, paper: 3)
    """
    result = cq_dice_regex.findall(message)[0]
    return decode_cq_escape(result[0])


def extract_cq_rich(message):
    """
    get rich text parameters
    :param message: raw cq message
    :return: url, text
    """
    result = cq_rich_regex.findall(message)[0]
    return decode_cq_escape(result[0]), decode_cq_escape(result[1])


def extract_cq_music(message):
    """
    get music parameters
    :param message: raw cq message
    :return: type, id
    """
    result = cq_music_regex.findall(message)[0]
    return decode_cq_escape(result[0]), decode_cq_escape(result[1])


def extract_cq_share(message):
    """
    get share parameters
    :param message: raw cq message
    :return: url, title, content, image_url
    """
    result = cq_share_regex.findall(message)[0]
    return decode_cq_escape(result[0]), decode_cq_escape(result[1]), \
        decode_cq_escape(result[2]), decode_cq_escape(result[3])


def extract_cq_record(message):
    """
    get record parameters
    :param message: raw cq message
    :return: file, magic
    """
    result = cq_record_regex.findall(message)[0]
    return decode_cq_escape(result[0]), decode_cq_escape(result[1])


def extract_cq_custom_music(message):
    """
    get custom music patameters
    :param message:
    :return: url, audio, title, content, image
    """
    result = cq_record_regex.findall(message)[0]
    return decode_cq_escape(result[0]), decode_cq_escape(result[1]), \
        decode_cq_escape(result[2]), decode_cq_escape(result[3]), \
        decode_cq_escape(result[4])
