import global_vars
import telegram
from command import command_listener
from utils import send_all_except_current, text_reply


@command_listener('alipay', 'ali', description="Support Coolq Telegram Bot's work")
def show_red_pack(forward_index: int,
                  tg_group_id: int=None,
                  tg_user: telegram.User=None,
                  tg_message_id: int=None,
                  qq_group_id: int=None,
                  qq_discuss_id: int=None,
                  qq_user: int=None):

    message = '点击链接或者复制到浏览器打开，领取每日红包 https://qr.alipay.com/c1x00417d1veog0b99yea4e'

    if tg_group_id:
        send_all_except_current(forward_index,
                                text_reply(message),
                                tg_group_id=tg_group_id)
        global_vars.tg_bot.sendMessage(chat_id=tg_group_id,
                                       text=message,
                                       reply_to_message_id=tg_message_id)
    elif qq_group_id:
        send_all_except_current(forward_index,
                                text_reply(message),
                                qq_group_id=qq_group_id)
        return {'reply': message}
    else:
        send_all_except_current(forward_index,
                                text_reply(message),
                                qq_discuss_id=qq_discuss_id)
        return {'reply': message}
