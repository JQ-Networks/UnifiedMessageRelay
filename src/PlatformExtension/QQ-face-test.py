from typing import List
from Core import UMRLogging
from Core.UMRType import ChatAttribute
from aiocqhttp import MessageSegment
from Core.UMRDriver import driver_lookup_table
from Driver import QQ

logger = UMRLogging.getLogger('Plugin.QQ-recall')


# @register_command(cmd=['face'], description='test QQ face')
async def command(chat_attrs: ChatAttribute, args: List):
    if not args:
        return False
    if len(args) != 2:
        return False

    dst_driver_name = args[0]
    dst_chat_id = int(args[1])

    dst_driver = driver_lookup_table.get(dst_driver_name)
    if not dst_driver:
        return

    assert isinstance(dst_driver, QQ.QQDriver)

    context = dict()
    _group_type = dst_driver.chat_type.get(dst_chat_id, 'group')
    context['message_type'] = _group_type
    context['message'] = list()
    if _group_type == 'private':
        context['user_id'] = dst_chat_id
    else:
        context[f'{_group_type}_id'] = abs(dst_chat_id)

    for i in range(256):
        context['message'].append(MessageSegment.text(f'Emoji {i}: '))
        context['message'].append(MessageSegment.face(i))
        context['message'].append(MessageSegment.text('\n'))

    await dst_driver.bot.send(context, context['message'])
