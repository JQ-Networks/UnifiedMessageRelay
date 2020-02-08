from typing import List, Dict
import asyncio
from Core import UMRLogging
from Core.UMRCommand import register_command, quick_reply
from Core.UMRType import ChatAttribute, UnifiedMessage, MessageEntity, GroupID, DestinationMessageID, SendAction
from Core.UMRMessageRelation import get_relation_dict
from Driver.QQ import bot, loop, chat_type
from aiocqhttp import MessageSegment

logger = UMRLogging.getLogger('Plugin.QQ-recall')


# @register_command(cmd=['face'], description='test QQ face')
async def command(chat_attrs: ChatAttribute, args: List):
    if not args:
        return False

    dst_chat_id = int(args[0])

    context = dict()
    _group_type = chat_type.get(dst_chat_id, 'group')
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

    await bot.send(context, context['message'])
