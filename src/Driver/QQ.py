from typing import Dict, List
import threading
import asyncio
import janus
from aiocqhttp import CQHttp, MessageSegment
from Core.UMRType import UnifiedMessage, MessageEntity
from Core import UMRDriver
from Core import UMRLogging
from Util.Helper import check_attribute
from Core import UMRConfig
import re
from Core.UMRFileDL import get_image
import os

NAME = 'QQ'

logger = UMRLogging.getLogger('UMRDriver.QQ')

loop: asyncio.AbstractEventLoop
queue: janus.Queue

config: Dict = UMRConfig.config['Driver']['QQ']

attributes = [
    'Account',
    'APIRoot',
    'ListenIP',
    'ListenPort',
    'Token',
    'Secret',
    'IsPro',
    'ChatList',
]
check_attribute(config, attributes, logger)
bot = CQHttp(api_root=config.get('APIRoot'),
             access_token=config.get('Token'),
             secret=config.get('Secret'))

##### initializations #####

# get group list
group_list: Dict[int, Dict[int, Dict]] = dict()  # Dict[group_id, Dict[member_id, member_info]]
# see https://cqhttp.cc/docs/4.13/#/API?id=响应数据23

group_type: Dict[int, str] = config.get('ChatList')
is_coolq_pro = config.get('IsPro', False)
stranger_list: Dict[int, str] = dict()


##### Define send and receive #####

@bot.on_message()
# 上面这句等价于 @bot.on('message')
async def handle_msg(context):
    group_id = context.get('group_id')
    if group_type.get(group_id) != context.get('message_type'):  # filter unknown group chat
        logger.debug(f'ignored unknown source: {context.get("message_type")}: {group_id}')
        return {}

    unified_message_list = await dissemble_message(context)
    for message in unified_message_list:
        await UMRDriver.receive(message)
    return {}  # 返回给 HTTP API 插件，走快速回复途径


async def send(to_chat: int, messsage: UnifiedMessage):
    """
    decorator for send new message
    :return:
    """
    logger.debug('sending message')
    asyncio.run_coroutine_threadsafe(_send(to_chat, messsage), loop)


async def _send(to_chat: int, message: UnifiedMessage):
    """
    decorator for send new message
    :return:
    """
    context = dict()
    _group_type = group_type.get(to_chat)
    if not _group_type:
        logger.warning(f'Sending to undefined group or chat {to_chat}')
        return
    context['message_type'] = _group_type
    context['message'] = list()
    if message.image:
        image_name = os.path.basename(message.image)
        context['message'].append(MessageSegment.image(image_name))
    if message.forward_attrs.from_user:
        context['message'].append(MessageSegment.text(message.forward_attrs.from_user + ': '))
    for m in message.message:
        context['message'].append(MessageSegment.text(m.text + ' '))
        if m.link:
            context['message'].append(MessageSegment.text(m.link) + ' ')
    context[f'{_group_type}_id'] = to_chat
    logger.debug('finished processing message, ready to send')
    await bot.send(context, context['message'])


UMRDriver.api_register('QQ', 'send', send)


##### Utilities #####

async def get_username(user_id, chat_id, chat_type):
    if user_id == config['Account']:
        return 'bot'
    if chat_type == 'group':
        user = group_list.get(chat_id, dict()).get(user_id, dict())
        username = user.get('nickname', str(user_id))
    else:
        if user_id in stranger_list:
            username = stranger_list.get(user_id)
        else:
            user = await bot.get_stranger_info(user_id=user_id)
            username = user.get('nickname')
            stranger_list[user_id] = username
    return username


async def dissemble_message(context):
    # group_id = context.get('group_id')
    # user_id = context.get('user_id')
    # user = group_list.get(group_id, dict()).get(user_id, dict())
    # username = user.get('nickname', str(user_id))
    # for i in range(len(context['message'])):
    #     message = UnifiedMessage(from_platform='QQ', from_chat=group_id, from_user=username,
    #                              message=context.get('raw_message'))

    chat_id = context.get(f'{context.get("message_type")}_id')
    user_id = context.get('user_id')
    chat_type = context.get('message_type')
    username = await get_username(user_id, chat_id, chat_type)
    message: List[Dict] = context['message']

    unified_message = await parse_special_message(chat_id, username, message)
    if unified_message:
        return [unified_message]
    unified_message_list = await parse_message(chat_id, chat_type, username, message)
    return unified_message_list


