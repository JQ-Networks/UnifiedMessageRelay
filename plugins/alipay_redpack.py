import telegram
from main.command import command_listener

from main.utils import send_both_side


@command_listener('alipay', 'ali', description="Support Coolq Telegram Bot's work")
def show_red_pack(forward_index: int,
                  tg_group_id: int=None,
                  tg_user: telegram.User=None,
                  tg_message_id: int=None,
                  tg_reply_to: telegram.Message=None,
                  qq_group_id: int=None,
                  qq_discuss_id: int=None,
                  qq_user: int=None):

    message = '点击链接或者复制到浏览器打开，领取每日红包（两个）\nhttps://jqqqqqqqqqq.cn/hongbao\nhttps://jogle.top/hb/mengniu'

    return send_both_side(forward_index,
                          message,
                          qq_group_id,
                          qq_discuss_id,
                          tg_group_id,
                          tg_message_id)
