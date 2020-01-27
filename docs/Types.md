# Types

This page may not be up to date, see `src/core/UMRType.py` for latest information.

```python
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


class ActionType(Enum):
    All = 1
    Reply = 2


@dataclass
class Action:
    to_platform: str
    to_chat: int
    action_type: ActionType  # All, Reply


@dataclass
class MessageHook:
    src_driver: str
    src_chat: int
    dst_driver: str
    dst_chat: int
    hook_function: Callable


@dataclass
class Command:
    platform: FrozenSet[str]
    description: str
    command_function: Callable
```