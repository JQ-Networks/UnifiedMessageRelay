import logging

import global_vars
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

from main.utils import get_plugin_priority, get_full_user_name

# rely on _000_admins

logger = logging.getLogger("CTBPlugin." + __name__)
logger.debug(__name__ + " loading")

global_vars.create_variable('group_requests', {})  # pending admissions


@global_vars.qq_bot.on_request('group', group=get_plugin_priority(__name__))
def event_group_request(context):
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
    logger.debug(context)
    group_id = context.get('group_id')
    group_list = global_vars.qq_bot.get_group_list()
    group_name = str(group_id)
    for group in group_list:  # find group name
        if group['group_id'] == group_id:
            group_name = group['group_name']
            break

    sub_type = context.get('sub_type')
    user_id = context.get('user_id')

    """
    user_id	number	QQ 号
    nickname	string	昵称
    sex	string	性别，male 或 female 或 unknown
    age	number	年龄
    """

    user_name = global_vars.qq_bot.get_stranger_info(user_id=user_id)['nickname']
    qq_message = context.get('message')
    if qq_message:
        qq_message = '\n 验证消息：' + qq_message[0]['data']['text']

    if sub_type == 'add':  # others want to join this group
        message = user_name + " 想申请加入 " + group_name + '\n 验证消息：' + qq_message
    else:
        message = user_name + " 邀请 Bot 加入 " + group_name + qq_message

    accept_token = context.get('flag')

    decline_token = '!!' + accept_token
    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("Accept", callback_data=accept_token),
        InlineKeyboardButton("Decline", callback_data=decline_token),
    ]])

    message_id_list = list()
    for admin in global_vars.admin_list['TG']:
        message: telegram.Message = global_vars.tg_bot.sendMessage(chat_id=admin,
                                                                   text=message,
                                                                   reply_markup=reply_markup)
        message_id_list.append(message.message_id)

    saved_token = {
        'type': sub_type,
        'message_id_list': message_id_list
    }

    global_vars.group_requests[accept_token] = saved_token

    return ''


def group_request_callback(bot: telegram.Bot,
                           update: telegram.Update):
    query: telegram.CallbackQuery = update.callback_query
    user: telegram.User = query.from_user
    chat_id = user.id
    token = query.data

    user_name = get_full_user_name(user)

    if token.startswith('!!'):  # decline
        token = token[2:]
        if token not in global_vars.group_requests:
            return
        global_vars.qq_bot.set_group_add_request(flag=token,
                                                 type=global_vars.group_requests[token]['type'],
                                                 approve=False)
        for message_id in global_vars.group_requests[token]['message_id_list']:
            edited_message = {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': query.message.text + '\n' + user_name + 'declined'
            }
            bot.editMessageText(**edited_message)
    else:
        if token not in global_vars.group_requests:
            return
        global_vars.qq_bot.set_group_add_request(flag=token,
                                                 type=global_vars.group_requests[token]['type'],
                                                 approve=True)
        for message_id in global_vars.group_requests[token]['message_id_list']:
            edited_message = {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': query.message.text + '\n' + user_name + 'accepted'
            }
            bot.edit_message_text(**edited_message)

    del global_vars.group_requests[token]

global_vars.dp.add_handler(CallbackQueryHandler(callback=group_request_callback),
                           get_plugin_priority(__name__))
