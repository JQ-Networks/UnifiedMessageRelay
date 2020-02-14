from typing import Dict, List, Union
import threading
import asyncio
import json
from .aiocqhttp import CQHttp, MessageSegment
from Core.UMRType import UnifiedMessage, MessageEntity, ChatType, EntityType
from Core import UMRDriver
from Core import UMRLogging
from Core.UMRMessageRelation import set_ingress_message_id, set_egress_message_id
from Util.Helper import check_attribute, unparse_entities_to_markdown
from Core import UMRConfig
import re
import os

qq_emoji_list = {  # created by JogleLew and jqqqqqqqqqq, optimized based on Tim's emoji support
    0:   '😮',
    1:   '😣',
    2:   '😍',
    3:   '😳',
    4:   '😎',
    5:   '😭',
    6:   '☺️',
    7:   '😷',
    8:   '😴',
    9:   '😭',
    10:  '😰',
    11:  '😡',
    12:  '😝',
    13:  '😃',
    14:  '🙂',
    15:  '🙁',
    16:  '🤓',
    17:  '[Empty]',
    18:  '😤',
    19:  '😨',
    20:  '😏',
    21:  '😊',
    22:  '🙄',
    23:  '😕',
    24:  '🤤',
    25:  '😪',
    26:  '😨',
    27:  '😓',
    28:  '😬',
    29:  '🤑',
    30:  '✊',
    31:  '😤',
    32:  '🤔',
    33:  '🤐',
    34:  '😵',
    35:  '😩',
    36:  '💣',
    37:  '💀',
    38:  '🔨',
    39:  '👋',
    40:  '[Empty]',
    41:  '😮',
    42:  '💑',
    43:  '🕺',
    44:  '[Empty]',
    45:  '[Empty]',
    46:  '🐷',
    47:  '[Empty]',
    48:  '[Empty]',
    49:  '🤷',
    50:  '[Empty]',
    51:  '[Empty]',
    52:  '[Empty]',
    53:  '🎂',
    54:  '⚡',
    55:  '💣',
    56:  '🔪',
    57:  '⚽️',
    58:  '[Empty]',
    59:  '💩',
    60:  '☕️',
    61:  '🍚',
    62:  '[Empty]',
    63:  '🌹',
    64:  '🥀',
    65:  '[Empty]',
    66:  '❤️',
    67:  '💔️',
    68:  '[Empty]',
    69:  '🎁',
    70:  '[Empty]',
    71:  '[Empty]',
    72:  '[Empty]',
    73:  '[Empty]',
    74:  '🌞️',
    75:  '🌃',
    76:  '👍',
    77:  '👎',
    78:  '🤝',
    79:  '✌️',
    80:  '[Empty]',
    81:  '[Empty]',
    82:  '[Empty]',
    83:  '[Empty]',
    84:  '[Empty]',
    85:  '🥰',
    86:  '[怄火]',
    87:  '[Empty]',
    88:  '[Empty]',
    89:  '🍉',
    90:  '[Empty]',
    91:  '[Empty]',
    92:  '[Empty]',
    93:  '[Empty]',
    94:  '[Empty]',
    95:  '[Empty]',
    96:  '😅',
    97:  '[擦汗]',
    98:  '[抠鼻]',
    99:  '👏',
    100: '[糗大了]',
    101: '😏',
    102: '😏',
    103: '😏',
    104: '🥱',
    105: '[鄙视]',
    106: '😭',
    107: '😭',
    108: '[阴险]',
    109: '😚',
    110: '🙀',
    111: '[可怜]',
    112: '🔪',
    113: '🍺',
    114: '🏀',
    115: '🏓',
    116: '❤️',
    117: '🐞',
    118: '[抱拳]',
    119: '[勾引]',
    120: '✊',
    121: '[差劲]',
    122: '🤟',
    123: '🚫',
    124: '👌',
    125: '[转圈]',
    126: '[磕头]',
    127: '[回头]',
    128: '[跳绳]',
    129: '👋',
    130: '[激动]',
    131: '[街舞]',
    132: '😘',
    133: '[左太极]',
    134: '[右太极]',
    135: '[Empty]',
    136: '[双喜]',
    137: '🧨',
    138: '🏮',
    139: '💰',
    140: '[K歌]',
    141: '🛍️',
    142: '📧',
    143: '[帅]',
    144: '👏',
    145: '🙏',
    146: '[爆筋]',
    147: '🍭',
    148: '🍼',
    149: '[下面]',
    150: '🍌',
    151: '🛩',
    152: '🚗',
    153: '🚅',
    154: '[车厢]',
    155: '[高铁右车头]',
    156: '🌥',
    157: '下雨',
    158: '💵',
    159: '🐼',
    160: '💡',
    161: '[风车]',
    162: '⏰',
    163: '🌂',
    164: '[彩球]',
    165: '💍',
    166: '🛋',
    167: '[纸巾]',
    168: '💊',
    169: '🔫',
    170: '🐸',
    171: '🍵',
    172: '[眨眼睛]',
    173: '😭',
    174: '[无奈]',
    175: '[卖萌]',
    176: '[小纠结]',
    177: '[喷血]',
    178: '[斜眼笑]',
    179: '[doge]',
    180: '[惊喜]',
    181: '[骚扰]',
    182: '😹',
    183: '[我最美]',
    184: '🦀',
    185: '[羊驼]',
    186: '[Empty]',
    187: '👻',
    188: '🥚',
    189: '[Empty]',
    190: '🌼',
    191: '[Empty]',
    192: '🧧',
    193: '😄',
    194: '😞',
    195: '[Empty]',
    196: '[Empty]',
    197: '[冷漠]',
    198: '[呃]',
    199: '👍',
    200: '👋',
    201: '👍',
    202: '[无聊]',
    203: '[托脸]',
    204: '[吃]',
    205: '💐',
    206: '😨',
    207: '[花痴]',
    208: '[小样儿]',
    209: '[Empty]',
    210: '😭',
    211: '[我不看]',
    212: '[托腮]',
    213: '[Empty]',
    214: '😙',
    215: '[糊脸]',
    216: '[拍头]',
    217: '[扯一扯]',
    218: '[舔一舔]',
    219: '[蹭一蹭]',
    220: '[拽炸天]',
    221: '[顶呱呱]',
    222: '🤗',
    223: '[暴击]',
    224: '🔫',
    225: '[撩一撩]',
    226: '[拍桌]',
    227: '👏',
    228: '[恭喜]',
    229: '🍻',
    230: '[嘲讽]',
    231: '[哼]',
    232: '[佛系]',
    233: '[掐一掐]',
    234: '😮',
    235: '[颤抖]',
    236: '[啃头]',
    237: '[偷看]',
    238: '[扇脸]',
    239: '[原谅]',
    240: '[喷脸]',
    241: '🎂',
    242: '[Empty]',
    243: '[Empty]',
    244: '[Empty]',
    245: '[Empty]',
    246: '[Empty]',
    247: '[Empty]',
    248: '[Empty]',
    249: '[Empty]',
    250: '[Empty]',
    251: '[Empty]',
    252: '[Empty]',
    253: '[Empty]',
    254: '[Empty]',
    255: '[Empty]',
}

