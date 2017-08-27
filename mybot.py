#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import logging

from collections import namedtuple

from utils import *
import global_vars
from cq_utils import *
from short_url import *
from qq_emoji_list import *
from special_modes import *
from image_operations import *
from special_sticker_list import *

from cqsdk import CQBot, CQAt, CQImage, RcvdPrivateMessage, RcvdGroupMessage,\
    SendGroupMessage, GetGroupMemberList, RcvGroupMemberList
from telegram.ext import Updater, CommandHandler, InlineQueryHandler,\
    ConversationHandler, RegexHandler, MessageHandler, Filters
from telegram.error import BadRequest, TimedOut, NetworkError

logging.basicConfig(filename='bot.log', level=logging.INFO)

qq_bot = CQBot(CQ_PORT)
tg_bot = None
global_vars.qq_bot = qq_bot
global_vars.tg_bot = tg_bot
global_vars.tg_bot_id = int(TOKEN.split(':')[0])


def tg_get_pic_url(file_id, pic_type):
    """
    download image from Telegram Server, and generate new image link that send to QQ group
    :param file_id: telegram file id
    :param pic_type: picture extension name
    :return:
    """
    file = tg_bot.getFile(file_id)
    urlretrieve(file.file_path, os.path.join(CQ_IMAGE_ROOT, file_id))
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
    forward_from = get_forward_from(update.message)
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
    if JQ_MODE:
        text = '[CQ:image,file=' + file_id + '.jpg]'
    else:
        text = '[图片, 请点击查看' + pic_url + ']'

    if update.message.caption:
        text += update.message.caption
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

    logging.info(update.message)

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


def emoji_to_cqemoji(text):
    new_text = ''
    for char in text:
        if 8252 <= ord(char) < 12287 or 126980 < ord(char) < 129472:
            new_text += "[CQ:emoji,id=" + str(ord(char)) + "]"
        else:
            new_text += char
    return new_text


def sticker_from_telegram(bot, update):
    
    logging.info(update.message)
    
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
        if JQ_MODE:
            text = '[CQ:image,file=' + file_id + '.png]'
        else:
            text = '[' + update.message.sticker.emoji + ' sticker, 请点击查看' + pic_url + ']'
    else:
        text = '[' + update.message.sticker.emoji + ' sticker]'

    text = emoji_to_cqemoji(text)

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
    logging.info(update.message)

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
    elif text.startswith('//'):
        return
    else:
        if get_drive_mode(forward_index):  # check drive mode
            return

        sender_name = get_full_user_name(update.message.from_user)
        forward_from = get_forward_from(update.message)
        reply_to = get_reply_to(update.message.reply_to_message)

        if forward_from and update.message.forward_from.id == global_vars.tg_bot_id:
            left_start = text.find(': ')
            if left_start != -1:
                text = text[left_start + 2:]
        text = emoji_to_cqemoji(text)

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
    messages.append(Message(message.qq, int(time.time()), message.text))  # add to message queue

    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if forward_index == -1:
        return  # no forward rule, return

    text = message.text  # get message text

    # handle send sticker instructions
    if text.startswith('!'):
        sticker = text.lstrip('!')
        if sticker in special_sticker_list:
            global_vars.tg_bot.sendSticker(tg_group_id, special_sticker_list[sticker])
            return

    name_list = qq_name_lists[forward_index]  # get reflect of this QQ group member

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
        if qq_number in qq_name_lists[0]:
            return '@' + qq_name_lists[0][qq_number]
        else:
            return '@' + qq_number

    text = CQAt.PATTERN.sub(replace_name, text)  # replace qq's at to telegram's

    # replace CQ:share/CQ:music

    if cq_share_regex.match(message.text):
        url, title, content, image_url = extract_cq_share(message.text)
        text = title + '\n' + url
    elif cq_music_regex.match(message.text):
        text = 'some music'

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
    elif text == '[reload namelist]':
        reload_qq_namelist()
        qq_bot.send(SendGroupMessage(
            group=qq_group_id,
            text='QQ群名片已重置'
        ))

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
            except BadRequest:
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
            except BadRequest:
                # when error occurs, download picture and send link instead
                error(message)
                traceback.print_exc()
                qq_download_pic(filename)
                my_url = get_short_url(SERVER_PIC_URL + filename)
                tg_bot.sendMessage(tg_group_id, my_url + '\n' + full_msg)

    # send plain text message with bold group member name
    if image_num == 0:
        if str(message.qq) in name_list:
            full_msg_bold = '<b>' + name_list[str(message.qq)] + '</b>: ' + text.strip().replace('<', '&lt;').replace('>', '&gt;')
        else:
            full_msg_bold = '<b>' + str(message.qq) + '</b>: ' + text.strip().replace('<', '&lt;').replace('>', '&gt;')
            tg_bot.sendMessage(tg_group_id, full_msg_bold, parse_mode='HTML')


@qq_bot.listener(RcvGroupMemberList)
def handle_group_member_list(message):
    global qq_name_lists
    json_list = read_group_member_list(message.path.split('\\')[-1])
    for key in json_list:
        json_list[key] = json_list[key].replace(':', ' ')
    json_list[str(QQ_BOT_ID)] = 'bot'
    qq_name_lists.append(json_list)
    print(qq_name_lists)


def reload_qq_namelist():
    global qq_name_lists
    qq_name_lists = []
    for (qq, tg, sticker, drive) in FORWARD_LIST:
        qq_bot.send(GetGroupMemberList(group=qq))


def main():
    global qq_name_lists
    global job_queue
    global tg_bot
    global qq_bot

    updater = Updater(TOKEN)
    job_queue = updater.job_queue
    tg_bot = updater.bot
    qq_bot.start()
    reload_qq_namelist()
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text | Filters.command, text_from_telegram))
    dp.add_handler(MessageHandler(Filters.sticker, sticker_from_telegram))
    dp.add_handler(MessageHandler(Filters.audio, audio_from_telegram))
    dp.add_handler(MessageHandler(Filters.photo, photo_from_telegram))
    dp.add_handler(MessageHandler(Filters.document, document_from_telegram))
    dp.add_handler(MessageHandler(Filters.video, video_from_telegram))

    dp.add_error_handler(error)
    # Start the Bot
    updater.start_polling(poll_interval=1.0, timeout=200)

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
