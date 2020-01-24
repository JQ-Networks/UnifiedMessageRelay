from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum


@dataclass
class ForwardAttributes:
    from_platform: str
    from_chat: int
    from_user: str
    forward_from: str  # an user's name, or whatever the name of the source
    reply_to: str  # reply to some user


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

    def __init__(self, message=None, image='', from_platform='', from_chat=-1, from_user='', forward_from='',
                 reply_to=''):
        if message is None:
            message = list()
        self.message = message
        self.image = image
        self.forward_attrs = ForwardAttributes(from_platform, from_chat, from_user, forward_from, reply_to)


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


class ActionType(Enum):
    All = 1
    Reply = 2


@dataclass
class Action:
    to_platform: str
    to_chat: int
    action_type: ActionType  # All, Reply
