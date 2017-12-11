from bot_constant import FORWARD_LIST, JQ_MODE, QQ_BOT_ID
import global_vars
from utils import get_forward_index, CQ_IMAGE_ROOT, SERVER_PIC_URL, \
    get_forward_from, get_reply_to, get_full_user_name, error, decode_cq_escape, \
    cq_send, get_qq_name
from cqsdk import SendGroupMessage, RcvdGroupMessage, CQAt, CQImage
from command import command_listener
from PIL import Image
from configparser import ConfigParser
import requests
from urllib.request import urlretrieve
from telegram.ext import MessageHandler, Filters
from telegram.error import BadRequest
from cq_utils import cq_emoji_regex, cq_face_regex, cq_image_regex, cq_image_simple_regex, \
    cq_bface_regex, cq_sface_regex
import traceback
import telegram
import json
import os
import re

"""
request set CQ_IMAGE_ROOT SERVER_PIC_URL JQ_MODE
"""
# region utils

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

qq_sface_list = {
    1: '[拜拜]',
    2: '[鄙视]',
    3: '[菜刀]',
    4: '[沧桑]',
    5: '[馋了]',
    6: '[吃惊]',
    7: '[微笑]',
    8: '[得意]',
    9: '[嘚瑟]',
    10: '[瞪眼]',
    11: '[震惊]',
    12: '[鼓掌]',
    13: '[害羞]',
    14: '[好的]',
    15: '[惊呆了]',
    16: '[静静看]',
    17: '[可爱]',
    18: '[困]',
    19: '[脸红]',
    20: '[你懂的]',
    21: '[期待]',
    22: '[亲亲]',
    23: '[伤心]',
    24: '[生气]',
    25: '[摇摆]',
    26: '[帅]',
    27: '[思考]',
    28: '[震惊哭]',
    29: '[痛心]',
    30: '[偷笑]',
    31: '[挖鼻孔]',
    32: '[抓狂]',
    33: '[笑着哭]',
    34: '[无语]',
    35: '[捂脸]',
    36: '[喜欢]',
    37: '[笑哭]',
    38: '[疑惑]',
    39: '[赞]',
    40: '[眨眼]'
}


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
    # urlretrieve(file.file_path, os.path.join(CQ_IMAGE_ROOT, file_id))  # download image
    file.download(custom_path=os.path.join(CQ_IMAGE_ROOT, file_id))
    if pic_type == 'jpg':
        create_jpg_image(CQ_IMAGE_ROOT, file_id)
        pic_url = get_short_url(SERVER_PIC_URL + file_id + '.jpg')
        return pic_url
    elif pic_type == 'png':
        create_png_image(CQ_IMAGE_ROOT, file_id)
        pic_url = get_short_url(SERVER_PIC_URL + file_id + '.png')
        return pic_url
    return ''


# endregion

PIC_LINK_MODE = []  # pic_link_mode per group

for forward in FORWARD_LIST:  # initialize
    PIC_LINK_MODE.append(forward['Pic_link'])


def photo_from_telegram(bot, update):
    if update.message:
        tg_group_id = update.message.chat_id  # telegram group id
        qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))

        file_id = update.message.photo[-1].file_id
        pic_url = tg_get_pic_url(file_id, 'jpg')
        if JQ_MODE:
            text = '[CQ:image,file=' + file_id + '.jpg]'
        else:
            text = '[ 图片, 请点击查看' + pic_url + ' ]'
        if update.message.caption:
            text += update.message.caption

        cq_send(update, text, qq_group_id)
    elif update.edited_message:
        tg_group_id = update.edited_message.chat_id  # telegram group id
        qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))

        file_id = update.edited_message.photo[-1].file_id
        pic_url = tg_get_pic_url(file_id, 'jpg')
        if JQ_MODE:
            text = '[CQ:image,file=' + file_id + '.jpg]'
        else:
            text = '[图片, 请点击查看' + pic_url + ' ]'
        if update.edited_message.caption:
            text += update.edited_message.caption
        cq_send(update, text, qq_group_id, edited=True)


def video_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(
        tg_group_id=int(tg_group_id))
    text = '[视频]'
    cq_send(update, text, qq_group_id)


def audio_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(
        tg_group_id=int(tg_group_id))
    text = '[音频]'
    cq_send(update, text, qq_group_id)


def document_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(
        tg_group_id=int(tg_group_id))
    text = '[文件]'
    cq_send(update, text, qq_group_id)


def sticker_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(
        tg_group_id=int(tg_group_id))
    file_id = update.message.sticker.file_id
    if JQ_MODE: # If use CQPro, send sticker as photo.
        text = '[CQ:image,file=' + file_id + '.png]'
    elif PIC_LINK_MODE[forward_index]: # If not turn on JQ_MODE but enable Pic_link, send sticker with link.
        pic_url = tg_get_pic_url(file_id, 'png')
        text = '[ ' + update.message.sticker.emoji + \
            ' sticker, 请点击查看' + pic_url + ' ]'
    else: # Seem user set JQ_MODE and Pic_Link both False, only send emoji.
        text = '[' + update.message.sticker.emoji + ' sticker]'
    cq_send(update, text, qq_group_id)


def text_from_telegram(bot, update):
    if update.message:
        tg_group_id = update.message.chat_id  # telegram group id
        qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))

        text = update.message.text
        if text.startswith('//'):  # feature, comment will no be send to qq
            return
        else:
            cq_send(update, text, qq_group_id)
    elif update.edited_message:
        tg_group_id = update.edited_message.chat_id  # telegram group id
        qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))

        text = update.edited_message.text
        if text.startswith('//'):  # feature, comment will no be send to qq
            return
        else:
            cq_send(update, text, qq_group_id, edited=True)


