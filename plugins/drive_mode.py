from bot_constant import FORWARD_LIST
import global_vars
from utils import get_forward_index
from telegram.ext import MessageHandler, Filters
from telegram.ext.dispatcher import DispatcherHandlerStop
from cqsdk import RcvdGroupMessage, SendGroupMessage
from command import command_listener

DRIVE_MODE = []

for forward in FORWARD_LIST:
    DRIVE_MODE.append(forward['Drive_mode'])


def tg_drive_mode(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    # if forward_index == -1:
    #     raise dispatcher.DispatcherHandlerStop()
    if DRIVE_MODE[forward_index]:
        raise DispatcherHandlerStop()


global_vars.dp.add_handler(MessageHandler(Filters.all, tg_drive_mode), 1)  # priority 1


@global_vars.qq_bot.listener((RcvdGroupMessage, ), 1)  # priority 1
def qq_drive_mode(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    # if forward_index == -1:
    #     return True
    if DRIVE_MODE[forward_index]:
        return True
    return False


# add commands

@command_listener('[drive mode on]')
def drive_mode_on(forward_index, tg_group_id, qq_group_id):
    DRIVE_MODE[forward_index] = True
    msg = 'Telegram向QQ转发消息已暂停'
    global_vars.tg_bot.sendMessage(tg_group_id, msg)
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))


@command_listener('[drive mode off]')
def drive_mode_on(forward_index, tg_group_id, qq_group_id):
    DRIVE_MODE[forward_index] = False
    msg = 'Telegram向QQ转发消息已重启'
    global_vars.tg_bot.sendMessage(tg_group_id, msg)
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))
