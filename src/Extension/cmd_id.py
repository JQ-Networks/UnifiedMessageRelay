from typing import List
from asyncio import iscoroutinefunction
from Core.CTBType import ForwardAttributes, UnifiedMessage, MessageEntity
from Core.CTBCommand import register_command
from Core.CTBDriver import api_lookup


@register_command(cmd='id', platform='Telegram', description='get Telegram group id')
async def command(forward_attrs: ForwardAttributes, args: List):
    """
    Prototype of command
    :param forward_attrs:
    :param args:
    :return:
    """
    if args:  # args should be empty
        return

    send = api_lookup(forward_attrs.from_platform, 'send')
    if not send:
        return
    message = UnifiedMessage()
    message.message.append(MessageEntity(text='chat_id: ' + str(forward_attrs.from_chat)))
    if iscoroutinefunction(send):
        await send(forward_attrs.from_chat, message)
    else:
        send(forward_attrs.from_chat, message)
