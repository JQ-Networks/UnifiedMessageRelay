import global_vars
from cqsdk import RcvdGroupMessage, RE_CQ_SPECIAL
from cq_utils import cq_share_regex, cq_music_regex, cq_dice_regex,\
    cq_custom_music_regex, cq_shake_regex, cq_rps_regex, cq_record_regex, cq_rich_regex, \
    extract_cq_share, extract_cq_dice, extract_cq_music, extract_cq_record, \
    extract_cq_rich, extract_cq_rps, extract_cq_custom_music
from utils import get_forward_index, get_qq_name


@global_vars.qq_bot.listener((RcvdGroupMessage, ), 99)  # priority 100
def new(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if RE_CQ_SPECIAL.match(message.text):
        text = ''
        if cq_dice_regex.match(message.text):
            dice = extract_cq_dice(message.text)
            text = '扔了' + str(dice)
        elif cq_shake_regex.match(message.text):
            text = '发送了一个抖动'
        elif cq_rps_regex.match(message.text):
            rps = extract_cq_rps(message.text)
            text = '出了' + '石头' if rps == 1 else '剪刀' if rps == 2 else '布'
        elif cq_rich_regex.match(message.text):
            url, _text = extract_cq_rich(message.text)
            text = ': ' + _text + '(' + url + ')'
        elif cq_share_regex.match(message.text):
            url, title, content, image_url = extract_cq_share(message.text)
            text = '分享了 ' + title + '(' + url + ')'
        elif cq_custom_music_regex.match(message.text):
            url, audio, title, content, image = extract_cq_custom_music(message.text)
            text = '分享了 ' + title + '(' + url + ')'
        elif cq_music_regex.match(message.text):
            _type, _id = extract_cq_music(message.text)
            text = '分享了 音乐(https://y.qq.com/n/yqq/song/' + str(_id) + '_num.html)'
        elif cq_record_regex.match(message.text):
            file, magic = extract_cq_record(message.text)
            text = '说了句话，懒得转了'
        if text:
            full_msg = get_qq_name(int(message.qq), forward_index) + text.strip()
            global_vars.tg_bot.sendMessage(tg_group_id, full_msg, parse_mode='Markdown')
            return True
    return False
