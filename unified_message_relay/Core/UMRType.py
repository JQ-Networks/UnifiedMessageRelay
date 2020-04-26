from __future__ import annotations
from dataclasses import dataclass
from typing import List, Callable, FrozenSet, Union
from enum import Enum, auto, Flag


class LogLevel(str, Enum):
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'


class ChatType(str, Enum):
    """
    Command filter option
    """
    UNSPECIFIED = 'unspecified'
    PRIVATE = 'private'
    DISCUSS = 'discuss'
    GROUP = 'group'


class ForwardTypeEnum(str, Enum):
    OneWay = 'OneWay'
    OneWayPlus = 'OneWay+'
    BiDirection = 'BiDirection'


class DefaultForwardTypeEnum(str, Enum):
    OneWay = 'OneWay'
    OneWayPlus = 'OneWay+'


class Privilege(str, Enum):
    """
    Command filter option
    The privilege of lower number always contain the privilege of the higher number
    """
    UNSPECIFIED = 'unspecified'  # permit all, available everywhere
    GROUP_ADMIN = 'group_admin'  # only available in group
    GROUP_OWNER = 'group_owner'  # only available in group
    BOT_ADMIN = 'bot_admin'      # only bot admin, available everywhere


class ChatAttribute:
    """
    Part of UnifiedMessage
    Attributes for every received message. Recursive attributes exist for some platform.
    """
    def __init__(self, platform: str = '', chat_id: Union[int, str] = 0, chat_type: ChatType = ChatType.UNSPECIFIED,
                 name: str = '', user_id: Union[int, str] = 0, message_id: int = 0):
        self.platform = platform
        self.chat_id = chat_id
        self.chat_type = chat_type
        self.name = name
        self.user_id = user_id
        self.message_id = message_id
        self.forward_from: Union[None, ChatAttribute] = None
        self.reply_to: Union[None, ChatAttribute] = None

    def __bool__(self):
        return self.platform is not None


class EntityType(Flag):
    """
    Each message entity in UnifiedMessage should be monolithic
    Only EitityType in unparse_* should be multi-valued
    """
    PLAIN = auto()
    BOLD = auto()
    ITALIC = auto()
    CODE = auto()
    CODE_BLOCK = auto()
    UNDERLINE = auto()
    STRIKETHROUGH = auto()
    QUOTE = auto()
    QUOTE_BLOCK = auto()
    LINK = auto()


@dataclass
class MessageEntity:
    """
    Part of UnifiedMessage
    Text segments with entity types
    """
    start: int
    end: int
    entity_type: EntityType
    link: str

    def __init__(self, start, end, entity_type=EntityType.PLAIN, link=''):
        self.start = start
        self.end = end
        self.entity_type = entity_type
        self.link = link


@dataclass
class SendAction:
    """
    Part of UnifiedMessage
    Currently the action only supports reply to a message or user
    """
    message_id: int
    user_id: int


@dataclass
class UnifiedMessage:
    """
    message: List of MessageEntity
    e.g.
    [
        ('this is text',         'bold'),
        ('this is another text', 'italic'),
        ('this is another text', 'monospace'),
        ('this is another text', 'underline'),
        ('this is another text', 'strikethrough'),
        ('http://..',            'link',    'title of the link (optional)')

    ]
    """
    chat_attrs: ChatAttribute
    text: str  # pure text message
    text_entities: List[MessageEntity]
    image: str  # path of the image or download url
    file_id: str  # unique file identifier
    send_action: SendAction

    def __init__(self, text: str = '', message_entities=None, image='', file_id='', platform='', chat_id=0, chat_type=ChatType.UNSPECIFIED,
                 name='', user_id=0, message_id: int = 0):
        self.send_action = SendAction(0, 0)
        self.text = text
        if message_entities:
            self.text_entities = message_entities
        else:
            self.text_entities = list()
        self.image = image
        self.file_id = file_id
        self.chat_attrs = ChatAttribute(platform=platform,
                                        chat_id=chat_id,
                                        chat_type=chat_type,
                                        name=name,
                                        user_id=user_id,
                                        message_id=message_id)


@dataclass
class PrivilegeAttributes:
    """
    Currently not used in any part of the code
    """
    is_admin: bool
    is_owner: bool


@dataclass
class ControlMessage:
    """
        Currently not used in any part of the code
    """
    prompt: str
    answers: List[str]  # use empty list for open questions
    privilege_attrs: PrivilegeAttributes  # privilege required
    identifier: int  # id to match response with prompt

    def __init__(self, prompt=None, answers=None, is_admin=None, is_owner=False, identifier=-1):
        if answers is None:
            answers = list()
        self.prompt = prompt
        self.answers = answers
        self.privilege_attrs = PrivilegeAttributes(is_admin, is_owner)
        self.identifier = identifier


