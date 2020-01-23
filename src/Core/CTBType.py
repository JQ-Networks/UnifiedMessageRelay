from dataclasses import dataclass
from typing import List
from enum import Enum


@dataclass
class ForwardAttributes:
    from_platform: str
    from_chat: int
    from_user: str
    forward_from: str  # an user's name, or whatever the name of the source
    reply_to: str  # reply to some user


@dataclass
class PrivilegeAttributes:
    is_admin: bool
    is_owner: bool


@dataclass
class UnifiedMessage:
    forward_attrs: ForwardAttributes
    message: str  # pure text message
    image: str  # path of the image

    def __init__(self, message='', image='', from_platform='', from_chat=-1, from_user='', forward_from='',
                 reply_to=''):
        self.message = message
        self.image = image
        self.forward_attrs = ForwardAttributes(from_platform, from_chat, from_user, forward_from, reply_to)


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
