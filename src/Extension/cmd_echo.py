from typing import List
from Core.UMRType import ChatAttribute
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