global_vars.dp.add_handler(MessageHandler(Filters.text | Filters.command, text_from_telegram, edited_updates=True), 100)  # priority 100
global_vars.dp.add_handler(MessageHandler(Filters.sticker, sticker_from_telegram), 100)
global_vars.dp.add_handler(MessageHandler(Filters.audio, audio_from_telegram), 100)
global_vars.dp.add_handler(MessageHandler(Filters.photo, photo_from_telegram, edited_updates=True), 100)
global_vars.dp.add_handler(MessageHandler(Filters.document, document_from_telegram), 100)
global_vars.dp.add_handler(MessageHandler(Filters.video, video_from_telegram), 100)


@global_vars.qq_bot.listener((RcvdGroupMessage, ), 100)  # priority 100
def new(message):
    # logging.info('(' + message.qq + '): ' + message.text)

    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)

    text = message.text  # get message text

    # text, _ = cq_image_regex.subn('', text)   # clear CQ:image in text

    # replace special characters
    text = decode_cq_escape(text)

    text = cq_emoji_regex.sub(lambda x: chr(int(x.group(1))), text)  # replace [CQ:emoji,id=*]
    text = cq_face_regex.sub(lambda x: qq_emoji_list[int(x.group(1))] if int(x.group(1)) in qq_emoji_list else '\u2753', text)  # replace [CQ:face,id=*]
    text = cq_bface_regex.sub('\u2753', text)  # replace bface to '?'
    text = cq_sface_regex.sub(lambda x: qq_sface_list[int(x.group(1)) & 255] if int(x.group(1)) > 100000 and int(x.group(1)) & 255 in qq_sface_list else '\u2753', text)  # replace [CQ:sface,id=*], https://cqp.cc/t/26206

    def replace_name(qq_number):  # replace each qq number with preset id
        qq_number = qq_number.group(1)
        if int(qq_number) == QQ_BOT_ID:
            return '@bot'
        result = '@' + get_qq_name(int(qq_number), forward_index)
        result = result.replace(':', ' ')
        return result

    text = CQAt.PATTERN.sub(replace_name, text)  # replace CQAt to @username

    # send pictures to Telegram group
    pic_send_mode = 2
    # mode = 0 -> direct mode: send cqlink to tg server
    # mode = 1 -> (deprecated) download mode: download to local，send local link to tg server
    # mode = 2 -> download mode: download to local, upload from disk to tg server
    message_parts = cq_image_simple_regex.split(text)
    message_parts_count = len(message_parts)
    image_num = message_parts_count - 1
    if image_num == 0:
        # send plain text message with bold group member name
        full_msg_bold = '<b>' + get_qq_name(int(message.qq), forward_index) + '</b>: ' + text.strip().replace('<', '&lt;').replace('>', '&gt;')
        global_vars.tg_bot.sendMessage(tg_group_id, full_msg_bold, parse_mode='HTML')
    else:
        if message_parts[0]:
            part_msg_bold = '<b>' + get_qq_name(int(message.qq), forward_index) + '</b>: ' +\
                        '(1/' + str(message_parts_count) + ')' + message_parts[0].strip().replace('<', '&lt;').replace('>', '&gt;')
            global_vars.tg_bot.sendMessage(tg_group_id, part_msg_bold, parse_mode='HTML')
            part_index = 1
        else:
            message_parts.pop(0)
            message_parts_count -= 1
            part_index = 0
        for matches in CQImage.PATTERN.finditer(message.text):
            # replace QQ number to group member name, get full message text
            if message_parts_count == 1:
                part_msg = get_qq_name(int(message.qq), forward_index) + ': ' + message_parts[part_index].strip()
            else:
                part_msg = get_qq_name(int(message.qq), forward_index) + ': ' + '(' + str(part_index+1) + '/' + str(message_parts_count) + ')' + message_parts[part_index].strip()
            part_index += 1
            decode_cq_escape(part_msg)
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
                    global_vars.tg_bot.sendDocument(tg_group_id, pic, caption=part_msg)
                except BadRequest:
                    # when error occurs, download picture and send link instead
                    error(message)
                    traceback.print_exc()
                    if pic_send_mode == 0:
                        cq_download_pic(filename)
                    pic = get_short_url(SERVER_PIC_URL + filename)
                    global_vars.tg_bot.sendMessage(tg_group_id, pic + '\n' + part_msg)

            # jpg/png pictures send as photo
            else:
                try:
                    # the first image in message attach full message text
                    global_vars.tg_bot.sendPhoto(tg_group_id, pic, caption=part_msg)
                except BadRequest:
                    # when error occurs, download picture and send link instead
                    error(message)
                    traceback.print_exc()
                    if pic_send_mode == 0:
                        cq_download_pic(filename)
                    my_url = get_short_url(SERVER_PIC_URL + filename)
                    pic = my_url
                    global_vars.tg_bot.sendMessage(tg_group_id, pic + '\n' + part_msg)
    return True


@command_listener('[pic link on]', description='enable pic link mode, only available when JQ_MODE=False')
def drive_mode_on(forward_index, tg_group_id, tg_user, qq_group_id, qq):
    if JQ_MODE:
        return
    PIC_LINK_MODE[forward_index] = True
    msg = 'QQ 图片链接模式已启动'
    global_vars.tg_bot.sendMessage(tg_group_id, msg)
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))


@command_listener('[pic link off]', description='disable pic link mode, only available when JQ_MODE=False')
def drive_mode_off(forward_index, tg_group_id, tg_user, qq_group_id, qq):
    if JQ_MODE:
        return
    PIC_LINK_MODE[forward_index] = False
    msg = 'QQ 图片链接模式已关闭'
    global_vars.tg_bot.sendMessage(tg_group_id, msg)
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))
