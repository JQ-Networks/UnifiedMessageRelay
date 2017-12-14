from telegram.ext import MessageHandler, Filters, ConversationHandler, CommandHandler
import global_vars
import json
from pathlib import Path
from utils import get_plugin_priority
import logging
import telegram
from telegram import InlineKeyboardButton

logger = logging.getLogger("CTBPlugin." + __name__)
logger.debug(__name__ + " loading")

global_vars.create_variable('group_invites', [])  # pending other group invites
global_vars.create_variable('group_requests', [])  # pending new group member admissions

# TODO group invites


@global_vars.qq_bot.on_request('group', group=get_plugin_priority(__name__))
def handle_group_tequest(context):
    """
    handle qq group add/invite requests with reply markup
    :param context:
    post_type	    string	"request"	    上报类型
    request_type	string	"group"	        请求类型
    sub_type	    string	"add"、"invite"	请求子类型，分别表示加群请求、邀请登录号入群
    group_id	    number	-	            群号
    user_id	        number	-	            发送请求的 QQ 号
    message	        string	-	            验证信息
    flag	        string	-	            请求 flag，在调用处理请求的 API 时需要传入
    :return:
    """
    if context.get('sub_type') == 'add':  # others want to join this group
        global_vars.group_requests.append(context)
        global_vars.tg_bot.sendMessage(chat_id=tg_group_id, text=message, reply_to_message_id=tg_message_id)
    else:
        pass

    return ''

