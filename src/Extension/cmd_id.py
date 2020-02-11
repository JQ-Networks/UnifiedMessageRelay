from typing import List
from Core.UMRType import ChatAttribute
from Core.UMRCommand import register_command, quick_reply
from Core.UMRMessageRelation import get_message_id


@register_command(cmd='id', description='get group id')
async def command(chat_attrs: ChatAttribute, args: List):
    """
    Prototype of command
    :param chat_attrs:
    :param args:
    :return:
    """
    if args:  # args should be empty
        return

    if chat_attrs.reply_to:
        source_message = get_message_id(src_platform=chat_attrs.platform,
                                        src_chat_id=chat_attrs.chat_id,
                                        src_chat_type=chat_attrs.chat_type,
                                        src_message_id=chat_attrs.reply_to.message_id,
                                        dst_platform=chat_attrs.platform,
                                        dst_chat_id=chat_attrs.chat_id,
                                        dst_chat_type=chat_attrs.chat_type)
        if source_message.source:
            await quick_reply(chat_attrs, 'src_chat_type:' + str(source_message.source.chat_type) + '\nsrc_chat_id: ' + str(source_message.source.chat_id))
        else:
            await quick_reply(chat_attrs, 'chat_id: ' + str(chat_attrs.chat_id))
    else:
        await quick_reply(chat_attrs, 'chat_id: ' + str(chat_attrs.chat_id))
