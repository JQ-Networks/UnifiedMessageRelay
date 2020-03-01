# Driver

## API
Driver should implement the following API

### Send
```python
async def send(self, to_chat: int, chat_type: ChatType, messsage: UnifiedMessage):
    """
    function prototype for send new message
    this function should be implemented in driver, sync or async
    send should call set_ingress_message_id to register received message
    """
    pass
```

Or the synced version, if async not available:

```python
from Core.UMRType import UnifiedMessage
def send(self, to_chat: int, chat_type: ChatType, messsage: UnifiedMessage):
    """
    function prototype for send new message
    this function should be implemented in driver, sync or async
    send should call set_egress_message_id to register message
    """
    pass
```

### IsAdmin

```python
async def is_group_admin(self, chat_id: int, chat_type: ChatType, user_id: int) -> bool:
    """
    :return if the member is group admin
    """
    pass
```
### IsOwner

```python
async def is_group_owner(self, chat_id: int, chat_type: ChatType, user_id: int) -> bool:
    """
    :return if the member is group owner
    """
    if chat_type != ChatType.GROUP:
        return False
    if chat_id not in self.group_list:
        return False
    return self.group_list[chat_id][user_id]['role'] == 'owner'
```

------

These functions should be registered to driver's API lookup table, see any existing driver for example.

Driver must make sure that this function can be called directly from other events loop or threads.

## Inbound message
Driver should also implement the following handler, e.g. QQ:
Driver should call `set_ingress_message_id` to register received message

```python
async def handle_msg(context):
    message_type = context.get("message_type")
    chat_id = context.get(f'{message_type}_id')
    chat_type = self.chat_type_dict[message_type]

    unified_message_list = await self.dissemble_message(context)
    set_ingress_message_id(src_platform=self.name, src_chat_id=chat_id, src_chat_type=chat_type,
                           src_message_id=context.get('message_id'), user_id=context.get('user_id'))
    for message in unified_message_list:
        await self.receive(message)
    return {}
```

What is important about this code snippet is `await UMRDriver.receive(message)`. The driver should parse the income message
 to UnifiedMessage, and then call `UMRDriver.receive(message)`. This is an async function, and driver should use their own
  event loop to call this function.
  
## Calling driver

```python
from Core.UMRDriver import api_call
result = api_call(chat_attrs.from_platform, 'api name', *args, **kwargs)
```
