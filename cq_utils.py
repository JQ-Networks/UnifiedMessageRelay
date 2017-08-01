import re

cq_emoji_regex = re.compile(r'\[CQ:emoji,id=(\d+?)\]')
qq_face_regex = re.compile(r'\[CQ:face,id=(\d+?)\]')
cq_music_regex = re.compile(r'\[CQ:music,type=(.*),id=(\d+)\]')
cq_custom_music_regex = re.compile(r'\[CQ:share,type=custom,url=(.*),audio=(.*),title=(.*),content=(.*),image=(.*)\]', re.DOTALL)
cq_share_regex = re.compile(r'\[CQ:share,url=(.*),title=(.*),content=(.*),image=(.*)\]', re.DOTALL)
cq_anonymous_regex = re.compile(r'\[CQ:anonymous,ignore=(true|false)\]')
cq_shake_regex = re.compile(r'\[CQ:shake\]')
cq_dice_regex = re.compile(r'\[CQ:dice(,type=(\d))?\]')
cq_rps_regex = re.compile(r'\[CQ:dice(,type=(\d))?\]')
cq_at_regex = re.compile(r'\[CQ:at,qq=(\d+?)\]')
cq_record_regex = re.compile(r'\[CQ:record,file=(.*)(,magic=(true|false))?\]')


# https://d.cqp.me/Pro/CQ码
# to be continued

def extract_cq_share(message):
    """
    get share parameters
    :param message: raw cq message
    :return: url, title, content, image_url
    """
    result = cq_share_regex.findall(message)[0]
    return result[0], result[1], result[2], result[3]
