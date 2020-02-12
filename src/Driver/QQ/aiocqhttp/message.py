"""
此模块提供了消息相关类。
"""

import re
from typing import Iterable, Dict, Tuple, Any, Optional


def escape(s: str, *, escape_comma: bool = True) -> str:
    """
    对字符串进行 CQ 码转义。

    ``escape_comma`` 参数控制是否转义逗号（``,``）。
    """
    s = s.replace('&', '&amp;') \
        .replace('[', '&#91;') \
        .replace(']', '&#93;')
    if escape_comma:
        s = s.replace(',', '&#44;')
    return s


def unescape(s: str) -> str:
    """对字符串进行 CQ 码去转义。"""
    return s.replace('&#44;', ',') \
        .replace('&#91;', '[') \
        .replace('&#93;', ']') \
        .replace('&amp;', '&')


def _b2s(b: bool):
    if b:
        return 'true'
    else:
        return 'false'


class MessageSegment(dict):
    """
    消息段，即表示成字典的 CQ 码。

    不建议手动构造消息段；建议使用此类的静态方法构造，例如：

    ```py
    at_seg = MessageSegment.at(10001000)
    ```

    可进行判等和加法操作，例如：

    ```py
    assert at_seg == MessageSegment.at(10001000)
    msg: Message = at_seg + MessageSegment.face(14)
    ```
    """

    def __init__(self, d: Optional[Dict[str, Any]] = None, *,
                 type_: Optional[str] = None,
                 data: Optional[Dict[str, str]] = None):
        super().__init__()
        if isinstance(d, dict) and d.get('type'):
            self.update(d)
        elif type_:
            self.type = type_
            self.data = data
        else:
            raise ValueError('the "type" field cannot be None or empty')

    def __getitem__(self, item):
        if item not in ('type', 'data'):
            raise KeyError(f'the key "{item}" is not allowed')
        return super().__getitem__(item)

    def __setitem__(self, key, value):
        if key not in ('type', 'data'):
            raise KeyError(f'the key "{key}" is not allowed')
        return super().__setitem__(key, value)

    def __delitem__(self, key):
        raise NotImplementedError

    @property
    def type(self) -> str:
        """
        消息段类型，即 CQ 码功能名。

        纯文本消息段的类型名为 ``text``。
        """
        return self['type']

    @type.setter
    def type(self, type_: str):
        self['type'] = type_

    @property
    def data(self) -> Dict[str, str]:
        """
        消息段数据，即 CQ 码参数。

        该字典内所有值都是未经 CQ 码转义的字符串。
        """
        return self['data']

    @data.setter
    def data(self, data: Optional[Dict[str, str]]):
        self['data'] = data or {}

    def __str__(self):
        if self.type == 'text':
            return escape(self.data.get('text', ''), escape_comma=False)

        params = ','.join(('{}={}'.format(k, escape(str(v)))
                           for k, v in self.data.items()))
        if params:
            params = ',' + params
        return '[CQ:{type}{params}]'.format(type=self.type, params=params)

    def __eq__(self, other):
        if not isinstance(other, MessageSegment):
            return False
        return self.type == other.type and self.data == other.data

    def __add__(self, other: Any):
        return Message(self).__add__(other)

    @staticmethod
    def text(text: str) -> 'MessageSegment':
        """纯文本。"""
        return MessageSegment(type_='text', data={'text': text})

    @staticmethod
    def emoji(id_: int) -> 'MessageSegment':
        """Emoji 表情。"""
        return MessageSegment(type_='emoji', data={'id': str(id_)})

    @staticmethod
    def face(id_: int) -> 'MessageSegment':
        """QQ 表情。"""
        return MessageSegment(type_='face', data={'id': str(id_)})

    @staticmethod
    def image(file: str) -> 'MessageSegment':
        """图片。"""
        return MessageSegment(type_='image', data={'file': file})

    @staticmethod
    def record(file: str, magic: bool = False) -> 'MessageSegment':
        """语音。"""
        return MessageSegment(type_='record', data={
            'file': file,
            'magic': _b2s(magic)
        })

    @staticmethod
    def at(user_id: int) -> 'MessageSegment':
        """@某人。"""
        return MessageSegment(type_='at', data={'qq': str(user_id)})

    @staticmethod
    def rps() -> 'MessageSegment':
        """猜拳魔法表情。"""
        return MessageSegment(type_='rps')

    @staticmethod
    def dice() -> 'MessageSegment':
        """掷骰子魔法表情。"""
        return MessageSegment(type_='dice')

    @staticmethod
    def shake() -> 'MessageSegment':
        """戳一戳。"""
        return MessageSegment(type_='shake')

    @staticmethod
    def anonymous(ignore_failure: bool = False) -> 'MessageSegment':
        """匿名发消息。"""
        return MessageSegment(type_='anonymous',
                              data={'ignore': _b2s(ignore_failure)})

    @staticmethod
    def share(url: str, title: str, content: str = '',
              image_url: str = '') -> 'MessageSegment':
        """链接分享。"""
        return MessageSegment(type_='share', data={
            'url': url,
            'title': title,
            'content': content,
            'image': image_url
        })

    @staticmethod
    def contact_user(id_: int) -> 'MessageSegment':
        """推荐好友。"""
        return MessageSegment(type_='contact', data={
            'type': 'qq',
            'id': str(id_)
        })

    @staticmethod
    def contact_group(id_: int) -> 'MessageSegment':
        """推荐群。"""
        return MessageSegment(type_='contact', data={
            'type': 'group',
            'id': str(id_)
        })

    @staticmethod
    def location(latitude: float, longitude: float, title: str = '',
                 content: str = '') -> 'MessageSegment':
        """位置。"""
        return MessageSegment(type_='location', data={
            'lat': str(latitude),
            'lon': str(longitude),
            'title': title,
            'content': content
        })

    @staticmethod
    def music(type_: str, id_: int,
              style: Optional[int] = None) -> 'MessageSegment':
        """音乐"""
        if style is not None:
            return MessageSegment(type_='music', data={
                'type': type_,
                'id': str(id_),
                'style': str(style)
            })
        return MessageSegment(type_='music', data={
            'type': type_,
            'id': str(id_)
        })

    @staticmethod
    def music_custom(url: str, audio_url: str, title: str, content: str = '',
                     image_url: str = '') -> 'MessageSegment':
        """音乐自定义分享。"""
        return MessageSegment(type_='music', data={
            'type': 'custom',
            'url': url,
            'audio': audio_url,
            'title': title,
            'content': content,
            'image': image_url
        })


