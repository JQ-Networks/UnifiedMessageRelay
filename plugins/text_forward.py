from bot_constant import FORWARD_LIST, JQ_MODE, QQ_BOT_ID
import global_vars
from utils import get_forward_index, CQ_IMAGE_ROOT, SERVER_PIC_URL, \
    get_forward_from, get_reply_to, get_full_user_name, error
from cqsdk import SendGroupMessage, RcvdGroupMessage, CQAt, CQImage
from command import command_listener
from PIL import Image
from configparser import ConfigParser
import requests
from urllib.request import urlretrieve
from telegram.ext import MessageHandler, Filters
from telegram.error import BadRequest
from cq_utils import cq_share_regex, cq_music_regex, cq_emoji_regex,\
    qq_face_regex, extract_cq_share
import traceback
import telegram
import json
import os
import re

"""
request set CQ_IMAGE_ROOT SERVER_PIC_URL JQ_MODE
"""
# region utils

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


qq_emoji_list = {  # created by JogleLew, optimizations are welcome
    0: u'\U0001F62E',
    1: u'\U0001F623',
    2: u'\U0001F60D',
    3: u'\U0001F633',
    4: u'\U0001F60E',
    5: u'\U0001F62D',
    6: u'\U0000263A',
    7: u'\U0001F637',
    8: u'\U0001F634',
    9: u'\U0001F62D',
    10: u'\U0001F630',
    11: u'\U0001F621',
    12: u'\U0001F61D',
    13: u'\U0001F603',
    14: u'\U0001F642',
    15: u'\U0001F641',
    16: u'\U0001F913',
    18: u'\U0001F624',
    19: u'\U0001F628',
    20: u'\U0001F60F',
    21: u'\U0001F60A',
    22: u'\U0001F644',
    23: u'\U0001F615',
    24: u'\U0001F924',
    25: u'\U0001F62A',
    26: u'\U0001F628',
    27: u'\U0001F613',
    28: u'\U0001F62C',
    29: u'\U0001F911',
    30: u'\U0001F44A',
    31: u'\U0001F624',
    32: u'\U0001F914',
    33: u'\U0001F910',
    34: u'\U0001F635',
    35: u'\U0001F629',
    36: u'\U0001F47F',
    37: u'\U0001F480',
    38: u'\U0001F915',
    39: u'\U0001F44B',
    50: u'\U0001F641',
    51: u'\U0001F913',
    53: u'\U0001F624',
    54: u'\U0001F92E',
    55: u'\U0001F628',
    56: u'\U0001F613',
    57: u'\U0001F62C',
    58: u'\U0001F911',
    73: u'\U0001F60F',
    74: u'\U0001F60A',
    75: u'\U0001F644',
    76: u'\U0001F615',
    77: u'\U0001F924',
    78: u'\U0001F62A',
    79: u'\U0001F44A',
    80: u'\U0001F624',
    81: u'\U0001F914',
    82: u'\U0001F910',
    83: u'\U0001F635',
    84: u'\U0001F629',
    85: u'\U0001F47F',
    86: u'\U0001F480',
    87: u'\U0001F915',
    88: u'\U0001F44B',
    96: u'\U0001F630',
    97: u'\U0001F605',
    98: u'\U0001F925',
    99: u'\U0001F44F',
    100: u'\U0001F922',
    101: u'\U0001F62C',
    102: u'\U0001F610',
    103: u'\U0001F610',
    104: u'\U0001F629',
    105: u'\U0001F620',
    106: u'\U0001F61E',
    107: u'\U0001F61F',
    108: u'\U0001F60F',
    109: u'\U0001F619',
    110: u'\U0001F627',
    111: u'\U0001F920',
    172: u'\U0001F61C',
    173: u'\U0001F62D',
    174: u'\U0001F636',
    175: u'\U0001F609',
    176: u'\U0001F913',
    177: u'\U0001F635',
    178: u'\U0001F61C',
    179: u'\U0001F4A9',
    180: u'\U0001F633',
    181: u'\U0001F913',
    182: u'\U0001F602',
    183: u'\U0001F913',
    212: u'\U0001F633',
}


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


def create_jpg_image(path, name):
    """
    convert Telegram webp image to jpg image
    :param path: save path
    :param name: image name
    """
    im = Image.open(os.path.join(path, name)).convert("RGB")
    im.save(os.path.join(path, name + ".jpg"), "JPEG")


def create_png_image(path, name):
    """
    convert Telegram webp image to png image
    :param path: save path
    :param name: image name
    """
    im = Image.open(os.path.join(path, name)).convert("RGBA")
    im.save(os.path.join(path, name + ".png"), "PNG")


def cq_get_pic_url(filename):
    """
    get real image url from cqimg file
    :param filename:
    :return: image url
    """
    cqimg = os.path.join(CQ_IMAGE_ROOT, filename+'.cqimg')
    parser = ConfigParser()
    parser.read(cqimg)
    url = parser['image']['url']
    return url


