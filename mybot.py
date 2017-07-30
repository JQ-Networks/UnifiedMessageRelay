#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import json
import time
import logging
import requests
import threading
import traceback

from PIL            import Image
from collections    import namedtuple
from configparser   import ConfigParser
from urllib.request import urlretrieve

# constants and reflects
from short_url            import *
from bot_constant import *
from qq_emoji_list        import *
from image_operations     import *
from special_sticker_list import *

# import from telepot
import telepot
from telepot.loop import MessageLoop

# import from coolq-sdk
from utils import CQ_IMAGE_ROOT, error, reply
from cqsdk import CQBot, CQAt, CQImage, RE_CQ_SPECIAL
from cqsdk import GroupMemberDecrease, GroupMemberIncrease
from cqsdk import RcvdPrivateMessage, RcvdGroupMessage, RcvdDiscussMessage
from cqsdk import SendPrivateMessage, SendGroupMessage, SendDiscussMessage

# global variables

## QQ bot
qq_bot = CQBot(11235)

## Telegram bot
tg_bot = telepot.Bot(TOKEN)
tg_bot_id = int(TOKEN.split(':')[0])

## sticker link mode switches (0 -> disable, 1 -> enable)
sticker_link_modes = [0] * len(forward_ids)

## drive mode switches (0 -> disable, 1 -> enable)
drive_modes = [0] * len(forward_ids)

## reflect of QQ number and QQ group member name
with open('namelist.json', 'r', encoding="utf-8") as f:
    data = json.loads(f.read())
    qq_name_lists = data

## config logging
logging.basicConfig(filename='bot.log', level=logging.INFO)

def tg_get_pic_url(file_id, pic_type):
    ## download image from Telegram Server, and generate new image link that send to QQ group
    file_path = tg_bot.getFile(file_id)
    urlretrieve('https://api.telegram.org/file/bot' + tg_token + "/" + file_path[u'file_path'], os.path.join(CQ_IMAGE_ROOT, file_id))
    if pic_type == 'jpg':
        create_jpg_image(CQ_IMAGE_ROOT, file_id)
        pic_url = get_short_url(server_pic_url + file_id + '.jpg')
    elif pic_type == 'png':
        create_png_image(CQ_IMAGE_ROOT, file_id)
        pic_url = get_short_url(server_pic_url + file_id + '.png')
    return pic_url


