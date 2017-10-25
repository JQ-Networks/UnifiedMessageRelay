import global_vars
from telegram.ext.dispatcher import DispatcherHandlerStop
from utils import get_forward_index
from telegram.ext import MessageHandler, Filters
from cqsdk import RcvdGroupMessage, SendGroupMessage
from command import command_listener
from telegram import Update, User

import re


def tg_command(bot, update: Update):
    tg_group_id = update.message.chat_id  # telegram group id

    for command in global_vars.command_list:  # process all non-forward commands
        if command.tg_only:
            if update.message.text == command.command:
                command.handler(tg_group_id, update.message.from_user)
                raise DispatcherHandlerStop()

    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    if forward_index == -1:
        raise DispatcherHandlerStop()

    for command in global_vars.command_list:  # process all forward commands
        if not command.tg_only and not command.qq_only:
            if update.message.text == command.command:
                command.handler(forward_index, tg_group_id, update.message.from_user, qq_group_id, 0)
                raise DispatcherHandlerStop()


global_vars.dp.add_handler(MessageHandler(Filters.text, tg_command), 0)  # priority 0


@global_vars.qq_bot.listener((RcvdGroupMessage, ), 0)  # priority 0
def qq_drive_mode(message):
    qq_group_id = int(message.group)
    text = message.text  # get message text
    text, _ = re.subn('&amp;', '&', text)  # restore characters
    text, _ = re.subn('&#91;', '[', text)
    text, _ = re.subn('&#93;', ']', text)
    text, _ = re.subn('&#44;', ',', text)

    for command in global_vars.command_list:  # process all non-forward commands
        if command.qq_only:
            if text == command.command:
                command.handler(qq_group_id, int(message.qq))
                return True

    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if forward_index == -1:
        return True

    for command in global_vars.command_list:  # process all forward commands
        if not command.tg_only and not command.qq_only:
            if text == command.command:
                command.handler(forward_index, tg_group_id, None, qq_group_id, int(message.qq))
                return True

    return False


@command_listener('[show commands]', qq_only=True, description='print all commands')
def drive_mode_on(qq_group_id: int, qq: int):
    result = ''
    for command in global_vars.command_list:
        result += command.command + ': ' + ('telegram command' if command.tg_only else ('qq command' if command.qq_only else '')) + '\n'
        if command.description:
            result += '  ' + command.description + '\n'
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=result))


@command_listener('[show commands]', tg_only=True, description='print all commands')
def drive_mode_on(tg_group_id: int, user: User):
    result = ''
    for command in global_vars.command_list:
        result += '<b>' + command.command + '</b>: ' + ('telegram command' if command.tg_only else ('qq command' if command.qq_only else '')) + '\n'
        if command.description:
            result += '  ' + command.description + '\n'
    global_vars.tg_bot.sendMessage(tg_group_id, result, parse_mode='HTML')