async def parse_special_message(chat_id, username, message):
    if len(message) > 1:
        return None
    message = message[0]
    message_type = message['type']
    message = message['data']
    unified_message = UnifiedMessage(from_platform='QQ', from_chat=chat_id, from_user=username)
    if message_type == 'share':
        unified_message.message = [
            MessageEntity(text='Shared '),
            MessageEntity(text=message['title'], entity_type='link', link=message['url'])
        ]
    elif message_type == 'rich':
        if 'url' in message:
            url = message['url']
            if url.startswith('mqqapi'):
                cq_location_regex = re.compile(r'^mqqapi:.*lat=(.*)&lon=(.*)&title=(.*)&loc=(.*)&.*$')
                locations = cq_location_regex.findall(message['url'])  # [('lat', 'lon', 'name', 'addr')]
                unified_message.message = [
                    MessageEntity(
                        text=f'Shared a location: {locations[2]}, {locations[3]}, {locations[0]}, {locations[1]}'),
                ]
            else:
                unified_message.message = [
                    MessageEntity(text='Shared '),
                    MessageEntity(text=message['text'], entity_type='link', link=message['url'])
                ]
        else:
            logger.debug(f'Got unseen rich text message: {str(message)}')
            unified_message.message = [
                MessageEntity(text=message['text']),
            ]
    elif message_type == 'dice':
        unified_message.message = [
            MessageEntity(text='Rolled '),
            MessageEntity(text=message['type'], entity_type='bold'),
        ]
    elif message_type == 'rps':
        unified_message.message = [
            MessageEntity(text='Played '),
            MessageEntity(text={'1': 'Rock',
                                '2': 'Scissors',
                                '3': 'Paper'}[message['type']]
                          , entity_type='bold')
        ]
    elif message_type == 'shake':
        unified_message.message = [
            MessageEntity(text='Sent you a shake')
        ]
    elif message_type == 'music':
        if message['type'].startswith('163'):
            unified_message.message = [
                MessageEntity(text='Shared a music: '),
                MessageEntity(text='Netease Music', entity_type='link',
                              link=f'https://music.163.com/song?id={message["id"]}')
            ]
        elif message['type'].startswith('qq'):
            unified_message.message = [
                MessageEntity(text='Shared a music: '),
                MessageEntity(text='QQ Music', entity_type='link',
                              link=f'https://y.qq.com/n/yqq/song/{message["id"]}_num.html')
            ]
        else:
            logger.debug(f'Got unseen music share message: {str(message)}')
            unified_message.message = [
                MessageEntity(text='Shared a music: ' + str(message)),
            ]
    elif message_type == 'record':
        unified_message.message = [
            MessageEntity(text='Unsupported voice record, please view on QQ')
        ]
    elif message_type == 'bface':
        unified_message.message = [
            MessageEntity(text='Unsupported big face, please view on QQ')
        ]
    else:
        return

    return unified_message


