import logging

import global_vars
import telegram
from main.command import command_listener
from telegram.ext import MessageHandler, Filters
from telegram.ext.dispatcher import DispatcherHandlerStop

from main.utils import get_forward_index, get_plugin_priority

logger = logging.getLogger("CTB.Plugin." + __name__)
logger.debug(__name__ + " loading")

# Commands are only available in group and discuss
# For private chat, another plugin will take over


def tg_command(bot: telegram.Bot,
               update: telegram.Update):
    if update.edited_message:  # handle edit
        message: telegram.Message = update.edited_message
    else:
        message: telegram.Message = update.message

    if not message.text.startswith('!!'):  # no command indicator
        return

    tg_group_id = message.chat_id  # telegram group id
    tg_reply_to = message.reply_to_message

    logger.debug('Command indicator met: ' + message.text)
    text = message.text[2:]

    for command in global_vars.command_list:  # process all non-forward commands
        if command.tg_only and (text == command.command or text == command.short_command):
            logger.debug(f'Matched Telegram only command: {command.command}')
            command.handler(tg_group_id=tg_group_id,
                            tg_user=message.from_user,
                            tg_message_id=message.message_id,
                            tg_reply_to=tg_reply_to)

            raise DispatcherHandlerStop()

    forward_index = get_forward_index(tg_group_id=tg_group_id)
    if forward_index == -1:
        logger.warning('Forward not found, please check your forward settings.')
        raise DispatcherHandlerStop()

    for command in global_vars.command_list:  # process all forward commands
        if not command.tg_only and not command.qq_only and (text == command.command or text == command.short_command):
            logger.debug(f'Matched general command: {command.command}')
            command.handler(forward_index,
                            tg_user=message.from_user,
                            tg_group_id=tg_group_id,
                            tg_message_id=message.message_id,
                            tg_reply_to=tg_reply_to)
            raise DispatcherHandlerStop()


global_vars.dp.add_handler(MessageHandler(Filters.text & Filters.group,
                                          tg_command),
                           get_plugin_priority(__name__))


# decorator 'message_type', 'message_type', ..., group=number
@global_vars.qq_bot.on_message('group', 'discuss', group=get_plugin_priority(__name__))
def qq_command(context):
    if len(context['message']) > 1:  # rich text can not be commands
        return {'pass': True}

    if context['message'][0]['type'] != 'text':  # commands can only be pure text
        return {'pass': True}

    qq_group_id = context.get('group_id')
    qq_discuss_id = context.get('discuss_id')
    text = context['message'][0]['data']['text']  # get message text

    if not text.startswith('!!'):  # no command indicator
        return {'pass': True}

    logger.debug('Command indicator met: ' + text)
    text = text[2:]

    for command in global_vars.command_list:  # process all non-forward commands
        if command.qq_only and (text == command.command or text == command.short_command):
            logger.debug(f'Matched QQ only command: {command.command}')
            return command.handler(qq_group_id,
                                   qq_discuss_id,
                                   int(context['user_id']))

    forward_index = get_forward_index(qq_group_id=qq_group_id,
                                      qq_discuss_id=qq_discuss_id)
    if forward_index == -1:
        logger.warning('Forward not found, please check your forward settings.')
        return ''

    for command in global_vars.command_list:  # process all forward commands
        if not command.tg_only and not command.qq_only and (text == command.command or text == command.short_command):
            logger.debug(f'Matched general command: {command.command}')
            return command.handler(forward_index,
                                   qq_group_id=qq_group_id,
                                   qq_discuss_id=qq_discuss_id,
                                   qq_user=int(context['user_id']))

    return {'pass': True}


@command_listener('show commands', 'cmd', qq_only=True, description='print all commands')
def command_qq_cmd(qq_group_id: int,
               qq_discuss_id:int,
               qq_user: int):
    result = '\n'
    for command in global_vars.command_list:
        if not command.tg_only:
            result += f'{command.command}({command.short_command}): \n  {command.description}\n\n'
    return {'reply': result}


@command_listener('show commands', 'cmd', tg_only=True, description='print all commands')
def command_tg_cmd(tg_group_id: int,
               tg_user: telegram.User,
               tg_message_id: int,
               tg_reply_to: telegram.Message):
    result = ''
    for command in global_vars.command_list:
        if not command.qq_only:
            result += f'<b>{command.command}</b>(<b>{command.short_command}</b>): \n  {command.description}\n\n'
    global_vars.tg_bot.sendMessage(chat_id=tg_group_id,
                                   text=result,
                                   reply_to_message_id=tg_message_id,
                                   parse_mode='HTML')


@command_listener('help', 'h', qq_only=True, description='print help')
def command_qq_h(qq_group_id: int,
               qq_discuss_id:int,
               qq_user: int):
    result = '''I'm a relay bot between qq and tg.
Please use "!!show commands" or "!!cmd" to show all commands.
'''
    return {'reply': result}


@command_listener('help', 'h', tg_only=True, description='print help')
def command_tg_h(tg_group_id: int,
               tg_user: telegram.User,
               tg_message_id: int,
               tg_reply_to: telegram.Message = None):
    result = '''I'm a relay bot between qq and tg.
Please use "!!show commands" or "!!cmd" to show all commands.
'''
    global_vars.tg_bot.sendMessage(chat_id=tg_group_id,
                                   text=result,
                                   reply_to_message_id=tg_message_id,
                                   parse_mode='HTML')
