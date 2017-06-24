#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import threading
import time
import traceback
from collections import namedtuple
from configparser import ConfigParser
from urllib.request import urlretrieve
import re
# from apscheduler.schedulers.background import BackgroundScheduler

from cqsdk import CQBot, CQAt, CQImage, RcvdPrivateMessage, RcvdGroupMessage, \
    RE_CQ_SPECIAL, \
    RcvdDiscussMessage, \
    SendPrivateMessage, SendGroupMessage, SendDiscussMessage, \
    GroupMemberDecrease, GroupMemberIncrease

from utils import CQ_IMAGE_ROOT, error, reply

from bot_constant import *
from qq_emoji_list import *
from special_sticker_list import *

# Logging Part
import logging
logging.basicConfig(
    filename = 'bot.log',
    level = logging.DEBUG
)

def debug(message):
    logging.debug('------coolq message------')
    logging.debug('from group: ' + message.group)
    logging.debug('from qq: ' + message.qq)
    logging.debug('from text: ' + message.text)
    logging.debug('-------------------------')

# generate short url
import requests
import json
def get_short_url(long_url):
    try:
        r = requests.get('http://api.t.sina.com.cn/short_url/shorten.json?source=3271760578&url_long=' + long_url)
        obj = json.loads(r.text)
        short_url = obj[0]['url_short']
        return short_url
    except:
        traceback.print_exc()
        return long_url


# Telegram Bot Part
import telepot
from pprint import pprint
from PIL import Image

tgBot = telepot.Bot(tgToken)
stickerLinkMode = 0

def create_jpg_image(path, name):
    im = Image.open(os.path.join(path, name)).convert("RGB")
    im.save(os.path.join(path, name + ".jpg"), "JPEG")

def create_png_image(path, name):
    im = Image.open(os.path.join(path, name)).convert("RGBA")
    im.save(os.path.join(path, name + ".png"), "PNG")

def handle(msg):
    global tgBot
    global qqbot
    global tgBotId
    global tgGroupId
    global qqGroupId
    global stickerLinkMode
    global server_pic_url
    logging.debug(msg)
    pprint(msg)
    chatId = msg[u'chat'][u'id']
    chatType = msg[u'chat'][u'type']
    if chatType != u'group':
        return
    sender = msg[u'from'][u'first_name']
    if u'last_name' in msg[u'from']:
        sender += " " +  msg[u'from'][u'last_name']
    text = u''
    if u'text' in msg:
        text = msg[u'text']
    elif u'photo' in msg:
        fileId = msg[u'photo'][-1][u'file_id']
        filePath = tgBot.getFile(fileId)
        urlretrieve('https://api.telegram.org/file/bot' + tgToken + "/" + filePath[u'file_path'], os.path.join(CQ_IMAGE_ROOT, fileId))
        create_jpg_image(CQ_IMAGE_ROOT, fileId)
        pic_url = get_short_url(server_pic_url + fileId + '.jpg')
        text = u'[图片, 请点击查看' + pic_url + u']'
    elif u'video' in msg:
        text = u'[视频]'
    elif u'audio' in msg:
        text = u'[音频]'
    elif u'document' in msg:
        text = u'[文件]'
    elif u'sticker' in msg:
        text = u'[' + msg[u'sticker'][u'emoji'] + u' sticker]'
        fileId = msg[u'sticker'][u'file_id']
        if stickerLinkMode == 1:
            filePath = tgBot.getFile(fileId)
            urlretrieve('https://api.telegram.org/file/bot' + tgToken + "/" + filePath[u'file_path'], os.path.join(CQ_IMAGE_ROOT, fileId))
            create_png_image(CQ_IMAGE_ROOT, fileId)
            pic_url = get_short_url(server_pic_url + fileId + '.png')
            text = u'[' + msg[u'sticker'][u'emoji'] + ' sticker, 请点击查看' + pic_url + u']'
    if text == u'[showgroupid]':
        tgBot.sendMessage(chatId, 'Telegram连接已建立，chatId = ' + str(chatId));
    elif text == u'[sticker link on]':
        stickerLinkMode = 1
        tgBot.sendMessage(chatId, 'Telegram Sticker图片链接已启用');
        qqbot.send(SendGroupMessage(
            group = qqGroupId,
            text = 'Telegram Sticker图片链接已启用'
        ))
    elif text == u'[sticker link off]':
        stickerLinkMode = 0
        tgBot.sendMessage(chatId, 'Telegram Sticker图片链接已禁用');
        qqbot.send(SendGroupMessage(
            group = qqGroupId,
            text = 'Telegram Sticker图片链接已禁用'
        ))
    else:
        forwardFrom = u''
        if u'forward_from' in msg:
            forward_sender = msg[u'forward_from'][u'first_name']
            if u'last_name' in msg[u'forward_from']:
                forward_sender += " " +  msg[u'forward_from'][u'last_name']
            forwardFrom = u' (forwarded from ' + forward_sender + u') '
        replyTo = u''
        if u'reply_to_message' in msg:
            reply_sender = msg[u'reply_to_message'][u'from'][u'first_name']
            if u'last_name' in msg[u'reply_to_message'][u'from']:
                reply_sender += " " +  msg[u'reply_to_message'][u'from'][u'last_name']
            replyTo =  u' (reply to ' + reply_sender + u') '
            if msg[u'reply_to_message'][u'from'][u'id'] == tgBotId:
                replyTo =  u' (reply to ' + msg[u'reply_to_message'][u'text'].split(":")[0]  + u') '

        # replace emoji
        for i in range(8986, 12953):
            text, _ = re.subn(chr(i), "[CQ:emoji,id=" + str(i) + "]", text)
        for i in range(126980, 129472):
            text, _ = re.subn(chr(i), "[CQ:emoji,id=" + str(i) + "]", text)
        
        qqbot.send(SendGroupMessage(
            group = qqGroupId,
            text = sender + replyTo + forwardFrom + ': ' + text
        ))


