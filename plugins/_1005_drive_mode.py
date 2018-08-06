import logging

import global_vars
import telegram
from bot_constant import FORWARD_LIST
from main.command import command_listener
from telegram.ext import MessageHandler, Filters
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram import TelegramError

from main.utils import get_forward_index, send_both_side, get_plugin_priority, recall_message

logger = logging.getLogger("CTB." + __name__)
logger.debug(__name__ + " loading")

global_vars.create_variable('DRIVE_MODE', [])

for forward in FORWARD_LIST:  # initialize drive mode list
    global_vars.DRIVE_MODE.append(forward['DRIVE_MODE'])


def tg_drive_mode(bot: telegram.Bot,
                  update: telegram.Update):
    """
    if update.message:
        message: telegram.Message = update.message
    else:
        message: telegram.Message = update.edited_message
    """
    message: telegram.Message = update.effective_message
    edited = (bool(getattr(update, "edited_message", None)) or bool(getattr(update, "edited_channel_post", None)))

    tg_group_id = message.chat_id  # telegram group id
    forward_index = get_forward_index(tg_group_id=int(tg_group_id))

    if edited:
        recall_message(forward_index, message)

    # don't forward this message
    if (message.caption and message.caption.startswith('//')) or (
            message.reply_to_message and message.reply_to_message.caption and message.reply_to_message.caption.startswith(
            '//')) or (
            message.reply_to_message and message.reply_to_message.text and message.reply_to_message.text.startswith(
            '//')):
        logger.debug('Message ignored: matched comment pattern')
        raise DispatcherHandlerStop()

    # prevent message leak
    if forward_index == -1:
        raise DispatcherHandlerStop()

    if global_vars.DRIVE_MODE[forward_index]:  # normal block
        logger.debug('Telegram message ignored: drive mode is on')
        raise DispatcherHandlerStop()


global_vars.dp.add_handler(MessageHandler(Filters.all, tg_drive_mode, edited_updates=True),
                           get_plugin_priority(__name__))


@global_vars.qq_bot.on_message('group', 'discuss', group=get_plugin_priority(__name__))
def qq_drive_mode(context: dict):
    qq_group_id = context.get('group_id')
    qq_discuss_id = context.get('discuss_id')

    forward_index = get_forward_index(qq_group_id=qq_group_id,
                                      qq_discuss_id=qq_discuss_id)

    # prevent message leak
    if forward_index == -1:
        return ''

    if global_vars.DRIVE_MODE[forward_index]:  # normal block
        return ''
    return {'pass': True}


def drive_mode(forward_index: int, mode: bool) -> str:
    """
    set drive mode
    :param forward_index: forward index
    :param mode: drive mode to be set
    :return: Message: str
    """
    current = global_vars.DRIVE_MODE[forward_index]
    tg_group = FORWARD_LIST[forward_index]['TG']
    tg_group_title: str = global_vars.tg_bot.get_chat(tg_group).title
    if mode:
        if '(🚝)' not in tg_group_title:
            tg_group_title = '(🚝)' + tg_group_title
            try:
                global_vars.tg_bot.setChatTitle(tg_group, tg_group_title)
            except TelegramError as e:
                logger.debug(e.message)
        if current:
            msg = 'Status: 451'
        else:
            msg = 'Status changed: 451'
    else:
        if '(🚝)' in tg_group_title:
            tg_group_title = tg_group_title.replace('(🚝)', '').strip()
            if len(tg_group_title) == 0:
                tg_group_title = "WTF, what happened to the title"
            try:
                global_vars.tg_bot.setChatTitle(tg_group, tg_group_title)
            except TelegramError as e:
                logger.debug(e.message)
        if not current:
            msg = 'Status: 200'
        else:
            msg = 'Status changed: 200'
    global_vars.DRIVE_MODE[forward_index] = mode
    return msg


# add commands

# forward_index, tg_user=message.from_user, tg_group_id=tg_group_id, tg_message_id=message.id

@command_listener('drive mode on', 'drive', description='enable drive mode')
def drive_mode_on(forward_index: int,
                  tg_group_id: int = None,
                  tg_user: telegram.User = None,
                  tg_message_id: int = None,
                  tg_reply_to: telegram.Message = None,
                  qq_group_id: int = None,
                  qq_discuss_id: int = None,
                  qq_user: int = None):
    message = drive_mode(forward_index, True)

    return send_both_side(forward_index,
                          message,
                          qq_group_id,
                          qq_discuss_id,
                          tg_group_id,
                          tg_message_id)


@command_listener('drive mode off', 'park', description='disable drive mode')
def drive_mode_off(forward_index: int,
                   tg_group_id: int = None,
                   tg_user: telegram.User = None,
                   tg_message_id: int = None,
                   tg_reply_to: telegram.Message = None,
                   qq_group_id: int = None,
                   qq_discuss_id: int = None,
                   qq_user: int = None):
    message = drive_mode(forward_index, False)

    return send_both_side(forward_index,
                          message,
                          qq_group_id,
                          qq_discuss_id,
                          tg_group_id,
                          tg_message_id)
