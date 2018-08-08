import json
import logging
import os
import traceback
from typing import Union

from telegram.ext import DispatcherHandlerStop
import ffmpy
import global_vars
import requests
import telegram
from PIL import Image
from bot_constant import FORWARD_LIST, BAIDU_API, USE_SHORT_URL
from main.command import command_listener
from telegram.ext import MessageHandler, Filters

from main.utils import get_forward_index, CQ_IMAGE_ROOT, SERVER_PIC_URL, \
    get_plugin_priority, send_from_qq_to_tg, send_from_tg_to_qq, send_both_side

from main.tg_utils import tg_get_file, get_url

logger = logging.getLogger("CTB." + __name__)
logger.debug(__name__ + " loading")

"""
CQ_IMAGE_ROOT SERVER_PIC_URL required
"""

# endregion

IMAGE_LINK_MODE = list()  # pic_link_mode per group

for forward in FORWARD_LIST:  # initialize
    IMAGE_LINK_MODE.append(forward['IMAGE_LINK'])


def photo_from_telegram(bot: telegram.Bot,
                        update: telegram.Update):
    """
    handle photos sent from telegram
    :param bot:
    :param update:
    :return:
    """

    message: telegram.Message = update.effective_message
    edited = (bool(getattr(update, "edited_message", None)) or bool(getattr(update, "edited_channel_post", None)))

    tg_group_id = message.chat_id  # telegram group id
    forward_index = get_forward_index(tg_group_id=tg_group_id)

    reply_entity = list()

    photo = message.photo[-1]
    file_id = photo.file_id
    if global_vars.JQ_MODE:
        filename = tg_get_file(file_id)
        reply_entity.append({
            'type': 'image',
            'data': {'file': filename}
        })
        if message.caption:
            reply_entity.append({
                'type': 'text',
                'data': {'text': message.caption}
            })
    elif IMAGE_LINK_MODE[forward_index]:
        filename = tg_get_file(file_id)
        pic_url = get_url(filename)
        if message.caption:
            reply_entity.append({
                'type': 'text',
                'data': {'text': '[ 图片, 请点击查看' + pic_url + ' ]' + message.caption}
            })
        else:
            reply_entity.append({
                'type': 'text',
                'data': {'text': '[ 图片, 请点击查看' + pic_url + ' ]'}
            })
    else:
        reply_entity.append({
            'type': 'text',
            'data': {'text': '[ 图片 ]' + message.caption}
        })
    qq_message_id = send_from_tg_to_qq(forward_index,
                                       message=reply_entity,
                                       tg_group_id=tg_group_id,
                                       tg_user=update.effective_user,
                                       tg_forward_from=message,
                                       tg_reply_to=message.reply_to_message,
                                       edited=edited)
    global_vars.mdb.append_message(qq_message_id, message.message_id, forward_index, 0)


def video_from_telegram(bot: telegram.Bot,
                        update: telegram.Update):
    """
    if update.message:
        message: telegram.Message = update.message
        edited = False
    else:
        message: telegram.Message = update.edited_message
        edited = True
    """

    message: telegram.Message = update.effective_message
    edited = (bool(getattr(update, "edited_message", None)) or bool(getattr(update, "edited_channel_post", None)))

    tg_group_id = message.chat_id  # telegram group id
    forward_index = get_forward_index(tg_group_id=tg_group_id)

    reply_entity = list()

    reply_entity.append({
        'type': 'text',
        'data': {'text': '[ 视频 ]'}
    })
    if message.caption:
        reply_entity.append({
            'type': 'text',
            'data': {'text': message.caption}
        })

    qq_message_id = send_from_tg_to_qq(forward_index,
                                       message=reply_entity,
                                       tg_group_id=tg_group_id,
                                       tg_user=update.effective_user,
                                       tg_forward_from=message,
                                       tg_reply_to=message.reply_to_message,
                                       edited=edited)
    global_vars.mdb.append_message(qq_message_id, message.message_id, forward_index, 0)


def audio_from_telegram(bot: telegram.Bot,
                        update: telegram.Update):
    message: telegram.Message = update.effective_message

    tg_group_id = message.chat_id  # telegram group id
    forward_index = get_forward_index(tg_group_id=tg_group_id)

    reply_entity = list()

    reply_entity.append({
        'type': 'text',
        'data': {'text': '[ 音频 ]'}
    })
    qq_message_id = send_from_tg_to_qq(forward_index,
                                       message=reply_entity,
                                       tg_group_id=tg_group_id,
                                       tg_user=update.effective_user,
                                       tg_forward_from=message,
                                       tg_reply_to=message.reply_to_message)
    global_vars.mdb.append_message(qq_message_id, message.message_id, forward_index, 0)