# Coolq Bot Part
qqbot = CQBot(11235)
POI_GROUP = '545452952'

with open('admin.json', 'r', encoding="utf-8") as f:
    data = json.loads(f.read())
    ADMIN = data

with open('namelist.json', 'r', encoding="utf-8") as f:
    data = json.loads(f.read())
    NAMELIST = data

Message = namedtuple('Manifest', ('qq', 'time', 'text'))
messages = []

def debug(message):
    logging.debug('------coolq message------')
    logging.debug('from group: ' + message.group)
    logging.debug('from qq: ' + message.qq)
    logging.debug('from text: ' + message.text)
    logging.debug('-------------------------')


@qqbot.listener((RcvdGroupMessage, ))
def blacklist(message):
    return message.group != POI_GROUP


@qqbot.listener((RcvdGroupMessage, RcvdPrivateMessage))
def command(message):
    # Restrict to admin
    if message.qq not in ADMIN:
        return
    # Parse message
    try:
        texts = message.text.split()
        cmd = texts[0]
        qq = texts[1]
        idx = texts[2:]
    except:
        return
    if cmd != '/awd':
        return

    match = CQAt.PATTERN.fullmatch(qq)
    if match and match.group(1):
        qq = match.group(1)
    try:
        idx = list(map(lambda x: int(x), idx))
    except:
        idx = []
    if len(idx) == 0:
        idx = [0]

    items = list(filter(lambda x: x.qq == qq, messages))
    items.reverse()
    for i in idx:
        try:
            item = items[i]
        except:
            continue
        reply(qqbot, message, "[awd] {qq} #{i}\n{text}".format(
                i=i, qq=CQAt(item.qq), text=item.text))


