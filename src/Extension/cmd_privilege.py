from typing import List
from Core.UMRType import ChatAttribute, Privilege
from Core.UMRCommand import register_command, quick_reply


@register_command(cmd='owner', description='only owner can use this command', privilege=Privilege.GROUP_OWNER)
async def command(chat_attrs: ChatAttribute, args: List):
    """
    Prototype of command
    :param chat_attrs:
    :param args:
    :return:
    """
    if args:  # args should be empty
        return

    await quick_reply(chat_attrs, 'You are owner')


@register_command(cmd='admin', description='only admin can use this command', privilege=Privilege.GROUP_ADMIN)
async def command(chat_attrs: ChatAttribute, args: List):
    """
    Prototype of command
    :param chat_attrs:
    :param args:
    :return:
    """
    if args:  # args should be empty
        return

    await quick_reply(chat_attrs, 'You are admin')