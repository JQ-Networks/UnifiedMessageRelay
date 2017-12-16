from telegram.ext import MessageHandler, Filters, ConversationHandler, CommandHandler
import global_vars
import json
from pathlib import Path
from utils import get_plugin_priority
import logging
import telegram

logger = logging.getLogger("CTBPlugin." + __name__)
logger.debug(__name__ + " loading")


global_vars.create_variable('admin_list', {'QQ': [], 'TG': []})


def load_data():
    logger.debug("Begin loading admin list")
    json_file = Path('./plugins/conf/' + __name__ + '.json')
    if json_file.is_file():
        global_vars.admin_list = json.load(open('./plugins/conf/' + __name__ + '.json', 'r'))
        logger.debug("Admin list loaded")


def save_data():
    json.dump(global_vars.admin_list, open('./plugins/conf/' + __name__ + '.json', 'w'),
              ensure_ascii=False, indent=4)


load_data()


def start(bot: telegram.Bot,
          update: telegram.Update):
    update.message.reply_text('This is a QQ <-> Telegram Relay bot, '
                              'source code is available on [Github](https://github.com/jqqqqqqqqqq/coolq-telegram-bot)'
                              , parse_mode='Markdown')
    if len(global_vars.admin_list['TG']) == 0:  # no admin
        global_vars.admin_list['TG'].append(update.message.from_user.id)
        save_data()
        update.message.reply_text("You've been promoted to admin")


def add_admin(bot: telegram.Bot,
              update: telegram.Update,
              args: list):
    if len(global_vars.admin_list['TG']) == 0:  # no admin
        return

    # only bot maintainer can access, temporary solution
    if update.message.from_user.id != global_vars.admin_list['TG'][0]:
        return

    if len(args) != 2:
        update.message.reply_text('Usage: /add_admin [qq|tg] [qq_id|tg_id]')
        return

    try:
        qq_or_tg_id = int(args[1])
    except ValueError as e:
        update.message.reply_text(e)
        return

    if args[0] == 'qq':
        if qq_or_tg_id in global_vars.admin_list['QQ']:
            update.message.reply_text(str(qq_or_tg_id) + ' already in list', reply_to_message_id=update.message.id)
        else:
            global_vars.admin_list['QQ'].append(qq_or_tg_id)
            update.message.reply_text(str(qq_or_tg_id) + ' added', reply_to_message_id=update.message.id)
    elif args[0] == 'tg':
        if qq_or_tg_id in global_vars.admin_list['TG']:
            update.message.reply_text(str(qq_or_tg_id) + ' already in list', reply_to_message_id=update.message.id)
        else:
            global_vars.admin_list['TG'].append(qq_or_tg_id)
            update.message.reply_text(str(qq_or_tg_id) + ' added', reply_to_message_id=update.message.id)
    else:
        update.message.reply_text('Usage: /add_admin [qq|tg] [qq_id|tg_id]')
        return

    save_data()

global_vars.dp.add_handler(CommandHandler(command='start',
                                          callback=start,
                                          filters=Filters.private),
                           group=get_plugin_priority(__name__))
global_vars.dp.add_handler(CommandHandler(command='add_admin',
                                          callback=add_admin,
                                          filters=Filters.private,
                                          pass_args=True),
                           group=get_plugin_priority(__name__))

logger.debug(__name__ + " loaded")
