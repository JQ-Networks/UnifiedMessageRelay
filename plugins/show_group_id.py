import global_vars
from main.command import command_listener
import telegram
import logging
from telegram.ext import Filters, CommandHandler
from bot_constant import FORWARD_LIST
logger = logging.getLogger("CTB.Plugin." + __name__)

logger.debug(__name__ + " loading")


@command_listener('show group id', 'id', tg_only=True, description='show current telegram group id')
def show_tg_group_id(tg_group_id: int,
                     tg_user: telegram.User,
                     tg_message_id: int,
                     tg_reply_to: telegram.Message):
    msg = 'Telegram group id is: ' + str(tg_group_id)
    global_vars.tg_bot.sendMessage(chat_id=tg_group_id,
                                   text=msg)


@command_listener('show group id', 'id', qq_only=True, description='show current QQ group id')
def show_qq_group_id(qq_group_id: int,
                     qq_discuss_id: int,
                     qq_user: int):
    if qq_group_id:
        msg = 'QQ group id is: ' + str(qq_group_id)
        return {'reply': msg}
    else:
        msg = 'QQ discuss id is: ' + str(qq_discuss_id)
        return {'reply': msg}
def get_connected_groups(bot: telegram.Bot,
                         update: telegram.Update,
                         args: list):
    if update.message.from_user.id != global_vars.admin_list['TG'][0]:
        return
    s = ""
    for forward in FORWARD_LIST:
        s += "QQ: `%d`, TG: `%d`\n"%(forward['QQ'], forward['TG'])
    update.message.reply_markdown(text=s)
global_vars.dp.add_handler(CommandHandler(command='get_connected_groups',
                                          callback=get_connected_groups,
                                          filters=Filters.private,
                                          pass_args=True))