class Message(list):
    """
    消息，即消息段列表。
    """

    def __init__(self, msg: Any = None, *args, **kwargs):
        """``msg`` 参数为要转换为 `Message` 对象的字符串、列表或字典。"""
        super().__init__(*args, **kwargs)
        try:
            if isinstance(msg, (list, str)):
                self.extend(msg)
            elif isinstance(msg, dict):
                self.append(msg)
        except ValueError:
            raise ValueError('the msg argument is not recognizable')

    @staticmethod
    def _split_iter(msg_str: str) -> Iterable[MessageSegment]:
        def iter_function_name_and_extra() -> Iterable[Tuple[str, str]]:
            text_begin = 0
            for cqcode in re.finditer(r'\[CQ:(?P<type>[a-zA-Z0-9-_.]+)'
                                      r'(?P<params>'
                                      r'(?:,[a-zA-Z0-9-_.]+=?[^,\]]*)*'
                                      r'),?\]',
                                      msg_str):
                yield 'text', unescape(
                    msg_str[text_begin:cqcode.pos + cqcode.start()])
                text_begin = cqcode.pos + cqcode.end()
                yield cqcode.group('type'), cqcode.group('params').lstrip(',')
            yield 'text', unescape(msg_str[text_begin:])

        for function_name, extra in iter_function_name_and_extra():
            if function_name == 'text':
                if extra:
                    # only yield non-empty text segment
                    yield MessageSegment(type_=function_name,
                                         data={'text': extra})
            else:
                data = {k: v for k, v in map(
                    lambda x: x.split('=', maxsplit=1),
                    filter(lambda x: x, (x.lstrip() for x in extra.split(',')))
                )}
                yield MessageSegment(type_=function_name, data=data)

    def __str__(self):
        return ''.join((str(seg) for seg in self))

    def __add__(self, other: Any):
        result = Message(self)
        try:
            if isinstance(other, Message):
                result.extend(other)
            elif isinstance(other, MessageSegment):
                result.append(other)
            elif isinstance(other, list):
                result.extend(map(lambda d: MessageSegment(d), other))
            elif isinstance(other, dict):
                result.append(MessageSegment(other))
            elif isinstance(other, str):
                result.extend(Message._split_iter(other))
            return result
        except ValueError:
            raise ValueError('the addend is not a valid message')

    def append(self, obj: Any) -> Any:
        """在消息末尾追加消息段。"""
        try:
            if isinstance(obj, MessageSegment):
                if self and self[-1].type == 'text' and obj.type == 'text':
                    self[-1].data['text'] += obj.data['text']
                elif obj.type != 'text' or obj.data['text'] or not self:
                    super().append(obj)
            else:
                self.append(MessageSegment(obj))
            return self
        except ValueError:
            raise ValueError('the object is not a valid message segment')

    def extend(self, msg: Any) -> Any:
        """在消息末尾追加消息（字符串或消息段列表）。"""
        try:
            if isinstance(msg, str):
                msg = self._split_iter(msg)

            for seg in msg:
                self.append(seg)
            return self
        except ValueError:
            raise ValueError('the object is not a valid message')

    def reduce(self) -> None:
        """
        化简消息，即去除多余消息段、合并相邻纯文本消息段。

        由于 `Message` 类基于 `list`，此方法时间复杂度为 O(n)。
        """
        idx = 0
        while idx < len(self):
            if idx > 0 and \
                    self[idx - 1].type == 'text' and self[idx].type == 'text':
                self[idx - 1].data['text'] += self[idx].data['text']
                del self[idx]
            else:
                idx += 1

    def extract_plain_text(self, reduce: bool = False) -> str:
        """
        提取消息中的所有纯文本消息段，合并，中间用空格分隔。

        ``reduce`` 参数控制是否在提取之前化简消息。
        """
        if reduce:
            self.reduce()

        result = ''
        for seg in self:
            if seg.type == 'text':
                result += ' ' + seg.data['text']
        if result:
            result = result[1:]
        return result