# telegram message receive
def tg_msg_receive(msg):
    global tg_bot
    global qq_bot
    global tg_bot_id
    global forward_ids
    global sticker_link_modes
    global drive_modes
    global server_pic_url

    ## log message
    logging.info(msg)

    ## drop if not Telegram group message 
    chat_type = msg[u'chat'][u'type']
    if chat_type != u'group':
        return
    
    ## get QQ group to forward message
    tg_group_id = msg[u'chat'][u'id']
    qq_group_id, _, forward_index = get_forward_info(0, int(tg_group_id))
    
    ### special instruction: show group id
    if u'text' in msg and msg[u'text'] == u'[showgroupid]':
        tg_bot.sendMessage(tg_group_id, u'DEBUG: tg_group_id = ' + str(tg_group_id));
        return

    if forward_index == -1:
        return
    
    ## get sender name
    sender = msg[u'from'][u'first_name']
    if u'last_name' in msg[u'from']:
        sender += " " +  msg[u'from'][u'last_name']
    
    ## get text in message
    text = u''

    ### plain text
    if u'text' in msg:
        text = msg[u'text']

    ### photo message
    elif u'photo' in msg:
        fileId = msg[u'photo'][-1][u'file_id']
        pic_url = tg_get_pic_url(fileId, 'jpg')
        text = u'[图片, 请点击查看' + pic_url + u']'

    ### video message (show placeholder)
    elif u'video' in msg:
        text = u'[视频]'

    ### audio message (show placeholder)
    elif u'audio' in msg:
        text = u'[音频]'

    ### document message (show placeholder)
    elif u'document' in msg:
        text = u'[文件]'

    ### sticker message
    elif u'sticker' in msg:
        text = u'[' + msg[u'sticker'][u'emoji'] + u' sticker]'
        file_id = msg[u'sticker'][u'file_id']

        #### check sticker link mode
        if sticker_link_modes[forward_index] == 1:
            pic_url = tg_get_pic_url(file_id, 'png')
            text = u'[' + msg[u'sticker'][u'emoji'] + ' sticker, 请点击查看' + pic_url + u']'
    
    ## add picture caption to text
    if u'caption' in msg:
        text = text + ' ' + msg[u'caption']
    
    ## handle special instructions
    if text == u'[sticker link on]':
        set_sticker_link_mode(forward_index, 1, tg_group_id, qq_group_id)
    elif text == u'[sticker link off]':
        set_sticker_link_mode(forward_index, 0, tg_group_id, qq_group_id)
    elif text == u'[drive mode on]':
        set_drive_mode(forward_index, 1, tg_group_id, qq_group_id)
    elif text == u'[drive mode off]':
        set_drive_mode(forward_index, 0, tg_group_id, qq_group_id)
    
    else:
        ## add `forward from` tag
        forwardFrom = u''
        if u'forward_from' in msg:
            forward_sender = msg[u'forward_from'][u'first_name']
            if forward_sender == 'null' and u'forward_from_chat' in msg:
                forward_sender = msg[u'forward_from_chat'][u'title']
            if u'last_name' in msg[u'forward_from']:
                forward_sender += " " +  msg[u'forward_from'][u'last_name']
            forwardFrom = u' (forwarded from ' + forward_sender + u') '
        
        ## add `reply to` tag
        replyTo = u''
        if u'reply_to_message' in msg:
            reply_sender = msg[u'reply_to_message'][u'from'][u'first_name']
            if u'last_name' in msg[u'reply_to_message'][u'from']:
                reply_sender += " " +  msg[u'reply_to_message'][u'from'][u'last_name']
            replyTo =  u' (reply to ' + reply_sender + u') '
            if msg[u'reply_to_message'][u'from'][u'id'] == tg_bot_id:
                replyTo =  u' (reply to ' + msg[u'reply_to_message'][u'text'].split(":")[0]  + u') '

        ## replace emoji to CQ:emoji
        for i in range(8986, 12287):
            text, _ = re.subn(chr(i), "[CQ:emoji,id=" + str(i) + "]", text)
        for i in range(126980, 129472):
            text, _ = re.subn(chr(i), "[CQ:emoji,id=" + str(i) + "]", text)
        
        ## blank message add placeholder
        if len(text) == 0:
            text = '[不支持的消息类型]'
        
        ## check drive mode
        if drive_modes[forward_index] == 1:
            return
        
        ## send message to QQ group
        qq_bot.send(SendGroupMessage(
            group = qq_group_id,
            text = sender + replyTo + forwardFrom + ': ' + text
        ))

# QQ group message receive
Message = namedtuple('Manifest', ('qq', 'time', 'text'))
messages = []