def cq_download_pic(filename):
    """
    download image by cqimg file
    :param filename: cqimg file name
    """
    try:
        path = os.path.join(CQ_IMAGE_ROOT, filename)
        if os.path.exists(path):
            return

        cqimg = os.path.join(CQ_IMAGE_ROOT, filename + '.cqimg')
        parser = ConfigParser()
        parser.read(cqimg)

        url = parser['image']['url']
        urlretrieve(url, path)
    except:
        error(filename)
        traceback.print_exc()


def get_short_url(long_url):
    """
    generate short url using Sina Weibo api
    :param long_url: the original url
    :return: short url
    """
    # change long url to `t.cn` short url
    sina_api_prefix = 'http://api.t.sina.com.cn/short_url/shorten.json?source=3271760578&url_long='
    try:
        r = requests.get(sina_api_prefix + long_url)
        obj = json.loads(r.text)
        short_url = obj[0]['url_short']
        return short_url

    # when error occurs, return origin long url
    except:
        traceback.print_exc()
        return long_url


def tg_get_pic_url(file_id: str, pic_type: str):
    """
    download image from Telegram Server, and generate new image link that send to QQ group
    :param file_id: telegram file id
    :param pic_type: picture extension name
    :return: pic url
    """
    file = global_vars.tg_bot.getFile(file_id)
    urlretrieve(file.file_path, os.path.join(CQ_IMAGE_ROOT, file_id))  # download image
    if pic_type == 'jpg':
        create_jpg_image(CQ_IMAGE_ROOT, file_id)
        pic_url = get_short_url(SERVER_PIC_URL + file_id + '.jpg')
        return pic_url
    elif pic_type == 'png':
        create_png_image(CQ_IMAGE_ROOT, file_id)
        pic_url = get_short_url(SERVER_PIC_URL + file_id + '.png')
        return pic_url
    return ''


def cq_send(update: telegram.Update, text: str, qq_group_id: int):
    """
    send telegram message to qq with forward of reply support
    :param update: telegram.Update
    :param text: text to send, in coolq format
    :param qq_group_id: which group to send
    """
    sender_name = get_full_user_name(update.message.from_user)
    forward_from = get_forward_from(update.message)
    reply_to = get_reply_to(update.message.reply_to_message)

    # get real sender from telegram message
    if forward_from and update.message.forward_from.id == global_vars.tg_bot_id:
        left_start = text.find(': ')
        if left_start != -1:
            text = text[left_start + 2:]
    text = emoji_to_cqemoji(text)

    global_vars.qq_bot.send(SendGroupMessage(
        group=qq_group_id,
        text=sender_name + reply_to + forward_from + ': ' + text
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

# endregion

PIC_LINK_MODE = []  # pic_link_mode per group

for forward in FORWARD_LIST:  # initialize
    PIC_LINK_MODE.append(forward['Pic_link'])


def photo_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))

    file_id = update.message.photo[-1].file_id
    pic_url = tg_get_pic_url(file_id, 'jpg')
    if JQ_MODE:
        text = '[CQ:image,file=' + file_id + '.jpg]'
    else:
        text = '[图片, 请点击查看' + pic_url + ']'
    if update.message.caption:
        text += update.message.caption

    cq_send(update, text, qq_group_id)


def video_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    text = '[视频]'
    cq_send(update, text, qq_group_id)


def audio_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    text = '[音频]'
    cq_send(update, text, qq_group_id)


def document_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    text = '[文件]'
    cq_send(update, text, qq_group_id)


def sticker_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))

    if PIC_LINK_MODE[forward_index]:
        file_id = update.message.sticker.file_id
        pic_url = tg_get_pic_url(file_id, 'png')
        if JQ_MODE:
            text = '[CQ:image,file=' + file_id + '.png]'
        else:
            text = '[' + update.message.sticker.emoji + ' sticker, 请点击查看' + pic_url + ']'
    else:
        text = '[' + update.message.sticker.emoji + ' sticker]'
    cq_send(update, text, qq_group_id)


def text_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))

    text = update.message.text
    if text.startswith('//'):  # feature, comment will no be send to qq
        return
    else:
        cq_send(update, text, qq_group_id)


global_vars.dp.add_handler(MessageHandler(Filters.text | Filters.command, text_from_telegram), 100) # priority 100
global_vars.dp.add_handler(MessageHandler(Filters.sticker, sticker_from_telegram), 100)
global_vars.dp.add_handler(MessageHandler(Filters.audio, audio_from_telegram), 100)
global_vars.dp.add_handler(MessageHandler(Filters.photo, photo_from_telegram), 100)
global_vars.dp.add_handler(MessageHandler(Filters.document, document_from_telegram), 100)
global_vars.dp.add_handler(MessageHandler(Filters.video, video_from_telegram), 100)


