import global_vars
from pathlib import Path
import json
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.ext import MessageHandler, Filters, ConversationHandler, CommandHandler
import telegram
from utils import get_forward_index, get_plugin_priority

global_vars.create_variable('filter_list', {'keywords': [], 'channels': []})


def load_data():
    json_file = Path('./plugins/conf/' + __name__ + '.json')
    if json_file.is_file():
        global_vars.filter_list = json.load(open('./plugins/conf/' + __name__ + '.json', 'r'))


def save_data():
    json.dump(global_vars.filter_list, open('./plugins/conf/' + __name__ + '.json', 'w'),
              ensure_ascii=False, indent=4)


load_data()


def tg_water_meter(bot, update):
    if update.message:
        message: telegram.Message = update.message
    else:
        message: telegram.Message = update.edited_message

    tg_group_id = message.chat_id  # telegram group id
    forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    if message.forward_from_chat:
        if message.forward_from_chat.type == 'channel':
            if update.message.forward_from_chat.id in global_vars.filter_list['channels']:
                global_vars.drive_mode_on(forward_index, tg_user=message.from_user, tg_group_id=tg_group_id,
                                          tg_message_id=message.id)
                raise DispatcherHandlerStop()

    for keyword in global_vars.filter_list['keywords']:
        if message.caption:
            if keyword in message.caption:
                global_vars.drive_mode_on(forward_index, tg_user=message.from_user, tg_group_id=tg_group_id,
                                          tg_message_id=message.id)
                raise DispatcherHandlerStop()
        elif message.text:
            if keyword in message.text:
                global_vars.drive_mode_on(forward_index, tg_user=message.from_user, tg_group_id=tg_group_id,
                                          tg_message_id=message.id)
                raise DispatcherHandlerStop()


global_vars.dp.add_handler(MessageHandler(Filters.all, tg_water_meter), get_plugin_priority(__name__))


# TODO private chat plugin

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
    update.message.reply_text('Done.')
    save_data()

CHANNEL = range(1)


def begin_add_channel(bot, update):
    if update.message.chat_id < 0:
        return
    update.message.reply_text('Please forward me message from channels:')
    return CHANNEL


def add_channel(bot, update):
    if update.message.forward_from_chat:
        if update.message.forward_from_chat.type == 'channel':
            print(update.message.forward_from_chat.type)
            print(update.message.forward_from_chat.id)
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
