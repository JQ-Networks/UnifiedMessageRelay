from typing import List, Dict
import asyncio
from Core import UMRLogging
from Core.UMRCommand import register_command, quick_reply
from Core.UMRType import ChatAttribute, UnifiedMessage, MessageEntity, GroupID, DestinationMessageID, SendAction
from Core.UMRMessageRelation import get_relation_dict
from Driver import QQ
from Core.UMRDriver import driver_lookup_table

logger = UMRLogging.get_logger('Plugin.QQ-recall')


@register_command(cmd=['del', 'recall'], description='recall all related qq message sent by forward bot')
async def command(chat_attrs: ChatAttribute, args: List):
    if chat_attrs.reply_to:
        message_relation = get_relation_dict(src_platform=chat_attrs.platform,
                                             src_chat_id=chat_attrs.chat_id,
                                             src_chat_type=chat_attrs.chat_type,
                                             message_id=chat_attrs.reply_to.message_id)

        dst_drivers = {k: v for k, v in driver_lookup_table.items() if isinstance(v, QQ.QQDriver)}

        if message_relation:
            filtered_message_ids: Dict[GroupID, DestinationMessageID] = {k: w for k, w in message_relation.items() if
                                                                         k.platform in dst_drivers}
            if filtered_message_ids:
                for key, value in filtered_message_ids.items():
                    asyncio.run_coroutine_threadsafe(dst_drivers[value.platform].bot.delete_msg(message_id=value.message_id), dst_drivers[value.platform].loop)
                reply_text = 'Message recalled'
            else:
                reply_text = 'No related QQ message found'
        else:
            reply_text = 'Message not recallable'
    else:
        reply_text = 'No message specified, please reply to a message'

    await quick_reply(chat_attrs, reply_text)
