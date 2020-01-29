from typing import List
from Core.UMRType import ChatAttribute
from Core.UMRCommand import register_command, quick_reply


@register_command(cmd='id', platform='Telegram', description='get Telegram group id')
async def command(chat_attrs: ChatAttribute, args: List):
    """
    Prototype of command
    :param chat_attrs:
    :param args:
    :return:
    """
    if args:  # args should be empty
        return

    await quick_reply(chat_attrs, 'chat_id: ' + str(chat_attrs.chat_id))
