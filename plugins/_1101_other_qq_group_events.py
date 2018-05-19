import logging

import global_vars
from bot_constant import FORWARD_LIST, QQ_BOT_ID

from main.utils import get_plugin_priority, get_forward_index, get_qq_name_encoded

logger = logging.getLogger("CTB." + __name__)
logger.debug(__name__ + " loading")


@global_vars.qq_bot.on_event('group_upload', group=get_plugin_priority(__name__))
def handle_group_upload(context):
    qq_group_id = context.get('group_id')
    user_id = context.get('user_id')
    file = context.get('file')

    logger.debug(context)

    forward_index = get_forward_index(qq_group_id=qq_group_id)
    if forward_index == -1:
        return ''

    qq_name = get_qq_name_encoded(user_id, forward_index)

    result = f'<b>{qq_name}</b> sent a 📎group file: {file["name"]}. Please view it on QQ.'
    global_vars.tg_bot.sendMessage(chat_id=FORWARD_LIST[forward_index]['TG'],
                                   text=result,
                                   parse_mode='HTML')

    return ''


@global_vars.qq_bot.on_event('group_admin', group=get_plugin_priority(__name__))
def handle_group_admin(context):
    qq_group_id = context.get('group_id')
    sub_type = context.get('sub_type')
    user_id = context.get('user_id')
    logger.debug(context)

    forward_index = get_forward_index(qq_group_id=qq_group_id)
    if forward_index == -1:
        return ''

    qq_name = get_qq_name_encoded(user_id, forward_index)

    if sub_type == 'set':
        verb = 'promoted to admin.'
    else:
        verb = 'demoted to member.'

    result = f'{qq_name} was {verb}'
    global_vars.tg_bot.sendMessage(chat_id=FORWARD_LIST[forward_index]['TG'],
                                   text=result,
                                   parse_mode='HTML')

    return ''


@global_vars.qq_bot.on_event('group_decrease', group=get_plugin_priority(__name__))
def handle_group_decrease(context):
    qq_group_id = context.get('group_id')
    sub_type = context.get('sub_type')
    user_id = context.get('user_id')
    operator_id = context.get('operator_id')
    logger.debug(context)

    forward_index = get_forward_index(qq_group_id=qq_group_id)
    if forward_index == -1:
        return ''

    if sub_type == 'leave':
        if str(user_id) == str(QQ_BOT_ID):
            result = 'Your bot left the group.'
        else:
            qq_name = get_qq_name_encoded(user_id, forward_index)
            result = f'{qq_name} left the group.'
    elif sub_type == 'kick':
        qq_name = get_qq_name_encoded(user_id, forward_index)
        operator_name = get_qq_name_encoded(operator_id, forward_index)
        result = f'{qq_name} was kicked by {operator_name}.'
    else:
        operator_name = get_qq_name_encoded(operator_id, forward_index)
        result = f'Your bot was kicked by {operator_name}.'

    global_vars.tg_bot.sendMessage(chat_id=FORWARD_LIST[forward_index]['TG'],
                                   text=result,
                                   parse_mode='HTML')
    return ''


@global_vars.qq_bot.on_event('group_increase', group=get_plugin_priority(__name__))
def handle_group_increase(context):
    qq_group_id = context.get('group_id')
    sub_type = context.get('sub_type')
    user_id = context.get('user_id')
    operator_id = context.get('operator_id')
    logger.debug(context)

    forward_index = get_forward_index(qq_group_id=qq_group_id)
    if forward_index == -1:
        return ''

    # reload namelist because there is a new member here
    global_vars.reload_qq_namelist(forward_index)

    qq_name = get_qq_name_encoded(user_id, forward_index)
    operator_name = get_qq_name_encoded(operator_id, forward_index)

    if sub_type == 'approve':
        result = f'{qq_name} approved by {operator_name} joined the group.'
    else:
        result = f'{qq_name} invited by {operator_name} joined the group.'

    global_vars.tg_bot.sendMessage(chat_id=FORWARD_LIST[forward_index]['TG'],
                                   text=result,
                                   parse_mode='HTML')

    return ''
