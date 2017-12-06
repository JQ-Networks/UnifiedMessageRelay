import global_vars
from cq_utils import cq_location_regex
from utils import get_forward_index, get_qq_name, get_plugin_priority, send_all_except_current
import bot_constant
from telegram.ext import MessageHandler, Filters, DispatcherHandlerStop
from newspaper import Article
from utils import get_full_user_name, trim_emoji, send_all_except_current
import telegram

# disabled due to technical problems
# def link_from_telegram(bot: telegram.Bot, update: telegram.Update):
#     if update.message:
#         message: telegram.Message = update.message
#     else:
#         message: telegram.Message = update.edited_message
#
#     tg_group_id = message.chat_id  # telegram group id
#     forward_index = get_forward_index(tg_group_id=tg_group_id)
#
#     link_regex = re.compile(r'^https?://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]$')
#     text = message.text
#     if link_regex.match(text):  # feature, comment will no be send to qq
#         article = Article(text)
#         article.download()
#         article.parse()
#         sender_name = trim_emoji(get_full_user_name(update.message.from_user)) + ':'  # unicode emoji cannot pass into create_cq_share
#         msg = create_cq_share(text, sender_name, article.title, article.top_image if article.top_image else '')
#         cq_send(update, msg, qq_group_id)
#         raise DispatcherHandlerStop()
#
#
# global_vars.dp.add_handler(MessageHandler(Filters.text, link_from_telegram), 99)  # priority 99


def extract_mqqapi(link):
    locations = cq_location_regex.findall(link)  # [('lat', 'lon', 'name', 'addr')]
    return locations[0], locations[1], locations[2], locations[3]


@global_vars.qq_bot.on_message('group', 'discuss', group=get_plugin_priority(__name__))
def handle_special_message(context):
    if context['message'][0]['type'] in ('image', 'text'):
        return {'pass': True}

    qq_group_id = context.get('group_id')
    qq_discuss_id = context.get('discuss_id')

    forward_index = get_forward_index(qq_group_id=qq_group_id, qq_discuss_id=qq_discuss_id)

    if context['message'][0]['type'] == 'share':
        text = '分享了<a href="' + context['message'][0]['data']['url'] + '">' + context['message'][0]['data']['title'] + '</a>'
    elif context['message'][0]['type'] == 'rich':
        if context['message'][0]['data'].get('url'):
            if context['message'][0]['data']['url'].startswith('mqqapi'):
                lat, lon, name, addr = extract_mqqapi(context['message'][0]['data']['url'])
                text = context['message'][0]['data']['text']
                if qq_group_id:
                    send_all_except_current(forward_index, text, qq_group_id=qq_group_id)
                else:
                    send_all_except_current(forward_index, text, qq_discuss_id=qq_discuss_id)
                global_vars.tg_bot.sendLocation(chat_id=bot_constant.FORWARD_LIST[forward_index]['TG'], latitude=float(lat), longitude=float(lon))
                return ''
            else:
                text = '<a href="' + context['message'][0]['data']['url'] + '">' + context['message'][0]['data']['text'] + '</a>'
        else:
            text = context['message'][0]['data']['text']
    elif context['message'][0]['type'] == 'dice':
        text = '掷出了 <b>' + context['message'][0]['data']['type'] + '</b>'
    elif context['message'][0]['type'] == 'rps':
        text = '出了 <b>' + {'1': '石头', '2': '剪刀', '3': '布'}[context['message'][0]['data']['type']] + '</b>'
    elif context['message'][0]['type'] == 'shake':  # not available in group and discuss
        text = '发送了一个抖动'
    elif context['message'][0]['type'] == 'music':
        text = '分享了<a href="https://y.qq.com/n/yqq/song/' + context['message'][0]['data']['id'] + '_num.html"> qq 音乐</a>'
    elif context['message'][0]['type'] == 'record':
        text = '说了句话，懒得转了'
    else:
        text = context['message']

    if qq_group_id:
        send_all_except_current(forward_index, text, qq_group_id=qq_group_id)
    else:
        send_all_except_current(forward_index, text, qq_discuss_id=qq_discuss_id)
