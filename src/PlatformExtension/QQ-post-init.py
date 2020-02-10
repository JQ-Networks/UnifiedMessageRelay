import asyncio
from typing import List
from Core import UMRLogging
from Driver import QQ
from Core.UMRType import ChatAttribute, UnifiedMessage, MessageEntity
from Core.UMRCommand import register_command, quick_reply
from Core.UMRDriver import driver_lookup_table

logger = UMRLogging.getLogger('UMRPlugins.QQ-init')


async def update_name_list(QQ):
    try:
        groups = await QQ.bot.get_group_list()
        for group in groups:
            group_id = group['group_id']
            QQ.group_list[-group_id] = dict()
            # see https://cqhttp.cc/docs/4.13/#/API?id=get_group_member_info-获取群成员信息
            group_members = await QQ.bot.get_group_member_list(group_id=group_id)
            for i in group_members:
                QQ.group_list[-group_id][i['user_id']] = i

    except Exception as e:
        logger.error(e)
        logger.error('Update name list failed! Please restart the bot or try update name list later.')

    logger.info('QQ name list initialized')

# while True:
#     if hasattr(QQ, 'loop'):
#         break
#     else:
#         sleep(1)


def do_update():
    for k, v in driver_lookup_table.items():
        if isinstance(v, QQ.QQDriver):
            asyncio.run_coroutine_threadsafe(update_name_list(v), v.loop)


@register_command(cmd='name', description='update QQ nicknames')
async def reload_name_list(chat_attrs: ChatAttribute, args: List):
    if args:  # args should be empty
        return

    do_update()
    await quick_reply(chat_attrs, 'QQ nicknames updated')

do_update()