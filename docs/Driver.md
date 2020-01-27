# Driver

## API 
Driver should implement the following API

```python
import asyncio
from Core.UMRType import UnifiedMessage

async def send(to_chat: int, messsage: UnifiedMessage) -> asyncio.Future:
    """
    function prototype for send new message
    this function should be implemented in driver, sync or async
    :return: future object contains message id
    """
    pass
```

Or the synced version, if async not available:

```python
from Core.UMRType import UnifiedMessage
def send(to_chat: int, messsage: UnifiedMessage) -> int:
    """
    function prototype for send new message
    this function should be implemented in driver, sync or async
    :return: message id
    """
    pass
```

Driver must make sure that this function can be called directly from other events loop or threads.

## Income message
Driver should also implement the following handler, e.g. QQ:

```python
@bot.on_message()
async def handle_msg(context):
    group_id = context.get('group_id')
    if group_type.get(group_id) != context.get('message_type'):  # filter unknown group chat
        logger.debug(f'ignored unknown source: {context.get("message_type")}: {group_id}')
        return {}

    unified_message_list = await dissemble_message(context)
    for message in unified_message_list:
        await UMRDriver.receive(message)
    return {}
```

What is important about this code snippet is `await UMRDriver.receive(message)`. The driver should parse the income message
 to UnifiedMessage, and then call `UMRDriver.receive(message)`. This is an async function, and driver should use their own
  event loop to call this function.
  
## Calling driver

Due to the limitation of async, calling send is verbose and there is nothing I can do about it. One approach is to drop 
support for synced driver, but this is not decided yet.

```python
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