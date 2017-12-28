from bot_constant import FORWARD_LIST
import global_vars
from utils import get_plugin_priority, get_forward_index, send_from_qq_to_tg, get_qq_name
import logging

logger = logging.getLogger("CTBPlugin." + __name__)
logger.debug(__name__ + " loading")


@global_vars.qq_bot.on_event(group=0)
def handle_all(context):

    logger.debug(context)

    # tg_message_id_list = send_from_qq_to_tg(forward_index, message=context['message'],
    #                                         qq_group_id=qq_group_id,
    #                                         qq_user=context['user_id'])
    #
    # # save message to database, using telegram message id as index
    # for msg_id in tg_message_id_list:
    #     global_vars.mdb.append_message(context.get('message_id'), msg_id, forward_index, context.get('user_id'))

    return ''


@global_vars.qq_bot.on_event('group_upload', group=get_plugin_priority(__name__))
def handle_group_upload(context):
    qq_group_id = context.get('group_id')
    user_id = context.get('user_id')
    file = context.get('file')
    logger.debug(context)
    forward_index = get_forward_index(qq_group_id=qq_group_id)

    qq_name = get_qq_name(user_id, forward_index)

    # tg_message_id_list = send_from_qq_to_tg(forward_index, message=context['message'],
    #                                         qq_group_id=qq_group_id,
    #                                         qq_user=context['user_id'])
    #
    # # save message to database, using telegram message id as index
    # for msg_id in tg_message_id_list:
    #     global_vars.mdb.append_message(context.get('message_id'), msg_id, forward_index, context.get('user_id'))

    return ''


@global_vars.qq_bot.on_event('group_admin', group=get_plugin_priority(__name__))
def handle_group_admin(context):
    qq_group_id = context.get('group_id')
    sub_type = context.get('sub_type')
    user_id = context.get('user_id')
    file = context.get('file')
    logger.debug(context)
    forward_index = get_forward_index(qq_group_id=qq_group_id)

    # tg_message_id_list = send_from_qq_to_tg(forward_index, message=context['message'],
    #                                         qq_group_id=qq_group_id,
    #                                         qq_user=context['user_id'])
    #
    # # save message to database, using telegram message id as index
    # for msg_id in tg_message_id_list:
    #     global_vars.mdb.append_message(context.get('message_id'), msg_id, forward_index, context.get('user_id'))

    return ''


@global_vars.qq_bot.on_event('group_decrease', group=get_plugin_priority(__name__))
def handle_group_decrease(context):
    qq_group_id = context.get('group_id')
    sub_type = context.get('sub_type')
    user_id = context.get('user_id')
    operator_id = context.get('operator_id')
    logger.debug(context)
    forward_index = get_forward_index(qq_group_id=qq_group_id)

    # tg_message_id_list = send_from_qq_to_tg(forward_index, message=context['message'],
    #                                         qq_group_id=qq_group_id,
    #                                         qq_user=context['user_id'])
    #
    # # save message to database, using telegram message id as index
    # for msg_id in tg_message_id_list:
    #     global_vars.mdb.append_message(context.get('message_id'), msg_id, forward_index, context.get('user_id'))

    return ''


@global_vars.qq_bot.on_event('group_increase', group=get_plugin_priority(__name__))
def handle_group_increase(context):
    qq_group_id = context.get('group_id')
    sub_type = context.get('sub_type')
    user_id = context.get('user_id')
    operator_id = context.get('operator_id')
    logger.debug(context)
    forward_index = get_forward_index(qq_group_id=qq_group_id)

    # tg_message_id_list = send_from_qq_to_tg(forward_index, message=context['message'],
    #                                         qq_group_id=qq_group_id,
    #                                         qq_user=context['user_id'])
    #
    # # save message to database, using telegram message id as index
    # for msg_id in tg_message_id_list:
    #     global_vars.mdb.append_message(context.get('message_id'), msg_id, forward_index, context.get('user_id'))

    return ''