# original text copied from Tim
qq_emoji_text_list = {
    0:   '[惊讶]',
    1:   '[撇嘴]',
    2:   '[色]',
    3:   '[发呆]',
    4:   '[得意]',
    5:   '[流泪]',
    6:   '[害羞]',
    7:   '[闭嘴]',
    8:   '[睡]',
    9:   '[大哭]',
    10:  '[尴尬]',
    11:  '[发怒]',
    12:  '[调皮]',
    13:  '[呲牙]',
    14:  '[微笑]',
    15:  '[难过]',
    16:  '[酷]',
    17:  '[Empty]',
    18:  '[抓狂]',
    19:  '[吐]',
    20:  '[偷笑]',
    21:  '[可爱]',
    22:  '[白眼]',
    23:  '[傲慢]',
    24:  '[饥饿]',
    25:  '[困]',
    26:  '[惊恐]',
    27:  '[流汗]',
    28:  '[憨笑]',
    29:  '[悠闲]',
    30:  '[奋斗]',
    31:  '[咒骂]',
    32:  '[疑问]',
    33:  '[嘘]',
    34:  '[晕]',
    35:  '[折磨]',
    36:  '[衰]',
    37:  '[骷髅]',
    38:  '[敲打]',
    39:  '[再见]',
    40:  '[Empty]',
    41:  '[发抖]',
    42:  '[爱情]',
    43:  '[跳跳]',
    44:  '[Empty]',
    45:  '[Empty]',
    46:  '[猪头]',
    47:  '[Empty]',
    48:  '[Empty]',
    49:  '[拥抱]',
    50:  '[Empty]',
    51:  '[Empty]',
    52:  '[Empty]',
    53:  '[蛋糕]',
    54:  '[闪电]',
    55:  '[炸弹]',
    56:  '[刀]',
    57:  '[足球]',
    58:  '[Empty]',
    59:  '[便便]',
    60:  '[咖啡]',
    61:  '[饭]',
    62:  '[Empty]',
    63:  '[玫瑰]',
    64:  '[凋谢]',
    65:  '[Empty]',
    66:  '[爱心]',
    67:  '[心碎]',
    68:  '[Empty]',
    69:  '[礼物]',
    70:  '[Empty]',
    71:  '[Empty]',
    72:  '[Empty]',
    73:  '[Empty]',
    74:  '[太阳]',
    75:  '[月亮]',
    76:  '[赞]',
    77:  '[踩]',
    78:  '[握手]',
    79:  '[胜利]',
    80:  '[Empty]',
    81:  '[Empty]',
    82:  '[Empty]',
    83:  '[Empty]',
    84:  '[Empty]',
    85:  '[飞吻]',
    86:  '[怄火]',
    87:  '[Empty]',
    88:  '[Empty]',
    89:  '[西瓜]',
    90:  '[Empty]',
    91:  '[Empty]',
    92:  '[Empty]',
    93:  '[Empty]',
    94:  '[Empty]',
    95:  '[Empty]',
    96:  '[冷汗]',
    97:  '[擦汗]',
    98:  '[抠鼻]',
    99:  '[鼓掌]',
    100: '[糗大了]',
    101: '[坏笑]',
    102: '[左哼哼]',
    103: '[右哼哼]',
    104: '[哈欠]',
    105: '[鄙视]',
    106: '[委屈]',
    107: '[快哭了]',
    108: '[阴险]',
    109: '[亲亲]',
    110: '[吓]',
    111: '[可怜]',
    112: '[菜刀]',
    113: '[啤酒]',
    114: '[篮球]',
    115: '[乒乓]',
    116: '[示爱]',
    117: '[瓢虫]',
    118: '[抱拳]',
    119: '[勾引]',
    120: '[拳头]',
    121: '[差劲]',
    122: '[爱你]',
    123: '[NO]',
    124: '[OK]',
    125: '[转圈]',
    126: '[磕头]',
    127: '[回头]',
    128: '[跳绳]',
    129: '[挥手]',
    130: '[激动]',
    131: '[街舞]',
    132: '[献吻]',
    133: '[左太极]',
    134: '[右太极]',
    135: '[Empty]',
    136: '[双喜]',
    137: '[鞭炮]',
    138: '[灯笼]',
    139: '[发财]',
    140: '[K歌]',
    141: '[购物]',
    142: '[邮件]',
    143: '[帅]',
    144: '[喝彩]',
    145: '[祈祷]',
    146: '[爆筋]',
    147: '[棒棒糖]',
    148: '[喝奶]',
    149: '[下面]',
    150: '[香蕉]',
    151: '[飞机]',
    152: '[开车]',
    153: '[高铁左车头]',
    154: '[车厢]',
    155: '[高铁右车头]',
    156: '[多云]',
    157: '[下雨]',
    158: '[钞票]',
    159: '[熊猫]',
    160: '[灯泡]',
    161: '[风车]',
    162: '[闹钟]',
    163: '[打伞]',
    164: '[彩球]',
    165: '[钻戒]',
    166: '[沙发]',
    167: '[纸巾]',
    168: '[药]',
    169: '[手枪]',
    170: '[青蛙]',
    171: '[茶]',
    172: '[眨眼睛]',
    173: '[泪奔]',
    174: '[无奈]',
    175: '[卖萌]',
    176: '[小纠结]',
    177: '[喷血]',
    178: '[斜眼笑]',
    179: '[doge]',
    180: '[惊喜]',
    181: '[骚扰]',
    182: '[笑哭]',
    183: '[我最美]',
    184: '[河蟹]',
    185: '[羊驼]',
    186: '[Empty]',
    187: '[幽灵]',
    188: '[蛋]',
    189: '[Empty]',
    190: '[菊花]',
    191: '[Empty]',
    192: '[红包]',
    193: '[大笑]',
    194: '[不开心]',
    195: '[Empty]',
    196: '[Empty]',
    197: '[冷漠]',
    198: '[呃]',
    199: '[好棒]',
    200: '[拜托]',
    201: '[点赞]',
    202: '[无聊]',
    203: '[托脸]',
    204: '[吃]',
    205: '[送花]',
    206: '[害怕]',
    207: '[花痴]',
    208: '[小样儿]',
    209: '[Empty]',
    210: '[飙泪]',
    211: '[我不看]',
    212: '[托腮]',
    213: '[Empty]',
    214: '[啵啵]',
    215: '[糊脸]',
    216: '[拍头]',
    217: '[扯一扯]',
    218: '[舔一舔]',
    219: '[蹭一蹭]',
    220: '[拽炸天]',
    221: '[顶呱呱]',
    222: '[抱抱]',
    223: '[暴击]',
    224: '[开枪]',
    225: '[撩一撩]',
    226: '[拍桌]',
    227: '[拍手]',
    228: '[恭喜]',
    229: '[干杯]',
    230: '[嘲讽]',
    231: '[哼]',
    232: '[佛系]',
    233: '[掐一掐]',
    234: '[惊呆]',
    235: '[颤抖]',
    236: '[啃头]',
    237: '[偷看]',
    238: '[扇脸]',
    239: '[原谅]',
    240: '[喷脸]',
    241: '[生日快乐]',
    242: '[Empty]',
    243: '[Empty]',
    244: '[Empty]',
    245: '[Empty]',
    246: '[Empty]',
    247: '[Empty]',
    248: '[Empty]',
    249: '[Empty]',
    250: '[Empty]',
    251: '[Empty]',
    252: '[Empty]',
    253: '[Empty]',
    254: '[Empty]',
    255: '[Empty]',
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


class QQDriver(UMRDriver.BaseDriver):
    def __init__(self, name):
        self.name = name
        self.logger = UMRLogging.getLogger(f'UMRDriver.{self.name}')
        self.logger.debug(f'Started initialization for {self.name}')

        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.loop.set_exception_handler(self.handle_exception)
        self.config: Dict = UMRConfig.config['Driver'][self.name]

        attributes = [
            'Account',
            'APIRoot',
            'ListenIP',
            'ListenPort',
            'Token',
            'Secret',
            'IsPro',
            'NameforPrivateChat',
            'NameforGroupChat',
        ]
        check_attribute(self.config, attributes, self.logger)
        self.bot = CQHttp(api_root=self.config.get('APIRoot'),
                          access_token=self.config.get('Token'),
                          secret=self.config.get('Secret'))

        ##### initializations #####

        # get group list
        self.group_list: Dict[int, Dict[int, Dict]] = dict()  # Dict[group_id, Dict[member_id, member_info]]
        # see https://cqhttp.cc/docs/4.13/#/API?id=响应数据23
        self.is_coolq_pro = self.config.get('IsPro', False)  # todo initialization on startup
        self.stranger_list: Dict[int, str] = dict()

        self.chat_type_dict = {
                'group': ChatType.GROUP,
                'discuss': ChatType.DISCUSS,
                'private': ChatType.PRIVATE,
            }

        self.chat_type_dict_reverse = {v: k for k, v in self.chat_type_dict.items()}

        @self.bot.on_message()
        async def handle_msg(context):
            message_type = context.get("message_type")
            chat_id = context.get(f'{message_type}_id')
            chat_type = self.chat_type_dict[message_type]

            self.logger.debug(f'Received message from group: {chat_id} user: {context.get("user_id")}')

            unified_message_list = await self.dissemble_message(context)
            set_ingress_message_id(src_platform=self.name, src_chat_id=chat_id, src_chat_type=chat_type,
                                   src_message_id=context.get('message_id'), user_id=context.get('user_id'))
            for message in unified_message_list:
                await UMRDriver.receive(message)
            return {}

    def start(self):
        def do_nothing():
            pass

        def run():
            asyncio.set_event_loop(self.loop)
            self.logger.debug(f'Starting Quart server for {self.name}')
            self.bot.run(host=self.config.get('ListenIP'), port=self.config.get('ListenPort'), loop=self.loop,
                         shutdown_trigger=do_nothing)

        t = threading.Thread(target=run)
        t.daemon = True
        UMRDriver.threads.append(t)
        t.start()

        self.logger.debug(f'Finished initialization for {self.name}')

        ##### Define send and receive #####

    async def send(self, to_chat: Union[int, str], chat_type: ChatType, messsage: UnifiedMessage):
        """
        decorator for send new message
        :return:
        """
        self.logger.debug('calling real send')
        return asyncio.run_coroutine_threadsafe(self._send(to_chat, chat_type, messsage), self.loop)

    async def _send(self, to_chat: int, chat_type: ChatType, message: UnifiedMessage):
        """
        decorator for send new message
        :return:
        """
        self.logger.debug('begin processing message')
        context = dict()
        if chat_type == ChatType.UNSPECIFIED:
            self.logger.warning(f'Sending to undefined group or chat {to_chat}')
            return

        _chat_type = self.chat_type_dict_reverse[chat_type]
        context['message_type'] = _chat_type
        context['message'] = list()
        if message.image:
            image_name = os.path.basename(message.image)
            context['message'].append(MessageSegment.image(image_name))

        if (_chat_type == 'private' and self.config['NameforPrivateChat']) or \
                (_chat_type in ('group', 'discuss') and self.config['NameforGroupChat']):
            # name logic
            if message.chat_attrs.name:
                context['message'].append(MessageSegment.text(message.chat_attrs.name))
            if message.chat_attrs.reply_to:
                context['message'].append(MessageSegment.text(' (➡️️' + message.chat_attrs.reply_to.name + ')'))
            if message.chat_attrs.forward_from:
                context['message'].append(MessageSegment.text(' (️️↩️' + message.chat_attrs.forward_from.name + ')'))
            if message.chat_attrs.name:
                context['message'].append(MessageSegment.text(': '))

            # at user
            if message.send_action.user_id:
                context['message'].append(MessageSegment.at(message.send_action.user_id))
                context['message'].append(MessageSegment.text(' '))

        context['message'].append(MessageSegment.text(unparse_entities_to_markdown(message, EntityType.PLAIN)))

        if _chat_type == 'private':
            context['user_id'] = to_chat
        else:
            context[f'{_chat_type}_id'] = to_chat
        self.logger.debug('finished processing message, ready to send')
        result = await self.bot.send(context, context['message'])
        if message.chat_attrs:
            set_egress_message_id(src_platform=message.chat_attrs.platform,
                                  src_chat_id=message.chat_attrs.chat_id,
                                  src_chat_type=message.chat_attrs.chat_type,
                                  src_message_id=message.chat_attrs.message_id,
                                  dst_platform=self.name,
                                  dst_chat_id=to_chat,
                                  dst_chat_type=chat_type,
                                  dst_message_id=result.get('message_id'),
                                  user_id=self.config['Account'])
        self.logger.debug('finished sending')
        return result.get('message_id')

    async def get_username(self, user_id: int, chat_id: int, chat_type: ChatType):
        if user_id == self.config['Account']:
            return 'bot'
        if user_id == 1000000:
            return 'App message'
        if chat_type == ChatType.GROUP:
            user = self.group_list.get(chat_id, dict()).get(user_id, dict())
            username = user.get('card', '')
            if not username:
                username = user.get('nickname', str(user_id))
        else:
            if user_id in self.stranger_list:
                username = self.stranger_list.get(user_id)
            else:
                user = await self.bot.get_stranger_info(user_id=user_id)
                username = user.get('nickname', str(user_id))
                self.stranger_list[user_id] = username
        return username

    async def dissemble_message(self, context):
        # group_id = context.get('group_id')
        # user_id = context.get('user_id')
        # user = group_list.get(group_id, dict()).get(user_id, dict())
        # username = user.get('nickname', str(user_id))
        # for i in range(len(context['message'])):
        #     message = UnifiedMessage(from_platform=self.name, from_chat=group_id, from_user=username,
        #                              message=context.get('raw_message'))

        message_type = context.get('message_type')
        if message_type in ('group', 'discuss'):
            chat_id = context.get(f'{message_type}_id')
        else:
            chat_id = context.get('user_id')
        user_id = context.get('user_id')

        message_id = context.get('message_id')
        username = await self.get_username(user_id, chat_id, self.chat_type_dict[message_type])
        message: List[Dict] = context['message']

        unified_message = await self.parse_special_message(chat_id, self.chat_type_dict[message_type], username, message_id, user_id, message)
        if unified_message:
            return [unified_message]
        unified_message_list = await self.parse_message(chat_id, self.chat_type_dict[message_type], username, message_id, user_id, message)
        return unified_message_list

    async def parse_special_message(self, chat_id: int, chat_type: ChatType, username: str, message_id: int, user_id: int,
                                    message: List[Dict[str, Dict[str, str]]]):
        if len(message) > 1:
            return None
        message = message[0]
        message_type = message['type']
        message = message['data']
        unified_message = UnifiedMessage(platform=self.name,
                                         chat_id=chat_id,
                                         chat_type=chat_type,
                                         name=username,
                                         user_id=user_id,
                                         message_id=message_id)
        if message_type == 'share':
            unified_message.message = 'Shared '
            unified_message.message_entities.append(
                MessageEntity(start=len(unified_message.message),
                              end=len(unified_message.message) + len(message['title']),
                              entity_type=EntityType.LINK,
                              link=message['url']))
            unified_message.message += message['title']
        elif message_type == 'rich':
            if 'url' in message:
                url = message['url']
                if url.startswith('mqqapi'):
                    cq_location_regex = re.compile(r'^mqqapi:.*lat=(.*)&lon=(.*)&title=(.*)&loc=(.*)&.*$')
                    locations = cq_location_regex.findall(message['url'])  # [('lat', 'lon', 'name', 'addr')]
                    unified_message.message = f'Shared a location: {locations[2]}, {locations[3]}, {locations[0]}, {locations[1]}'
                else:
                    unified_message.message = 'Shared '
                    unified_message.message_entities.append(
                        MessageEntity(start=len(unified_message.message),
                                      end=len(unified_message.message) + len(message['title']),
                                      entity_type=EntityType.LINK,
                                      link=message['url']))
                    unified_message.message += message['title']
            elif 'title' in message:
                if 'content' in message:
                    try:
                        content = json.loads(message['content'])
                        if 'news' in content:
                            unified_message.message = 'Shared '
                            unified_message.message_entities.append(
                                MessageEntity(start=len(unified_message.message),
                                              end=len(unified_message.message) + len(message['title']),
                                              entity_type=EntityType.LINK,
                                              link=content.get('jumpUrl')))
                            unified_message.message += message['title'] + ' ' + message.get('desc')
                        elif 'weather' in content:
                            unified_message.message = message['title']
                    except:
                        self.logger.exception(f'Cannot decode json: {str(message)}')
                        unified_message.message = message['title']
                else:
                    unified_message.message = message['title']
            else:
                self.logger.debug(f'Got miscellaneous rich text message: {str(message)}')
                unified_message.message = message.get('text', str(message))
        elif message_type == 'dice':
            unified_message.message = 'Rolled '
            unified_message.message_entities.append(
                MessageEntity(start=len(unified_message.message),
                              end=len(unified_message.message) + len(message['type']),
                              entity_type=EntityType.BOLD))
            unified_message.message += message['type']
        elif message_type == 'rps':
            unified_message.message = 'Played '
            played = {'1': 'Rock',
                                    '2': 'Scissors',
                                    '3': 'Paper'}[message['type']]
            unified_message.message_entities.append(
                MessageEntity(start=len(unified_message.message),
                              end=len(unified_message.message) + len(played),
                              entity_type=EntityType.BOLD))
            unified_message.message += played
        elif message_type == 'shake':
            unified_message.message = 'Sent you a shake'
        elif message_type == 'music':
            if message['type'].startswith('163'):
                unified_message.message = 'Shared a music: '
                music_title = 'Netease Music'
                unified_message.message_entities.append(
                    MessageEntity(start=len(unified_message.message),
                                  end=len(unified_message.message) + len(music_title),
                                  entity_type=EntityType.LINK,
                                  link=f'https://music.163.com/song?id={message["id"]}'))
                unified_message += music_title
            elif message['type'].startswith('qq'):
                unified_message.message = 'Shared a music: '
                music_title = 'Netease Music'
                unified_message.message_entities.append(
                    MessageEntity(start=len(unified_message.message),
                                  end=len(unified_message.message) + len(music_title),
                                  entity_type=EntityType.LINK,
                                  link=f'https://y.qq.com/n/yqq/song/{message["id"]}_num.html'))
                unified_message += music_title
            else:
                self.logger.debug(f'Got unseen music share message: {str(message)}')
                unified_message.message = 'Shared a music: ' + str(message)
        elif message_type == 'record':
            unified_message.message = 'Unsupported voice record, please view on QQ'
        elif message_type == 'bface':
            unified_message.message = 'Unsupported big face, please view on QQ'
        elif message_type == 'sign':
            unified_message.image = message['image']
            sign_text = f'Sign at location: {message["location"]} with title: {message["title"]}'
            unified_message.message = sign_text
        else:
            return

        return unified_message

    async def parse_message(self, chat_id: int, chat_type: ChatType, username: str, message_id: int, user_id: int,
                            message: List[Dict[str, Dict[str, str]]]):
        message_list = list()
        unified_message = UnifiedMessage(platform=self.name,
                                         chat_id=chat_id,
                                         chat_type=chat_type,
                                         name=username,
                                         user_id=user_id,
                                         message_id=message_id)
        for m in message:
            message_type = m['type']
            m = m['data']
            if message_type == 'image':
                # message not empty or contained a image, append to list
                if unified_message.message or unified_message.image:
                    message_list.append(unified_message)
                    unified_message = UnifiedMessage(platform=self.name,
                                                     chat_id=chat_id,
                                                     chat_type=chat_type,
                                                     name=username,
                                                     user_id=user_id,
                                                     message_id=message_id)
                unified_message.image = m['url']

            elif message_type == 'text':
                unified_message.message += m['text']
            elif message_type == 'at':
                target = await self.get_username(int(m['qq']), chat_id, chat_type)
                at_user_text = '@' + target
                unified_message.message_entities.append(
                    MessageEntity(start=len(unified_message.message),
                                  end=len(unified_message.message) + len(at_user_text),
                                  entity_type=EntityType.BOLD))
                unified_message.message += at_user_text
            elif message_type == 'sface':
                qq_face = int(m['id']) & 255
                if qq_face in qq_sface_list:
                    unified_message.message += qq_sface_list[qq_face]
                else:
                    unified_message.message += '\u2753'  # ❓
            elif message_type == 'face':
                qq_face = int(m['id'])
                if qq_face in qq_emoji_list:
                    unified_message.message += qq_emoji_list[qq_face]
                else:
                    unified_message.message += '\u2753'  # ❓
            else:
                self.logger.debug(f'Unhandled message type: {str(m)} with type: {message_type}')

        message_list.append(unified_message)
        return message_list

    async def is_group_admin(self, chat_id: int, chat_type: ChatType, user_id: int):
        if chat_type != ChatType.GROUP:
            return False
        if chat_id not in self.group_list:
            return False
        return self.group_list[chat_id][user_id]['role'] in ('owner', 'admin')

    async def is_group_owner(self, chat_id: int, chat_type: ChatType, user_id: int):
        if chat_type != ChatType.GROUP:
            return False
        if chat_id not in self.group_list:
            return False
        return self.group_list[chat_id][user_id]['role'] == 'owner'

    def handle_exception(self, loop, context):
        # context["message"] will always be there; but context["exception"] may not
        msg = context.get("exception", context["message"])
        self.logger.exception('Unhandled exception: ', exc_info=msg)


UMRDriver.register_driver('QQ', QQDriver)
