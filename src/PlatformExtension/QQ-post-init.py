from Core import CTBLogging
import asyncio
from Driver import QQ

logger = CTBLogging.getLogger('CTBPlugins.QQ-init')


async def update_name_list():
    try:
        groups = await QQ.bot.get_group_list()
        for group in groups:
            group_id = group['group_id']
            QQ.group_list[group_id] = dict()
            # see https://cqhttp.cc/docs/4.13/#/API?id=get_group_member_info-获取群成员信息
            group_members = await QQ.bot.get_group_member_list(group_id=group_id)
            for i in group_members:
                QQ.group_list[group_id][i['user_id']] = i

    except Exception as e:
        logger.error(e)
        logger.error('Update name list failed! Please restart the bot or try update name list later.')


asyncio.run_coroutine_threadsafe(update_name_list(), QQ.loop)
