from dataclasses import dataclass
from typing import List, Callable, FrozenSet, Union
from enum import Enum


@dataclass
class ForwardAttributes:
    from_platform: str
    from_chat: int
    from_user: str
    from_user_id: int
    from_message_id: int
    forward_from_user: str  # an user's name, or whatever the name of the source
    forward_from_chat: int
    reply_to_user: str  # reply to some user
    reply_to_message_id: int


@dataclass
class MessageEntity:
    text: str
    entity_type: str
    link: str

    def __init__(self, text='', entity_type='', link=''):
        self.text = text
        self.entity_type = entity_type
        self.link = link


@dataclass
class SendAction:
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
    forward_attrs: ForwardAttributes
    message: List[MessageEntity]  # pure text message
    image: str  # path of the image
    send_action: SendAction

    def __init__(self, message=None, image='', from_platform='', from_chat=-1, from_user='', from_user_id=0,
                 forward_from_user='', reply_to_user='', from_message_id: int = 0, forward_from_chat: int = 0,
                 reply_to_message_id: int = 0):
        if message is None:
            message = list()
        self.send_action = SendAction(0, 0)
        self.message = message
        self.image = image
        self.forward_attrs = ForwardAttributes(from_platform=from_platform,
                                               from_chat=from_chat,
                                               from_user=from_user,
                                               from_user_id=from_user_id,
                                               from_message_id=from_message_id,
                                               forward_from_user=forward_from_user,
                                               reply_to_user=reply_to_user,
                                               forward_from_chat=forward_from_chat,
                                               reply_to_message_id=reply_to_message_id)


@dataclass
class PrivilegeAttributes:
    is_admin: bool
    is_owner: bool


@dataclass
class ControlMessage:
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
    All = 1
    Reply = 2


@dataclass
class ForwardAction:
    to_platform: str
    to_chat: int
    action_type: ForwardActionType  # All, Reply


@dataclass
class MessageHook:
    src_driver: FrozenSet[str]
    src_chat: FrozenSet[int]
    dst_driver: FrozenSet[str]
    dst_chat: FrozenSet[int]
    hook_function: Callable

    def __init__(self, src_driver: Union[str, List[str]], src_chat: Union[int, List[int]],
                 dst_driver: Union[str, List[str]], dst_chat: Union[int, List[int]], hook_function: Callable):
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
        self.hook_function = hook_function


@dataclass
class Command:
    platform: FrozenSet[str]
    description: str
    command_function: Callable

    def __init__(self, platform: Union[str, List[str]] = '', description='', command_function=None):
        if isinstance(platform, str):
            if platform:
                self.platform = frozenset([platform])
            else:
                self.platform = frozenset()
        else:
            self.platform = frozenset(platform)
        self.description = description
        self.command_function = command_function


@dataclass(frozen=True)
class GroupID:
    platform: str
    chat_id: int


@dataclass(frozen=True)
class MessageID:
    platform: str
    chat_id: int
    message_id: int


@dataclass(frozen=True)
class DestinationMessageID:
    platform: str
    chat_id: int
    message_id: int
    user_id: int