@qqbot.listener((RcvdGroupMessage, ))
def new(message):
    global tgBot
    global tgGroupId
    global qqGroupId
    global stickerLinkMode
    global server_pic_url
    debug(message)
    messages.append(Message(message.qq, int(time.time()), message.text))

    text = message.text
    text, _ = re.subn("\\[CQ:image.*?\\]", "", text)
    
    # replace special characters
    text, _ = re.subn("&amp;", "&", text)
    text, _ = re.subn("&#91;", "[", text)
    text, _ = re.subn("&#93;", "]", text)
    text, _ = re.subn("&#44;", ",", text)

    # replace emoji
    for i in range(8986, 12953):
        text, _ = re.subn("\\[CQ:emoji,id=" + str(i) + "\\]", chr(i), text)
    for i in range(126980, 129472):
        text, _ = re.subn("\\[CQ:emoji,id=" + str(i) + "\\]", chr(i), text)
    
    # qq face to emoji
    for i in qqEmojiList:
        text = text.replace("[CQ:face,id=" + str(i) + "]", qqEmojiList[i])
    for j in specialStickerList:
        if text == u'!' + j:
            tgBot.sendSticker(tgGroupId, specialStickerList[j])
            return
    
    # replace CQ:at
    for k, v in NAMELIST.items():
        text = text.replace("[CQ:at,qq=" + k + "]", "@" + v + " ")

    if text == u'[sticker link on]':
        stickerLinkMode = 1
        tgBot.sendMessage(tgGroupId, 'Telegram Sticker图片链接已启用');
        qqbot.send(SendGroupMessage(
            group = qqGroupId,
            text = 'Telegram Sticker图片链接已启用'
        ))
    elif text == u'[sticker link off]':
        stickerLinkMode = 0
        tgBot.sendMessage(tgGroupId, 'Telegram Sticker图片链接已禁用');
        qqbot.send(SendGroupMessage(
            group = qqGroupId,
            text = 'Telegram Sticker图片链接已禁用'
        ))

    if str(message.qq) in NAMELIST:
        fullMsg = NAMELIST[str(message.qq)] + ': ' + text.strip()
    else:
        fullMsg = str(message.qq) + ': ' + text.strip()

    imageNum = 0
    for match in CQImage.PATTERN.finditer(message.text):
        imageNum = imageNum + 1
        filename = match.group(1)
        # ImageDownloader(filename).start()
        url = getImageUrl(filename)
        if filename.lower().endswith('gif'):
            try:
                if imageNum == 1:
                    tgBot.sendDocument(tgGroupId, url, caption=fullMsg)
                else:
                    tgBot.sendDocument(tgGroupId, url)
            except:
                error(message)
                traceback.print_exc()
                ImageDownloader(filename).run()
                my_url = get_short_url(server_pic_url + filename)
                tgBot.sendMessage(tgGroupId, my_url + "\n" + fullMsg)

        else:
            try:
                if imageNum == 1:
                    tgBot.sendPhoto(tgGroupId, url, caption=fullMsg)
                else:
                    tgBot.sendPhoto(tgGroupId, url)
            except:
                error(message)
                traceback.print_exc()
                ImageDownloader(filename).run()
                my_url = get_short_url(server_pic_url + filename)
                tgBot.sendMessage(tgGroupId, my_url + "\n" + fullMsg)   

    if imageNum == 0:
        tgBot.sendMessage(tgGroupId, fullMsg)

def getImageUrl(filename):
    cqimg = os.path.join(CQ_IMAGE_ROOT, filename+'.cqimg')
    parser = ConfigParser()
    parser.read(cqimg)
    url = parser['image']['url']
    return url

class ImageDownloader(threading.Thread):
    def __init__(self, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename

    def run(self):
        try:
            path = os.path.join(CQ_IMAGE_ROOT, self.filename)
            if os.path.exists(path):
                return

            cqimg = os.path.join(CQ_IMAGE_ROOT, self.filename+'.cqimg')
            parser = ConfigParser()
            parser.read(cqimg)

            url = parser['image']['url']
            urlretrieve(url, path)
        except:
            error(self.filename)
            traceback.print_exc()


if __name__ == '__main__':
    try:
        qqbot.start()
        tgBot.message_loop(handle);
        # scheduler.start()
        print("Running...")
        # Keep the program running.
        while 1:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping...")
