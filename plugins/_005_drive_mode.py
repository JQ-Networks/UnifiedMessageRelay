from bot_constant import FORWARD_LIST
import global_vars
from utils import get_forward_index
from telegram.ext import MessageHandler, Filters, ConversationHandler, CommandHandler
from telegram.ext.dispatcher import DispatcherHandlerStop
from cqsdk import RcvdGroupMessage, SendGroupMessage
from command import command_listener
from pathlib import Path
import json

DRIVE_MODE = []

filter_list = {'keywords': [], 'channels': []}


def load_data():
    global filter_list
    json_file = Path('./plugins/conf/_006_water_meter_filter.json')
    if json_file.is_file():
        filter_list = json.load(open('./plugins/conf/_006_water_meter_filter.json', 'r'))


def save_data():
    global filter_list
    json.dump(filter_list, open('./plugins/conf/_006_water_meter_filter.json', 'w'), ensure_ascii=False, indent=4)


load_data()


for forward in FORWARD_LIST:
    DRIVE_MODE.append(forward['Drive_mode'])


def tg_drive_mode(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))

    if DRIVE_MODE[forward_index]:
        raise DispatcherHandlerStop()
    if update.message.forward_from_chat:
        if update.message.forward_from_chat.type == 'channel':
            if update.message.forward_from_chat.id in filter_list['channels']:
                drive_mode_on(forward_index, tg_group_id, update.message.from_user, qq_group_id, 0)
                raise DispatcherHandlerStop()

    for keyword in filter_list['keywords']:
        if update.message.caption:
            if keyword in update.message.caption:
                drive_mode_on(forward_index, tg_group_id, update.message.from_user, qq_group_id, 0)
                raise DispatcherHandlerStop()
        elif update.message.text:
            if keyword in update.message.text:
                drive_mode_on(forward_index, tg_group_id, update.message.from_user, qq_group_id, 0)
                raise DispatcherHandlerStop()


global_vars.dp.add_handler(MessageHandler(Filters.all, tg_drive_mode), 5)  # priority 5


@global_vars.qq_bot.listener((RcvdGroupMessage, ), 5)  # priority 5
def qq_drive_mode(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)

    if DRIVE_MODE[forward_index]:
        return True
    return False


# add commands

@command_listener('[drive mode on]', description='enable drive mode')
def drive_mode_on(forward_index, tg_group_id, tg_user, qq_group_id, qq):
    DRIVE_MODE[forward_index] = True
    msg = 'Telegram向QQ转发消息已暂停'
    global_vars.tg_bot.sendMessage(tg_group_id, msg)
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))


@command_listener('[drive mode off]', description='disable drive mode')
def drive_mode_off(forward_index, tg_group_id, tg_user, qq_group_id, qq):
    DRIVE_MODE[forward_index] = False
    msg = 'Telegram向QQ转发消息已重启'
    global_vars.tg_bot.sendMessage(tg_group_id, msg)
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))


def add_keyword(bot, update, args):
    if update.message.chat_id < 0:
        return
    if len(args) == 0:
        update.message.reply_text('Usage: /add_keyword keyword1 keyword2 ...')
        return
    for keyword in args:
        if keyword in filter_list['keywords']:
            update.message.reply_text('Keyword: "' + keyword + '" already in list')
            continue
        filter_list['keywords'].append(keyword)
    update.message.reply_text('Success!')
    save_data()

CHANNEL = range(1)


def begin_add_channel(bot, update):
    if update.message.chat_id < 0:
        return
    update.message.reply_text('Please forward me message from channels:')
    return CHANNEL


def add_channel(bot, update):
    if update.message.forward_from_chat:
        update.message.reply_text(update.message.forward_from_chat.type)
        if update.message.forward_from_chat.type == 'channel':
            if update.message.forward_from_chat.id not in filter_list['channels']:
                filter_list['channels'].append(update.message.forward_from_chat.id)
                save_data()
                update.message.reply_text('Okay, please send me another, or use /cancel to stop')
            else:
                update.message.reply_text('Already in list. Send me another or use /cancel to stop')
            return CHANNEL
    else:
        if update.message.text == '/cancel':
            update.message.reply_text('Done.')
            return ConversationHandler.END
        else:
            update.message.reply_text('Message type error. Please forward me a message from channel, or use /cancel to stop')
            return CHANNEL


def cancel_add_channel(bot, update):
    update.message.reply_text('Done.')
    return ConversationHandler.END


conv_handler = ConversationHandler(
        entry_points=[CommandHandler('begin_add_channel', begin_add_channel)],

        states={
            CHANNEL: [MessageHandler(Filters.all, add_channel)]
        },

        fallbacks=[CommandHandler('cancel', cancel_add_channel)]
    )


global_vars.dp.add_handler(conv_handler, group=0)
global_vars.dp.add_handler(CommandHandler('add_keyword', add_keyword, pass_args=True), group=0)