@qq_bot.listener((RcvdGroupMessage, ))
def new(message):
    global tg_bot
    global qq_bot
    global forward_ids
    global sticker_link_modes
    global drive_modes
    global server_pic_url
    
    ## log message
    logging.info('(' + message.qq + '): ' + message.text)

    ## add to message queue
    messages.append(Message(message.qq, int(time.time()), message.text))
    
    ## get Telegram group to forward message
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index= get_forward_info(qq_group_id, 0)
    
    ## get reflect of this QQ group member
    name_list = qq_name_lists[forward_index]

    ## get message text
    text = message.text

    ## clear CQ:image in text
    text, _ = re.subn("\\[CQ:image.*?\\]", "", text)
    
    ## replace special characters
    text, _ = re.subn("&amp;", "&", text)
    text, _ = re.subn("&#91;", "[", text)
    text, _ = re.subn("&#93;", "]", text)
    text, _ = re.subn("&#44;", ",", text)

    ## replace CQ:emoji to emoji
    for i in range(8986, 12287):
        text, _ = re.subn("\\[CQ:emoji,id=" + str(i) + "\\]", chr(i), text)
    for i in range(126980, 129472):
        text, _ = re.subn("\\[CQ:emoji,id=" + str(i) + "\\]", chr(i), text)
    
    ## qq face to emoji
    for i in qq_emoji_list:
        text = text.replace("[CQ:face,id=" + str(i) + "]", qq_emoji_list[i])

    ## handle send sticker instructions
    for j in special_sticker_list:
        if text == u'!' + j:
            tg_bot.sendSticker(tg_group_id, special_sticker_list[j])
            return
    
    ## replace CQ:at
    for k, v in name_list.items():
        text = text.replace("[CQ:at,qq=" + k + "]", "@" + v + " ")
    
    ## replace CQ:share/CQ:music
    newtext = u''
    if text.startswith(u'[CQ:share') or text.startswith(u'[CQ:music'):
        parts = text.split(',')
        for part in parts:
            if part.startswith(u'title='):
                newtext = newtext + part.split('=')[1]
                break
        for part in parts:
            if part.startswith(u'url='):
                newtext = newtext + u'\n' + part.split('=')[1]
                break
        text = newtext

    ## handle special instructions
    if text == u'[sticker link on]':
        set_sticker_link_mode(forward_index, 1)
        return
    elif text == u'[sticker link off]':
        set_sticker_link_mode(forward_index, 0)
        return
    elif text == u'[drive mode on]':
        set_drive_mode(forward_index, 1)
        return
    elif text == u'[drive mode off]':
        set_drive_mode(forward_index, 0)
        return

    ## replace QQ number to group member name, get full message text
    if str(message.qq) in name_list:
        full_msg = name_list[str(message.qq)] + ': ' + text.strip()
    else:
        full_msg = str(message.qq) + ': ' + text.strip()

    ## send pictures to Telegram group
    image_num = 0
    for match in CQImage.PATTERN.finditer(message.text):
        image_num = image_num + 1
        filename = match.group(1)
        url = qq_get_pic_url(filename)

        ### gif pictures send as document
        if filename.lower().endswith('gif'):
            try:
                ### the first image in message attach full message text
                if image_num == 1:
                    tg_bot.sendDocument(tg_group_id, url, caption=full_msg)
                else:
                    tg_bot.sendDocument(tg_group_id, url)
            except:
                ### when error occurs, download picture and send link instead
                error(message)
                traceback.print_exc()
                qq_download_pic(filename)
                my_url = get_short_url(server_pic_url + filename)
                tg_bot.sendMessage(tg_group_id, my_url + "\n" + full_msg)

        ### jpg/png pictures send as photo
        else:
            try:
                ### the first image in message attach full message text
                if image_num == 1:
                    tg_bot.sendPhoto(tg_group_id, url, caption=full_msg)
                else:
                    tg_bot.sendPhoto(tg_group_id, url)
            except:
                ### when error occurs, download picture and send link instead
                error(message)
                traceback.print_exc()
                qq_download_pic(filename)
                my_url = get_short_url(server_pic_url + filename)
                tg_bot.sendMessage(tg_group_id, my_url + "\n" + full_msg)   

    ## send plain text message with bold group member name 
    if image_num == 0:
        if str(message.qq) in name_list:
            full_msg_bold = '*' + name_list[str(message.qq)] + '*: ' + text.strip()
        else:
            full_msg_bold = '*' + str(message.qq) + '*: ' + text.strip()
        tg_bot.sendMessage(tg_group_id, full_msg_bold, parse_mode="Markdown")

# toolkits
def get_forward_info(qq_group_id=0, tg_group_id=0):
    ## get forward information tuple by QQ group id or Telegram group id 
    forward_index = -1;
    for index in range(len(forward_ids)):
        qid, tid = forward_ids[index]
        if tg_group_id < 0 and tid == tg_group_id:
            qq_group_id = qid
            forward_index = index
            break
        elif qq_group_id > 0 and qid == qq_group_id:
            tg_group_id = tid
            forward_index = index
            break
    return (qq_group_id, tg_group_id, forward_index)

def set_sticker_link_mode(forward_index, status, tg_group_id, qq_group_id):
    ## set sticker link mode on/off
    global tg_bot
    global qq_bot
    global sticker_link_modes
    if status == 1:
        msg = 'Telegram Sticker图片链接已启用'
    elif status == 0:
        msg = 'Telegram Sticker图片链接已禁用'
    sticker_link_modes[forward_index] = status
    tg_bot.sendMessage(tg_group_id, msg)
    qq_bot.send(SendGroupMessage(group = qq_group_id, text = msg))

def set_drive_mode(forward_index, status, tg_group_id, qq_group_id):
    ## set drive mode on/off
    global tg_bot
    global qq_bot
    global drive_modes
    if status == 1:
        msg = 'Telegram向QQ转发消息已暂停'
    elif status == 0:
        msg = 'Telegram向QQ转发消息已重启'
    drive_modes[forward_index] = status
    tg_bot.sendMessage(tg_group_id, msg);
    qq_bot.send(SendGroupMessage(group = qq_group_id, text = msg))

def keep_main_thread():
    ## keep main thread running
    while True:
        time.sleep(10)

# main
if __name__ == '__main__':
    try:
        qq_bot.start()
        MessageLoop(tg_bot, tg_msg_receive).run_as_thread()
        print("Starting...")
        keep_main_thread()
    except KeyboardInterrupt:
        print("Stopping...")
