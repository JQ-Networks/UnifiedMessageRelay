#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from collections import namedtuple
from pprint import pprint
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, \
    ConversationHandler, RegexHandler, MessageHandler, Filters
from image_operations import *
from short_url import *
from utils import CQ_IMAGE_ROOT, error, reply
from bot_constant import *
from qq_emoji_list import *
from special_sticker_list import *
from cq_utils import *
from cqsdk import CQBot, CQAt, CQImage, RcvdPrivateMessage, RcvdGroupMessage,\
SendGroupMessage


from logger import *
logging.basicConfig(filename='bot.log', level=logging.DEBUG)

tg_bot_id = int(TOKEN.split(':')[0])
qq_bot = CQBot(11235)
tg_bot = None


def get_full_user_name(user):
    name = ''
    if user.first_name:
        name = user.first_name
        if user.last_name:
            name += ' ' + user.last_name
    elif user.last_name:
        name = user.last_name
    return name


def get_forward_from(forward_from):
    if forward_from:
        result = get_full_user_name(forward_from)
        return '(forwarded from ' + result + ')'
    else:
        return ''


def get_reply_to(reply_to_message):
    if reply_to_message:
        if reply_to_message.from_user.id == tg_bot_id:
            if reply_to_message.text:
                reply_to = 'reply to ' + reply_to_message.text.split(":")[0]
            else:
                reply_to = 'reply to ' + reply_to_message.caption.split(":")[0]
        else:
            reply_to = get_full_user_name(reply_to_message.from_user)
        return '(' + reply_to + ')'
    else:
        return ''


def get_forward_index(qq_group_id=0, tg_group_id=0):
    """
    Get forward index from FORWARD_LIST
    :param qq_group_id: optional, the qq group id, either this or tg_group_id must be valid
    :param tg_group_id: optional, the telegram group id, either this or qq_group_id must be valid
    :return: qq_group_id, tg_group_id, forward_index
    """
    for idx, (qq, tg, sticker, drive) in enumerate(FOWARD_LIST):
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
    FOWARD_LIST[forward_index][3] = status
    tg_bot.sendMessage(tg_group_id, msg)
    qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))


def get_sticker_link_mode(forward_index):
    return FOWARD_LIST[forward_index][3]


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
    tg_bot.sendMessage(tg_group_id, msg)
    qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))


def get_drive_mode(forward_index):
    return FOWARD_LIST[forward_index][2]


def tg_get_pic_url(file_id, pic_type):
    """
    download image from Telegram Server, and generate new image link that send to QQ group
    :param file_id: telegram file id
    :param pic_type: picture extension name
    :return:
    """
    file_path = tg_bot.getFile(file_id)
    urlretrieve('https://api.telegram.org/file/bot' + TOKEN + "/" + file_path[u'file_path'], os.path.join(CQ_IMAGE_ROOT, file_id))
    if pic_type == 'jpg':
        create_jpg_image(CQ_IMAGE_ROOT, file_id)
        pic_url = get_short_url(SERVER_PIC_URL + file_id + '.jpg')
        return pic_url
    elif pic_type == 'png':
        create_png_image(CQ_IMAGE_ROOT, file_id)
        pic_url = get_short_url(SERVER_PIC_URL + file_id + '.png')
        return pic_url
    return ''


def cq_send(update, text, qq_group_id):
    sender_name = get_full_user_name(update.message.from_user)
    forward_from = get_forward_from(update.message.foward_from)
    reply_to = get_reply_to(update.message.reply_to_message)

    qq_bot.send(SendGroupMessage(
        group=qq_group_id,
        text=sender_name + reply_to + forward_from + ': ' + text
    ))


def photo_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    if tg_group_id > 0:
        return  # chat id > 0 means private chat, ignore

    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    if forward_index == -1:
        return

    if get_drive_mode(forward_index):  # check drive mode
        return

    file_id = update.message.photo[-1].file_id
    pic_url = tg_get_pic_url(file_id, 'jpg')
    text = '[图片, 请点击查看' + pic_url + ']'

    cq_send(update, text, qq_group_id)


def video_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    if tg_group_id > 0:
        return  # chat id > 0 means private chat, ignore

    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    if forward_index == -1:
        return

    if get_drive_mode(forward_index):  # check drive mode
        return

    text = '[视频]'

    cq_send(update, text, qq_group_id)


