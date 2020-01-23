import logging
from Driver import QQ

logger = logging.getLogger('CTBPlugins.QQ-init')


def update_name_list():
    # try:
    groups = QQ.bot.get_group_list()
    for group in groups:
        group_id = group['group_id']
        QQ.group_list[group_id] = dict()
        # see https://cqhttp.cc/docs/4.13/#/API?id=get_group_member_info-获取群成员信息
        group_members = QQ.bot.get_group_member_list(group_id=group_id)
        for i in group_members:
            QQ.group_list[group_id][i['user_id']] = i  #
    #
    # except Exception as e:
    #     logger.error(e)
    #     logger.error('Update name list failed! Please restart the bot or try update name list later.')


update_name_list()