def document_from_telegram(bot: telegram.Bot,
                           update: telegram.Update):
    """
    if update.message:
        message: telegram.Message = update.message
        edited = False
    else:
        message: telegram.Message = update.edited_message
        edited = True
    """

    message: telegram.Message = update.effective_message
    edited = (bool(getattr(update, "edited_message", None)) or bool(getattr(update, "edited_channel_post", None)))

    tg_group_id = message.chat_id  # telegram group id
    forward_index = get_forward_index(tg_group_id=tg_group_id)

    reply_entity = list()

    file_id = message.document.file_id
    if message.document.mime_type == 'video/mp4':
        file_id = message.document.file_id
        if global_vars.JQ_MODE:
            filename = tg_get_file(file_id, mp4=True)
            if os.path.getsize(os.path.join(CQ_IMAGE_ROOT, filename)) > 5242880:
                reply_entity.append({
                    'type': 'text',
                    'data': {'text': '[ 视频：大小超过 5 MB ]'}
                })
            else:
                reply_entity.append({
                    'type': 'image',
                    'data': {'file': filename}
                })
            if message.caption:
                reply_entity.append({
                    'type': 'text',
                    'data': {'text': message.caption}
                })
        elif IMAGE_LINK_MODE[forward_index]:
            filename = tg_get_file(file_id, mp4=True)
            pic_url = get_url(filename)
            if message.caption:
                reply_entity.append({
                    'type': 'text',
                    'data': {'text': '[ 视频, 请点击查看' + pic_url + ' ]' + message.caption}
                })
            else:
                reply_entity.append({
                    'type': 'text',
                    'data': {'text': '[ 视频, 请点击查看' + pic_url + ' ]'}
                })
        else:
            reply_entity.append({
                'type': 'text',
                'data': {'text': '[ 视频 ]'}
            })
    elif message.document.mime_type == 'image/gif':
        if global_vars.JQ_MODE:
            filename = tg_get_file(file_id)
            reply_entity.append({
                'type': 'image',
                'data': {'file': filename}
            })
            if message.caption:
                reply_entity.append({
                    'type': 'text',
                    'data': {'text': message.caption}
                })
        elif IMAGE_LINK_MODE[forward_index]:
            filename = tg_get_file(file_id)
            pic_url = get_url(filename)
            if message.caption:
                reply_entity.append({
                    'type': 'text',
                    'data': {'text': '[ GIF, 请点击查看' + pic_url + ' ]' + message.caption}
                })
            else:
                reply_entity.append({
                    'type': 'text',
                    'data': {'text': '[ GIF, 请点击查看' + pic_url + ' ]'}
                })
        else:
            reply_entity.append({
                'type': 'text',
                'data': {'text': '[ GIF ]'}
            })
    else:
        reply_entity.append({
            'type': 'text',
            'data': {'text': '[ 文件 ]'}
        })
    qq_message_id = send_from_tg_to_qq(forward_index,
                                       message=reply_entity,
                                       tg_group_id=tg_group_id,
                                       tg_user=update.effective_user,
                                       tg_forward_from=message,
                                       tg_reply_to=message.reply_to_message,
                                       edited=edited)
    global_vars.mdb.append_message(qq_message_id, message.message_id, forward_index, 0)


def sticker_from_telegram(bot: telegram.Bot, update: telegram.Update):
    message: telegram.Message = update.effective_message

    tg_group_id = message.chat_id  # telegram group id
    forward_index = get_forward_index(tg_group_id=tg_group_id)

    reply_entity = list()

    file_id = message.sticker.file_id
    if global_vars.JQ_MODE:
        filename = tg_get_file(file_id)
        reply_entity.append({
            'type': 'image',
            'data': {'file': filename}
        })
    elif IMAGE_LINK_MODE[forward_index]:
        filename = tg_get_file(file_id)
        pic_url = get_url(filename)
        reply_entity.append({
            'type': 'text',
            'data': {'text': '[ ' + message.sticker.emoji + ' sticker, 请点击查看' + pic_url + ' ]'}
        })
    else:
        reply_entity.append({
            'type': 'text',
            'data': {'text': '[ ' + message.sticker.emoji + ' sticker ]'}
        })
    qq_message_id = send_from_tg_to_qq(forward_index,
                                       message=reply_entity,
                                       tg_group_id=tg_group_id,
                                       tg_user=update.effective_user,
                                       tg_forward_from=message,
                                       tg_reply_to=message.reply_to_message)
    global_vars.mdb.append_message(qq_message_id, message.message_id, forward_index, 0)


def get_location_from_baidu(latitude: Union[float, str],
                            longitude: Union[float, str]):
    params = (
        ('callback', 'renderReverse'),
        ('location', str(latitude) + ',' + str(longitude)),
        ('output', 'json'),
        ('pois', '1'),
        ('ak', BAIDU_API),
    )

    result = requests.get('http://api.map.baidu.com/geocoder/v2/',
                          params=params)
    result = result.text.replace('renderReverse&&renderReverse(', '')[:-1]

    result_json = json.loads(result)
    if result_json['status'] == 0:
        return result_json['result']['formatted_address']
    else:
        return 'Baidu API returned an error code: ' + str(result_json['status'])


