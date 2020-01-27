# Message Hook

Message hook api provides more flexible message handling

## Example

```python
from Core.UMRType import UnifiedMessage
from Core.UMRMessageHook import register_hook
@register_hook(src_driver='QQ', src_chat=123123, dst_driver='Telegram', dst_chat=124434)
async def message_hook_func(dst_driver: str, dst_chat: int,
                            message: UnifiedMessage) -> bool:
    """
    Prototype of message hook function with four tuple match
    :param dst_driver: driver name
    :param dst_chat: chat id
    :param message: unified message
    :return: True for block message forwarding, False for call next hook
    """
    pass


@register_hook(src_driver='QQ', src_chat=123123)
async def message_hook_func(message: UnifiedMessage) -> bool:
    """
    Prototype of message hook function with two tuple match
    :param message: unified message
    :return: True for block message forwarding, False for call next hook
    """
    pass
```

`@register_hook` has four arguments:
 - `src_driver`: str or List[str], the source driver
 - `src_chat`: int or List[int], the source chat id
 - `dst_driver`: str or List[str], the destination driver
 - `dst_chat`: int or List[int], the destination chat id
 
 WHen dst_\* are empty, the function prototype should be:
 
 `async def message_hook_func(message: UnifiedMessage) -> bool:`
 
 The reason is intuitive: for directed graph forwarding, there could be one to many forwards, and the message hook will
  be call multiple times if matches. As a result, a source based hook is provided and it only matches once per source. If
  the plugin doesn't care the destination, then leave dst_\* blank for single time match. If destination is what you care
   about and you wish to be called once per destination hit, then write down any of the dst_\*.