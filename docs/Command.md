# Command

Command module allows simple interaction between users and plugins.

## Example

```python
from typing import List
from Core.UMRType import ChatAttribute, ChatType, Privilege
from Core.UMRCommand import register_command, quick_reply


@register_command(cmd='echo', description='reply every word you sent')
async def command(chat_attrs: ChatAttribute, args: List):
    """
    Prototype of command
    :param chat_attrs:
    :param args:
    :return:
    """
    if not args:  # args should not be empty
        return

    await quick_reply(chat_attrs, ' '.join(args))

```

The example above provides basic reply function: it replies whenever you send !!echo with some arguments.

## Details

### register_command
A complete version of `register_command`
```python
from Core.UMRType import ChatAttribute, ChatType, Privilege
from Core.UMRCommand import register_command, quick_reply
from typing import List

@register_command(cmd=['cmd1', 'cmd2', ...], platform=['QQ', 'Telegram', ...],
 description='Your description goes here', chat_type=ChatType.PRIVATE_CHAT, privilege=Privilege.BOT_ADMIN)
async def command(chat_attrs: ChatAttribute, args: List):
    pass
```

#### Args:
- cmd: str or List\[str\], depends on how many aliases for the same command.
- platform: str or List\[str\], only command from these platform will be handled. Leave empty for match all.
- description: str, something that will show up in `!!help`.
- chat_type: the chat requirement of this message, possible values listed in `UMRTypes.ChatType`
- privilege: the privilege requirement of this command, possible values listed in `UMRTypes.Privilege`

### function prototype
```python
async def command(chat_attrs: ForwardAttributes, args: List):
    pass
```

#### Args:
- chat_attrs: `UMRTypes.ChatAttribute`
- args: list of str, extracted from the rest of the command split by spaces 

#### Return:

Not required