@global_vars.qq_bot.listener((RcvdGroupMessage, ), 100)  # priority 100
def new(message):
    # logging.info('(' + message.qq + '): ' + message.text)

    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)

    text = message.text  # get message text

    text, _ = re.subn(r'\[CQ:image.*?\]', '', text)  # clear CQ:image in text

    # replace special characters
    text, _ = re.subn('&amp;', '&', text)
    text, _ = re.subn('&#91;', '[', text)
    text, _ = re.subn('&#93;', ']', text)
    text, _ = re.subn('&#44;', ',', text)

    text = cq_emoji_regex.sub(lambda x: chr(int(x.group(1))), text)  # replace [CQ:emoji,id=*]
    text = qq_face_regex.sub(lambda x: qq_emoji_list[int(x.group(1))] if int(x.group(1)) in qq_emoji_list else '\u2753', text)  # replace [CQ:face,id=*]

    def replace_name(qq_number):  # replace each qq number with preset id
        qq_number = qq_number.group(1)
        if int(qq_number) == QQ_BOT_ID:
            return '@bot'
        result = '@' + get_qq_name(int(qq_number), forward_index)
        result = result.replace(':', ' ')
        return result

    text = CQAt.PATTERN.sub(replace_name, text)  # replace CQAt to @username

    # replace CQ:share/CQ:music, could be improved

    if cq_share_regex.match(message.text):
        url, title, content, image_url = extract_cq_share(message.text)
        text = title + '\n' + url
    elif cq_music_regex.match(message.text):
        text = 'some music'

    # replace QQ number to group member name, get full message text
    full_msg = get_qq_name(int(message.qq), forward_index) + ': ' + text.strip()

    # send pictures to Telegram group
    pic_send_mode = 2
    # mode = 0 -> direct mode: send cqlink to tg server
    # mode = 1 -> (deprecated) download mode: download to local，send local link to tg server
    # mode = 2 -> download mode: download to local, upload from disk to tg server
    image_num = 0
    for matches in CQImage.PATTERN.finditer(message.text):
        image_num = image_num + 1
        filename = matches.group(1)
        url = cq_get_pic_url(filename)
        pic = url
        if pic_send_mode == 1:
            cq_download_pic(filename)
            pic = SERVER_PIC_URL + filename
        elif pic_send_mode == 2:
            cq_download_pic(filename)
            pic = open(os.path.join(CQ_IMAGE_ROOT, filename), 'rb')
        # gif pictures send as document
        if filename.lower().endswith('gif'):
            try:
                # the first image in message attach full message text
                if image_num == 1:
                    global_vars.tg_bot.sendDocument(tg_group_id, pic, caption=full_msg)
                else:
                    global_vars.tg_bot.sendDocument(tg_group_id, pic)
            except BadRequest:
                # when error occurs, download picture and send link instead
                error(message)
                traceback.print_exc()
                if pic_send_mode == 0:
                    cq_download_pic(filename)
                pic = get_short_url(SERVER_PIC_URL + filename)
                global_vars.tg_bot.sendMessage(tg_group_id, pic + '\n' + full_msg)

        # jpg/png pictures send as photo
        else:
            try:
                # the first image in message attach full message text
                if image_num == 1:
                    global_vars.tg_bot.sendPhoto(tg_group_id, pic, caption=full_msg)
                else:
                    global_vars.tg_bot.sendPhoto(tg_group_id, pic)
            except BadRequest:
                # when error occurs, download picture and send link instead
                error(message)
                traceback.print_exc()
                if pic_send_mode == 0:
                    cq_download_pic(filename)
                my_url = get_short_url(SERVER_PIC_URL + filename)
                pic = my_url
                global_vars.tg_bot.sendMessage(tg_group_id, pic + '\n' + full_msg)

    # send plain text message with bold group member name
    if image_num == 0:
        full_msg_bold = '<b>' + get_qq_name(int(message.qq), forward_index) + '</b>: ' + text.strip().replace('<', '&lt;').replace('>', '&gt;')
        global_vars.tg_bot.sendMessage(tg_group_id, full_msg_bold, parse_mode='HTML')


@command_listener('[pic link on]', description='enable pic link mode, only available when JQ_MODE=False')
def drive_mode_on(forward_index, tg_group_id, qq_group_id):
    if JQ_MODE:
        return
    PIC_LINK_MODE[forward_index] = True
    msg = 'QQ 图片链接模式已启动'
    global_vars.tg_bot.sendMessage(tg_group_id, msg)
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))


@command_listener('[pic link off]', description='disable pic link mode, only available when JQ_MODE=False')
def drive_mode_on(forward_index, tg_group_id, qq_group_id):
    if JQ_MODE:
        return
    PIC_LINK_MODE[forward_index] = False
    msg = 'QQ 图片链接模式已关闭'
    global_vars.tg_bot.sendMessage(tg_group_id, msg)
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))