def location_from_telegram(bot: telegram.Bot,
                           update: telegram.Update):
    message: telegram.Message = update.effective_message

    tg_group_id = message.chat_id  # telegram group id
    forward_index = get_forward_index(tg_group_id=tg_group_id)

    latitude = message.location.latitude
    longitude = message.location.longitude
    reply_entity = list()

    reply_entity.append({
        'type': 'text',
        'data': {'text': '分享了一个位置：' + get_location_from_baidu(latitude, longitude)}
    })
    qq_message_id = send_from_tg_to_qq(forward_index,
                                       message=reply_entity,
                                       tg_group_id=tg_group_id,
                                       tg_user=update.effective_user,
                                       tg_forward_from=message,
                                       tg_reply_to=message.reply_to_message)
    global_vars.mdb.append_message(qq_message_id, message.message_id, forward_index, 0)


def text_from_telegram(bot: telegram.Bot,
                       update: telegram.Update):
    """
    if update.message:
        message: telegram.Message = update.message
        edited = False
    else:
        message: telegram.Message = update.edited_message
        edited = True
    """

    message: telegram.Message = update.effective_message
    edited = (bool(getattr(update, "edited_message", None)) or bool(getattr(update, "edited_channel_post", None)))

    tg_group_id = message.chat_id  # telegram group id
    forward_index = get_forward_index(tg_group_id=tg_group_id)

    if forward_index == -1:
        return ''

    reply_entity = list()

    reply_entity.append({
        'type': 'text',
        'data': {'text': message.text}
    })
    qq_message_id = send_from_tg_to_qq(forward_index,
                                       message=reply_entity,
                                       tg_group_id=tg_group_id,
                                       tg_user=update.effective_user,
                                       tg_forward_from=message,
                                       tg_reply_to=message.reply_to_message,
                                       edited=edited)
    global_vars.mdb.append_message(qq_message_id, message.message_id, forward_index, 0)


global_vars.dp.add_handler(MessageHandler((Filters.text | Filters.command),
                                          text_from_telegram,
                                          edited_updates=True),
                           get_plugin_priority(__name__))
global_vars.dp.add_handler(MessageHandler(Filters.sticker,
                                          sticker_from_telegram),
                           get_plugin_priority(__name__))
global_vars.dp.add_handler(MessageHandler(Filters.audio,
                                          audio_from_telegram),
                           get_plugin_priority(__name__))
global_vars.dp.add_handler(MessageHandler(Filters.photo,
                                          photo_from_telegram,
                                          edited_updates=True),
                           get_plugin_priority(__name__))
global_vars.dp.add_handler(MessageHandler(Filters.document,
                                          document_from_telegram,
                                          edited_updates=True),
                           get_plugin_priority(__name__))
global_vars.dp.add_handler(MessageHandler(Filters.video,
                                          video_from_telegram),
                           get_plugin_priority(__name__))
global_vars.dp.add_handler(MessageHandler(Filters.location,
                                          location_from_telegram),
                           get_plugin_priority(__name__))


@global_vars.qq_bot.on_message('group', 'discuss', group=get_plugin_priority(__name__))
def handle_forward(context):
    qq_group_id = context.get('group_id')
    qq_discuss_id = context.get('discuss_id')

    forward_index = get_forward_index(qq_group_id=qq_group_id,
                                      qq_discuss_id=qq_discuss_id)
    if forward_index == -1:
        return ''

    tg_message_id_list = send_from_qq_to_tg(forward_index, message=context['message'],
                                            qq_group_id=qq_group_id,
                                            qq_discuss_id=qq_discuss_id,
                                            qq_user=context['user_id'])

    # save message to database, using telegram message id as index
    for msg_id in tg_message_id_list:
        global_vars.mdb.append_message(context.get('message_id'), msg_id, forward_index, context.get('user_id'))

    return ''


@command_listener('image link on', 'lnkon', description='enable pic link mode, only available for Air users')
def pic_link_on(forward_index: int,
                tg_group_id: int = None,
                tg_user: telegram.User = None,
                tg_message_id: int = None,
                tg_reply_to: telegram.Message = None,
                qq_group_id: int = None,
                qq_discuss_id: int = None,
                qq_user: int = None):
    if global_vars.JQ_MODE:
        return
    IMAGE_LINK_MODE[forward_index] = True
    message = 'QQ 图片链接模式已启动'

    return send_both_side(forward_index,
                          message,
                          qq_group_id,
                          qq_discuss_id,
                          tg_group_id,
                          tg_message_id)


@command_listener('image link off', 'lnkoff', description='disable pic link mode, only available for Air users')
def pic_link_off(forward_index: int,
                 tg_group_id: int = None,
                 tg_user: telegram.User = None,
                 tg_message_id: int = None,
                 tg_reply_to: telegram.Message = None,
                 qq_group_id: int = None,
                 qq_discuss_id: int = None,
                 qq_user: int = None):
    if global_vars.JQ_MODE:
        return
    IMAGE_LINK_MODE[forward_index] = False
    message = 'QQ 图片链接模式已关闭'

    return send_both_side(forward_index,
                          message,
                          qq_group_id,
                          qq_discuss_id,
                          tg_group_id,
                          tg_message_id)