def audio_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    if tg_group_id > 0:
        return  # chat id > 0 means private chat, ignore

    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    if forward_index == -1:
        return

    if get_drive_mode(forward_index):  # check drive mode
        return

    text = '[音频]'

    cq_send(update, text, qq_group_id)


def document_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    if tg_group_id > 0:
        return  # chat id > 0 means private chat, ignore

    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    if forward_index == -1:
        return

    if get_drive_mode(forward_index):  # check drive mode
        return

    text = '[文件]'

    cq_send(update, text, qq_group_id)


def sticker_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    if tg_group_id > 0:
        return  # chat id > 0 means private chat, ignore

    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    if forward_index == -1:
        return

    if get_drive_mode(forward_index):  # check drive mode
        return

    if get_sticker_link_mode(forward_index):
        file_id = update.message.sticker.file_id
        pic_url = tg_get_pic_url(file_id, 'png')
        text = '[' + update.message.sticker.emoji + ' sticker, 请点击查看' + pic_url + ']'
    else:
        text = '[' + update.message.sticker.emoji + ']'

    if update.message.caption:
        text = text + ' ' + update.message.caption

    cq_send(update, text, qq_group_id)


def text_from_telegram(bot, update):
    """
    handle message from telegram
    :param bot:
    :param update:
    :return:
    """
    logging.debug(update)
    pprint(update)  # print raw message

    tg_group_id = update.message.chat_id  # telegram group id
    if update.message.text:
        text = update.message.text
        if text == '[showgroupid]':
            tg_bot.sendMessage(tg_group_id, u'DEBUG: tg_group_id = ' + str(tg_group_id))
            return
    if tg_group_id > 0:
        return  # chat id > 0 means private chat, ignore

    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    if forward_index == -1:
        return  # no forward rule, return

    text = update.message.text

    if text == '[sticker link on]':
        set_sticker_link_mode(forward_index, True, tg_group_id, qq_group_id)
        return
    elif text == '[sticker link off]':
        set_sticker_link_mode(forward_index, False, tg_group_id, qq_group_id)
        return
    elif text == '[drive mode on]':
        set_drive_mode(forward_index, True, tg_group_id, qq_group_id)
        return
    elif text == '[drive mode off]':
        set_drive_mode(forward_index, False, tg_group_id, qq_group_id)
        return
    else:
        if get_drive_mode(forward_index):  # check drive mode
            return

        sender_name = get_full_user_name(update.message.from_user)
        forward_from = get_forward_from(update.message.foward_from)
        reply_to = get_reply_to(update.message.reply_to_message)

        new_text = ''
        for char in text:
            if 8986 <= char < 12287 or 126980 < char < 129472:
                new_text += "[CQ:emoji,id=" + str(char) + "]"
            else:
                new_text += char

        if len(text) == 0:
            text = '[不支持的消息类型]'

        qq_bot.send(SendGroupMessage(
            group=qq_group_id,
            text=sender_name + reply_to + forward_from + ': ' + text
        ))


# QQ group message receive
Message = namedtuple('Manifest', ('qq', 'time', 'text'))
messages = []  # Message queue
qq_name_lists = None


