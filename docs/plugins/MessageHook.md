# Message Hook

```python
from Core.UMRType import UnifiedMessage
async def message_hook_func(dst_driver: str, dst_chat: int,
                            message: UnifiedMessage) -> bool:
    """
    Prototype of message hook function with four tuple match
    src_driver and src_chat are stored in message
    :param dst_driver: driver name
    :param dst_chat: chat id
    :param message: unified message
    :return: True for block message forwarding, False for call next hook
    """
    pass


async def message_hook_func(message: UnifiedMessage) -> bool:
    """
    Prototype of message hook function with two tuple match
    src_driver and src_chat are stored in message
    :param message: unified message
    :return: True for block message forwarding, False for call next hook
    """
    pass
```
