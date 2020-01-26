# Command

```python
from typing import List
from asyncio import iscoroutinefunction
from Core.UMRType import ForwardAttributes, UnifiedMessage, MessageEntity
from Core.UMRCommand import register_command
from Core.UMRDriver import api_lookup
@register_command('echo')
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
