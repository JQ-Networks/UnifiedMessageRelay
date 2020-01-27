# Command

Command module allows simple interaction between users and plugins.

## Example

```python
from typing import List
from asyncio import iscoroutinefunction
from Core.UMRType import ForwardAttributes, UnifiedMessage, MessageEntity
from Core.UMRCommand import register_command
from Core.UMRDriver import api_lookup
@register_command(cmd='echo', platform='', description='The human nature')
async def command(forward_attrs: ForwardAttributes, args: List):
    """
    Prototype of command
    :param forward_attrs:
    :param args:
    :return:
    """
    if not args:  # test empty
        return 
    
    send = api_lookup(forward_attrs.from_platform, 'send')
    if not send:
        return
    message = UnifiedMessage()
    message.message.append(MessageEntity(text=' '.join(args)))
    if iscoroutinefunction(send):
        await send(forward_attrs.from_chat, message)
    else:
        send(forward_attrs.from_chat, message)
```

## Details

### register_command
```python
@register_command(cmd='echo', platform='', description='The human nature')

@register_command(cmd=['echo', 'repeat'], platform=['QQ', 'Telegram'], description='The human nature')
```

It has three args:
- cmd: str or List\[str\], depends on how many aliases for the same command.
- platform: str or List\[str\], only command from these platform will be handled. Leave empty for match all.
- description: str, something that will show up in `!!help`.

### function prototype
```python
async def command(forward_attrs: ForwardAttributes, args: List):
    pass
```

It has two args:
- forward_attrs: see [Types](Types.md) for details
- args: list of str, extracted from the rest of the command