@qq_bot.listener((RcvdGroupMessage, ))
def new(message):
    logging.info('(' + message.qq + '): ' + message.text)
    messages.append(Message(message.qq, int(time.time()), message.text)) # add to message queue

    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if forward_index == -1:
        return  # no forward rule, return

    text = message.text  # get message text

    # handle send sticker instructions
    if text.startswith('!'):
        sticker = text.lstrip('!')
        if sticker in special_sticker_list:
            tg_bot.sendSticker(tg_group_id, special_sticker_list[sticker])
            return

    name_list = qq_name_lists[forward_index]  # get reflect of this QQ group member

    text, _ = re.subn(r'\[CQ:image.*?\]', '', text)  # clear CQ:image in text

    # replace special characters
    text, _ = re.subn('&amp;', '&', text)
    text, _ = re.subn('&#91;', '[', text)
    text, _ = re.subn('&#93;', ']', text)
    text, _ = re.subn('&#44;', ',', text)

    text = cq_emoji_regex.sub(lambda x: chr(int(x)), text)  # replace [CQ:emoji,id=*]
    text = qq_face_regex.sub(lambda x: qq_emoji_list[int(x)], text)  # replace [CQ:face,id=*]

    def replace_name(qq_number):  # replace each qq number with preset id
        qq_number = qq_number.group(1)
        if qq_number in qq_name_lists[0]:
            return '@' + qq_name_lists[0][qq_number]
        else:
            return '@' + qq_number

    text = CQAt.PATTERN.sub(replace_name, text)  # replace qq's at to telegram's

    # replace CQ:share/CQ:music
    new_text = ''
    if cq_share_regex.match(message.text):
        url, title, content, image_url = extract_cq_share(message.text)
        new_text = title + '\n' + url
    elif cq_music_regex.match(message.text):
        new_text = 'some music'

    # handle special instructions
    if text == '[sticker link on]':
        set_sticker_link_mode(forward_index, True, tg_group_id, qq_group_id)
        return
    elif text == '[sticker link off]':
        set_sticker_link_mode(forward_index, False, tg_group_id, qq_group_id)
        return
    elif text == '[drive mode on]':
        set_drive_mode(forward_index, True, tg_group_id, qq_group_id)
        return
    elif text == '[drive mode off]':
        set_drive_mode(forward_index, False, tg_group_id, qq_group_id)
        return

    # replace QQ number to group member name, get full message text
    if str(message.qq) in name_list:
        full_msg = name_list[str(message.qq)] + ': ' + text.strip()
    else:
        full_msg = str(message.qq) + ': ' + text.strip()

    # send pictures to Telegram group
    image_num = 0
    for match in CQImage.PATTERN.finditer(message.text):
        image_num = image_num + 1
        filename = match.group(1)
        url = qq_get_pic_url(filename)
        # gif pictures send as document
        if filename.lower().endswith('gif'):
            try:
                # the first image in message attach full message text
                if image_num == 1:
                    tg_bot.sendDocument(tg_group_id, url, caption=full_msg)
                else:
                    tg_bot.sendDocument(tg_group_id, url)
            except:
                # when error occurs, download picture and send link instead
                error(message)
                traceback.print_exc()
                qq_download_pic(filename)
                my_url = get_short_url(SERVER_PIC_URL + filename)
                tg_bot.sendMessage(tg_group_id, my_url + '\n' + full_msg)

        # jpg/png pictures send as photo
        else:
            try:
                # the first image in message attach full message text
                if image_num == 1:
                    tg_bot.sendPhoto(tg_group_id, url, caption=full_msg)
                else:
                    tg_bot.sendPhoto(tg_group_id, url)
            except:
                # when error occurs, download picture and send link instead
                error(message)
                traceback.print_exc()
                qq_download_pic(filename)
                my_url = get_short_url(SERVER_PIC_URL + filename)
                tg_bot.sendMessage(tg_group_id, my_url + '\n' + full_msg)

    # send plain text message with bold group member name
    if image_num == 0:
        if str(message.qq) in name_list:
            full_msg_bold = '*' + name_list[str(message.qq)] + '*: ' + text.strip()
        else:
            full_msg_bold = '*' + str(message.qq) + '*: ' + text.strip()
        tg_bot.sendMessage(tg_group_id, full_msg_bold, parse_mode='Markdown')


def main():
    global qq_name_lists
    global tg_bot
    # reflect of QQ number and QQ group member name
    with open('namelist.json', 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
        qq_name_lists = data

    global job_queue

    updater = Updater(TOKEN)
    job_queue = updater.job_queue
    tg_bot = updater.bot
    qq_bot.start()
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text, text_from_telegram))
    dp.add_handler(MessageHandler(Filters.sticker, sticker_from_telegram))
    dp.add_handler(MessageHandler(Filters.audio, audio_from_telegram))
    dp.add_handler(MessageHandler(Filters.photo, photo_from_telegram))
    dp.add_handler(MessageHandler(Filters.document, document_from_telegram))
    dp.add_handler(MessageHandler(Filters.video, video_from_telegram))

    dp.add_error_handler(error)
    # Start the Bot
    updater.start_polling()

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