class ForwardActionType(Enum):
    """
    Dispatch filter, filters message reply attribute
    """
    ForwardAll = 1  # message can go to the other side
    ReplyOnly = 2   # message that replies to forwarded message can go to the other side
    Block = 3       # message that cannot go to the other side (one way)


class DefaultForwardActionType(Enum):
    """
    Dispatch filter, filters message reply attribute
    """
    OneWay = 1           # aggregate message only, no backward
    OneWayWithReply = 2  # aggregate message and allow backward


@dataclass
class ForwardAction:
    """
    Dispatch action, final action for matching message
    """
    to_platform: str
    to_chat: Union[int, str]
    chat_type: ChatType
    action_type: ForwardActionType  # All, Reply


@dataclass
class DefaultForwardAction:
    """
    Dispatch action, final action for matching message
    """
    to_platform: str
    to_chat: Union[int, str]
    chat_type: ChatType
    action_type: DefaultForwardActionType  # All, Reply


@dataclass
class MessageHook:
    """
    Message Hook parameters
    """
    src_driver: FrozenSet[str]
    src_chat: FrozenSet[int]
    src_chat_type: FrozenSet[ChatType]
    dst_driver: FrozenSet[str]
    dst_chat: FrozenSet[int]
    dst_chat_type: FrozenSet[ChatType]
    hook_function: Callable

    def __init__(self, src_driver: Union[str, List[str]], src_chat: Union[int, List[int]], src_chat_type: Union[ChatType, List[ChatType]],
                 dst_driver: Union[str, List[str]], dst_chat: Union[int, List[int]], dst_chat_type: Union[ChatType, List[ChatType]], hook_function: Callable):
        if isinstance(src_driver, str):
            if src_driver:
                self.src_driver = frozenset([src_driver])
            else:
                self.src_driver = frozenset()
        else:
            self.src_driver = frozenset(src_driver)
        if isinstance(src_chat, int):
            if src_chat:
                self.src_chat = frozenset([src_chat])
            else:
                self.src_chat = frozenset()
        else:
            self.src_chat = frozenset(src_chat)
        if isinstance(src_chat_type, ChatType):
            self.src_chat_type = frozenset([src_chat_type])
        else:
            self.src_chat_type = frozenset(src_chat_type)
        if isinstance(dst_driver, str):
            if dst_driver:
                self.dst_driver = frozenset([dst_driver])
            else:
                self.dst_driver = frozenset()
        else:
            self.dst_driver = frozenset(dst_driver)
        if isinstance(dst_chat, int):
            if dst_chat:
                self.dst_chat = frozenset([dst_chat])
            else:
                self.dst_chat = frozenset()
        else:
            self.dst_chat = frozenset(dst_chat)
        if isinstance(dst_chat_type, ChatType):
            self.dst_chat_type = frozenset([dst_chat_type])
        else:
            self.dst_chat_type = frozenset(dst_chat_type)
        self.hook_function = hook_function


@dataclass
class Command:
    """
    Command parameters
    """
    platform: FrozenSet[str]
    description: str
    privilege: Privilege
    chat_type: ChatType
    command_function: Callable

    def __init__(self, platform: Union[str, List[str]] = '', description='', chat_type=ChatType.UNSPECIFIED,
                 privilege=Privilege.UNSPECIFIED, command_function=None):
        if isinstance(platform, str):
            if platform:
                self.platform = frozenset([platform])
            else:
                self.platform = frozenset()
        else:
            self.platform = frozenset(platform)
        self.description = description
        self.chat_type = chat_type
        self.privilege = privilege
        self.command_function = command_function


@dataclass(frozen=True)
class GroupID:
    """
    Used in MessageRelation
    """
    platform: str
    chat_type: ChatType
    chat_id: Union[int, str]


@dataclass(frozen=True)
class MessageID:
    """
    Used in MessageRelation
    """
    platform: str
    chat_id: Union[int, str]
    chat_type: ChatType
    message_id: int


@dataclass
class DestinationMessageID:
    """
    Used in MessageRelation
    """
    platform: str = ''
    chat_id: Union[int, str] = 0
    chat_type: ChatType = ChatType.UNSPECIFIED
    message_id: int = 0
    user_id: int = 0
    source: DestinationMessageID = None

