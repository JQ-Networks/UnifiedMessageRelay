from bot_constant import FORWARD_LIST
import global_vars
from utils import get_forward_index, send_all_except_current, get_plugin_priority
from telegram.ext import MessageHandler, Filters, ConversationHandler, CommandHandler
from telegram.ext.dispatcher import DispatcherHandlerStop
from command import command_listener
from log_calls import log_calls

import telegram


global_vars.create_variable('DRIVE_MODE', [])


for forward in FORWARD_LIST:
    global_vars.DRIVE_MODE.append(forward['Drive_mode'])


@log_calls()
def tg_drive_mode(bot, update):
    if update.message:
        message: telegram.Message = update.message
    else:
        message: telegram.Message = update.edited_message

    tg_group_id = message.chat_id  # telegram group id
    forward_index = get_forward_index(tg_group_id=int(tg_group_id))

    if global_vars.DRIVE_MODE[forward_index]:  # normal block
        raise DispatcherHandlerStop()


global_vars.dp.add_handler(MessageHandler(Filters.all, tg_drive_mode), get_plugin_priority(__name__))


@global_vars.qq_bot.on_message('group', 'discuss', group=get_plugin_priority(__name__))
@log_calls()
def qq_drive_mode(context: dict):
    qq_group_id = context.get('group_id')
    qq_discuss_id = context.get('discuss_id')

    forward_index = get_forward_index(qq_group_id=qq_group_id, qq_discuss_id=qq_discuss_id)

    if global_vars.DRIVE_MODE[forward_index]:
        return ''
    return {'pass': True}


# add commands

# forward_index, tg_user=message.from_user, tg_group_id=tg_group_id, tg_message_id=message.id

@log_calls()
@command_listener('drive mode on', 'dmon', description='enable drive mode')
def drive_mode_on(forward_index: int, tg_group_id: int=None, tg_user: telegram.User=None,
                  tg_message_id: int=None, qq_group_id: int=None, qq_discuss_id: int=None, qq_user: int=None):
    global_vars.DRIVE_MODE[forward_index] = True

    message = 'Status changed: 451'

    if tg_group_id:
        send_all_except_current(forward_index, message, tg_group_id=tg_group_id)
        global_vars.tg_bot.sendMessage(text=message, reply_to_message_id=tg_message_id)
    elif qq_group_id:
        send_all_except_current(forward_index, message, qq_group_id=qq_group_id)
        return {'reply': message}
    else:
        send_all_except_current(forward_index, message, qq_discuss_id=qq_discuss_id)
        return {'reply': message}


@command_listener('drive mode off', 'dmoff', description='disable drive mode')
def drive_mode_off(forward_index: int, tg_group_id: int=None, tg_user: telegram.User=None,
                   tg_message_id: int=None, qq_group_id: int=None, qq_discuss_id: int=None, qq_user: int=None):
    global_vars.DRIVE_MODE[forward_index] = False

    message = 'Status changed: 200'

    if tg_group_id:
        send_all_except_current(forward_index, message, tg_group_id=tg_group_id)
        global_vars.tg_bot.sendMessage(text=message, reply_to_message_id=tg_message_id)
    elif qq_group_id:
        send_all_except_current(forward_index, message, qq_group_id=qq_group_id)
        return {'reply': message}
    else:
        send_all_except_current(forward_index, message, qq_discuss_id=qq_discuss_id)
        return {'reply': message}