qq_emoji_list = {  # created by JogleLew, optimizations are welcome
    0:   u'\U0001F62E',
    1:   u'\U0001F623',
    2:   u'\U0001F60D',
    3:   u'\U0001F633',
    4:   u'\U0001F60E',
    5:   u'\U0001F62D',
    6:   u'\U0000263A',
    7:   u'\U0001F637',
    8:   u'\U0001F634',
    9:   u'\U0001F62D',
    10:  u'\U0001F630',
    11:  u'\U0001F621',
    12:  u'\U0001F61D',
    13:  u'\U0001F603',
    14:  u'\U0001F642',
    15:  u'\U0001F641',
    16:  u'\U0001F913',
    18:  u'\U0001F624',
    19:  u'\U0001F628',
    20:  u'\U0001F60F',
    21:  u'\U0001F60A',
    22:  u'\U0001F644',
    23:  u'\U0001F615',
    24:  u'\U0001F924',
    25:  u'\U0001F62A',
    26:  u'\U0001F628',
    27:  u'\U0001F613',
    28:  u'\U0001F62C',
    29:  u'\U0001F911',
    30:  u'\U0001F44A',
    31:  u'\U0001F624',
    32:  u'\U0001F914',
    33:  u'\U0001F910',
    34:  u'\U0001F635',
    35:  u'\U0001F629',
    36:  u'\U0001F47F',
    37:  u'\U0001F480',
    38:  u'\U0001F915',
    39:  u'\U0001F44B',
    50:  u'\U0001F641',
    51:  u'\U0001F913',
    53:  u'\U0001F624',
    54:  u'\U0001F92E',
    55:  u'\U0001F628',
    56:  u'\U0001F613',
    57:  u'\U0001F62C',
    58:  u'\U0001F911',
    73:  u'\U0001F60F',
    74:  u'\U0001F60A',
    75:  u'\U0001F644',
    76:  u'\U0001F615',
    77:  u'\U0001F924',
    78:  u'\U0001F62A',
    79:  u'\U0001F44A',
    80:  u'\U0001F624',
    81:  u'\U0001F914',
    82:  u'\U0001F910',
    83:  u'\U0001F635',
    84:  u'\U0001F629',
    85:  u'\U0001F47F',
    86:  u'\U0001F480',
    87:  u'\U0001F915',
    88:  u'\U0001F44B',
    96:  u'\U0001F630',
    97:  u'\U0001F605',
    98:  u'\U0001F925',
    99:  u'\U0001F44F',
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
    1:  '[拜拜]',
    2:  '[鄙视]',
    3:  '[菜刀]',
    4:  '[沧桑]',
    5:  '[馋了]',
    6:  '[吃惊]',
    7:  '[微笑]',
    8:  '[得意]',
    9:  '[嘚瑟]',
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


async def parse_message(chat_id, chat_type, username, message):
    message_list = list()
    unified_message = UnifiedMessage(from_platform='QQ', from_chat=chat_id, from_user=username)
    for m in message:
        message_type = m['type']
        m = m['data']
        if message_type == 'image':
            # message not empty or contained a image, append to list
            if unified_message.message or unified_message.image:
                message_list.append(unified_message)
                unified_message = UnifiedMessage(from_platform='QQ', from_chat=chat_id, from_user=username)
            file_dir = await get_image(m['url'])
            if file_dir:
                unified_message.image = file_dir
            else:
                unified_message.message.append(MessageEntity(text='[Image not found]'))
                logger.warning(f'URL downlaod failed: {m["url"]}')

        elif message_type == 'text':
            unified_message.message.append(MessageEntity(text=m['text']))
        elif message_type == 'at':
            target = await get_username(m['qq'], chat_type, chat_type)
            unified_message.message.append(MessageEntity(text='@' + target, entity_type='bold'))
        elif message_type == 'sface':
            qq_face = int(m['id']) & 255
            if qq_face in qq_sface_list:
                unified_message.message.append(MessageEntity(text=qq_sface_list[qq_face]))
            else:
                unified_message.message.append(MessageEntity(text='\u2753'))  # ❓
        elif message_type == 'face':
            qq_face = int(m['id'])
            if qq_face in qq_emoji_list:
                unified_message.message.append(MessageEntity(text=qq_emoji_list[qq_face]))
            else:
                unified_message.message.append(MessageEntity(text='\u2753'))  # ❓
        else:
            logger.debug('Unhandled message type: ' + str(m))

    message_list.append(unified_message)
    return message_list


##### Janus queue for async loop #####
async def async_coro(async_q):
    """
    Asnyc queue for incoming async call
    :param async_q:
    :return:
    """
    while True:
        func, args, kwargs = await async_q.get()
        if asyncio.iscoroutinefunction(func):
            await func(*args, **kwargs)
        else:
            func(*args, **kwargs)
        async_q.task_done()


def do_nothing():
    pass


def run():
    global queue, loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    queue = janus.Queue(loop=loop)
    loop.create_task(async_coro(queue.async_q))
    bot.run(host=config.get('ListenIP'), port=config.get('ListenPort'), loop=loop, shutdown_trigger=do_nothing)


t = threading.Thread(target=run)
UMRDriver.threads.append(t)
t.start()
