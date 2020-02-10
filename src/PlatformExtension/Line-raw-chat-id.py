from typing import List
from Core import UMRLogging
from Core.UMRType import ChatAttribute
from Core.UMRDriver import driver_lookup_table
from Driver import Line
from Core.UMRCommand import quick_reply, register_command

logger = UMRLogging.getLogger('Plugin.Line-raw-chat-id')


@register_command(cmd=['raw_id'], description='get line chat id', platform=['Line'])
async def command(chat_attrs: ChatAttribute, args: List):
    if args:
        return False

    dst_driver = driver_lookup_table.get(chat_attrs.platform)
    if not dst_driver:
        return

    assert isinstance(dst_driver, Line.main.LineDriver)

    raw_chat_id = dst_driver.chat_id_to_raw(chat_attrs.chat_id)

    await quick_reply(chat_attrs, f'Chat id: {raw_chat_id}')
