from bot_constant import FORWARD_LIST
import global_vars
from utils import get_forward_index, send_both_side, get_plugin_priority
from telegram.ext import MessageHandler, Filters
from telegram.ext.dispatcher import DispatcherHandlerStop
from command import command_listener
import telegram
import logging


logger = logging.getLogger("CTBPlugin." + __name__)
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


# add commands

# forward_index, tg_user=message.from_user, tg_group_id=tg_group_id, tg_message_id=message.id

@command_listener('drive mode on', 'drive', description='enable drive mode')
def drive_mode_on(forward_index: int,
                  tg_group_id: int=None,
                  tg_user: telegram.User=None,
                  tg_message_id: int=None,
                  tg_reply_to: telegram.Message=None,
                  qq_group_id: int=None,
                  qq_discuss_id: int=None,
                  qq_user: int=None):
    global_vars.DRIVE_MODE[forward_index] = True

    message = 'Status changed: 451'

    return send_both_side(forward_index,
                          message,
                          qq_group_id,
                          qq_discuss_id,
                          tg_group_id,
                          tg_message_id)


@command_listener('drive mode off', 'park', description='disable drive mode')
def drive_mode_off(forward_index: int,
                   tg_group_id: int=None,
                   tg_user: telegram.User=None,
                   tg_message_id: int=None,
                   tg_reply_to: telegram.Message=None,
                   qq_group_id: int=None,
                   qq_discuss_id: int=None,
                   qq_user: int=None):
    global_vars.DRIVE_MODE[forward_index] = False

    message = 'Status changed: 200'

    return send_both_side(forward_index,
                          message,
                          qq_group_id,
                          qq_discuss_id,
                          tg_group_id,
                          tg_message_id)
