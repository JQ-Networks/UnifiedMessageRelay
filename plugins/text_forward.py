from common import *

"""
request set CQ_IMAGE_ROOT SERVER_PIC_URL JQ_MODE
"""
# region utils

EMOJI_LIST = [10000035] + \
             list(range(10000048, 10000058)) + \
             [126980, 127183, 127344, 127345, 127358, 127359, 127374] + \
             list(range(127377, 127387)) + \
             [127489, 127490, 127514, 127535] + \
             list(range(127538, 127547)) + \
             [127568, 127569] + \
             list(range(127744, 127777)) + \
             list(range(127792, 127798)) + \
             list(range(127799, 127869)) + \
             list(range(127872, 127892)) + \
             list(range(127904, 127941)) + \
             list(range(127942, 127947)) + \
             list(range(127968, 127985)) + \
             list(range(128000, 128063)) + \
             [128064] + \
             list(range(128066, 128248)) + \
             [128249, 128250, 128251, 128252] + \
             list(range(128256, 128318)) + \
             list(range(128336, 128360)) + \
             list(range(128507, 128577)) + \
             list(range(128581, 128592)) + \
             list(range(128640, 128710)) + \
             [8252, 8265, 8482, 8505] + \
             list(range(8596, 8602)) + \
             [8617, 8618, 8986, 8987] + \
             list(range(9193, 9197)) + \
             [9200, 9203, 9410, 9642, 9643, 9654, 9664] + \
             list(range(9723, 9727)) + \
             [9728, 9729, 9742, 9745, 9748, 9749, 9757, 9786] + \
             list(range(9800, 9812)) + \
             [9824, 9827, 9829, 9830, 9832, 9851, 9855, 9875, 9888, 9889, 9898, 9899, 9917, 9918, 9924, 9925, 9934, 9940, 9962, 9970, 9971, 9973, 9978, 9981, 9986, 9989] + \
             list(range(9992, 9997)) + \
             [9999, 10002, 10004, 10006, 10024, 10035, 10036, 10052, 10055, 10060, 10062, 10067, 10068, 10069, 10071, 10084, 10133, 10134, 10135, 10145, 10160, 10175, 10548, 10549, 11013, 11014, 11015, 11035, 11036, 11088, 11093, 12336, 12349, 12951, 12953, 58634]


def emoji_to_cqemoji(text):
    new_text = ''
    for char in text:
        if (8252 <= ord(char) < 12287 or 126980 < ord(char) < 129472) and ord(char) in EMOJI_LIST:
            new_text += "[CQ:emoji,id=" + str(ord(char)) + "]"
        else:
            new_text += char
    return new_text


def create_jpg_image(path, name):
    """
    convert Telegram webp image to jpg image
    :param path: save path
    :param name: image name
    """
    im = Image.open(os.path.join(path, name)).convert("RGB")
    im.save(os.path.join(path, name + ".jpg"), "JPEG")


def create_png_image(path, name):
    """
    convert Telegram webp image to png image
    :param path: save path
    :param name: image name
    """
    im = Image.open(os.path.join(path, name)).convert("RGBA")
    im.save(os.path.join(path, name + ".png"), "PNG")


def qq_get_pic_url(filename):
    """
    get real image url from cqimg file
    :param filename:
    :return: image url
    """
    cqimg = os.path.join(CQ_IMAGE_ROOT, filename+'.cqimg')
    parser = ConfigParser()
    parser.read(cqimg)
    url = parser['image']['url']
    return url


def qq_download_pic(filename):
    """
    download image by cqimg file
    :param filename: cqimg file name
    """
    try:
        path = os.path.join(CQ_IMAGE_ROOT, filename)
        if os.path.exists(path):
            return

        cqimg = os.path.join(CQ_IMAGE_ROOT, filename + '.cqimg')
        parser = ConfigParser()
        parser.read(cqimg)

        url = parser['image']['url']
        urlretrieve(url, path)
    except:
        error(filename)
        traceback.print_exc()


def get_short_url(long_url):
    """
    generate short url
    :param long_url: the original url
    :return: short url
    """
    # change long url to `t.cn` short url
    sina_api_prefix = 'http://api.t.sina.com.cn/short_url/shorten.json?source=3271760578&url_long='
    try:
        r = requests.get(sina_api_prefix + long_url)
        obj = json.loads(r.text)
        short_url = obj[0]['url_short']
        return short_url

    # when error occurs, return origin long url
    except:
        traceback.print_exc()
        return long_url


def tg_get_pic_url(file_id: str, pic_type: str):
    """
    download image from Telegram Server, and generate new image link that send to QQ group
    :param file_id: telegram file id
    :param pic_type: picture extension name
    :return:
    """
    file = global_vars.tg_bot.getFile(file_id)
    urlretrieve(file.file_path, os.path.join(CQ_IMAGE_ROOT, file_id))
    if pic_type == 'jpg':
        create_jpg_image(CQ_IMAGE_ROOT, file_id)
        pic_url = get_short_url(SERVER_PIC_URL + file_id + '.jpg')
        return pic_url
    elif pic_type == 'png':
        create_png_image(CQ_IMAGE_ROOT, file_id)
        pic_url = get_short_url(SERVER_PIC_URL + file_id + '.png')
        return pic_url
    return ''


def cq_send(update: telegram.Update, text: str, qq_group_id: int):
    """
    send telegram message to qq with forward of reply support
    :param update: telegram.Update
    :param text:
    :param qq_group_id:
    :return:
    """
    sender_name = get_full_user_name(update.message.from_user)
    forward_from = get_forward_from(update.message)
    reply_to = get_reply_to(update.message.reply_to_message)

    # get real sender from telegram message
    if forward_from and update.message.forward_from.id == global_vars.tg_bot_id:
        left_start = text.find(': ')
        if left_start != -1:
            text = text[left_start + 2:]
    text = emoji_to_cqemoji(text)

    global_vars.qq_bot.send(SendGroupMessage(
        group=qq_group_id,
        text=sender_name + reply_to + forward_from + ': ' + text
    ))


# endregion

PIC_LINK_MODE = []

for forward in FORWARD_LIST:
    PIC_LINK_MODE.append(FORWARD_LIST['Pic_link'])


def photo_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))

    file_id = update.message.photo[-1].file_id
    pic_url = tg_get_pic_url(file_id, 'jpg')
    if JQ_MODE:
        text = '[CQ:image,file=' + file_id + '.jpg]'
    else:
        text = '[图片, 请点击查看' + pic_url + ']'
    if update.message.caption:
        text += update.message.caption
    cq_send(update, text, qq_group_id)


def video_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    text = '[视频]'
    cq_send(update, text, qq_group_id)


def audio_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    text = '[音频]'
    cq_send(update, text, qq_group_id)


def document_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))
    text = '[文件]'
    cq_send(update, text, qq_group_id)


def sticker_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))

    if PIC_LINK_MODE[forward_index]:
        file_id = update.message.sticker.file_id
        pic_url = tg_get_pic_url(file_id, 'png')
        if JQ_MODE:
            text = '[CQ:image,file=' + file_id + '.png]'
        else:
            text = '[' + update.message.sticker.emoji + ' sticker, 请点击查看' + pic_url + ']'
    else:
        text = '[' + update.message.sticker.emoji + ' sticker]'
    cq_send(update, text, qq_group_id)


def text_from_telegram(bot, update):
    tg_group_id = update.message.chat_id  # telegram group id
    qq_group_id, _, forward_index = get_forward_index(tg_group_id=int(tg_group_id))

    text = update.message.text

    if text.startswith('//'):
        return
    else:
        cq_send(update, text, qq_group_id)


global_vars.dp.add_handler(MessageHandler(Filters.text | Filters.command, text_from_telegram), 100) # priority 100
global_vars.dp.add_handler(MessageHandler(Filters.sticker, sticker_from_telegram), 100)
global_vars.dp.add_handler(MessageHandler(Filters.audio, audio_from_telegram), 100)
global_vars.dp.add_handler(MessageHandler(Filters.photo, photo_from_telegram), 100)
global_vars.dp.add_handler(MessageHandler(Filters.document, document_from_telegram), 100)
global_vars.dp.add_handler(MessageHandler(Filters.video, video_from_telegram), 100)


qq_name_lists = []


@global_vars.qq_bot.listener((RcvdGroupMessage, ), 100)  # priority 100
def new(message):
    # logging.info('(' + message.qq + '): ' + message.text)

    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)

    text = message.text  # get message text

    name_list = qq_name_lists[forward_index]  # get reflect of this QQ group member

    text, _ = re.subn(r'\[CQ:image.*?\]', '', text)  # clear CQ:image in text

    # replace special characters
    text, _ = re.subn('&amp;', '&', text)
    text, _ = re.subn('&#91;', '[', text)
    text, _ = re.subn('&#93;', ']', text)
    text, _ = re.subn('&#44;', ',', text)

    text = cq_emoji_regex.sub(lambda x: chr(int(x.group(1))), text)  # replace [CQ:emoji,id=*]
    text = qq_face_regex.sub(lambda x: qq_emoji_list[int(x.group(1))] if int(x.group(1)) in qq_emoji_list else '\u2753', text)  # replace [CQ:face,id=*]

    def replace_name(qq_number):  # replace each qq number with preset id
        qq_number = qq_number.group(1)
        if qq_number in qq_name_lists[forward_index]:
            return '@' + qq_name_lists[forward_index][qq_number]
        else:
            return '@' + qq_number

    text = CQAt.PATTERN.sub(replace_name, text)  # replace qq's at to telegram's

    # replace CQ:share/CQ:music, could be improved

    if cq_share_regex.match(message.text):
        url, title, content, image_url = extract_cq_share(message.text)
        text = title + '\n' + url
    elif cq_music_regex.match(message.text):
        text = 'some music'

    elif text == '[reload namelist]':
        reload_qq_namelist()
        qq_bot.send(SendGroupMessage(
            group=qq_group_id,
            text='QQ群名片已重置'
        ))

    # replace QQ number to group member name, get full message text
    if str(message.qq) in name_list:
        full_msg = name_list[str(message.qq)] + ': ' + text.strip()
    else:
        full_msg = str(message.qq) + ': ' + text.strip()

    # send pictures to Telegram group
    pic_send_mode = 1
    # mode = 0 -> direct mode: cqlink to tg server
    # mode = 1 -> (deprecated) download mode: cqlink download to local to tg server
    # mode = 2 -> download mode: cqlink download to local, upload from disk to tg server
    image_num = 0
    for matches in CQImage.PATTERN.finditer(message.text):
        image_num = image_num + 1
        filename = matches.group(1)
        url = qq_get_pic_url(filename)
        pic = url
        if pic_send_mode == 1:
            qq_download_pic(filename)
            my_url = SERVER_PIC_URL + filename
            pic = my_url
        elif pic_send_mode == 2:
            qq_download_pic(filename)
            pic = open(os.path.join(CQ_IMAGE_ROOT, filename), 'rb')
        # gif pictures send as document
        if filename.lower().endswith('gif'):
            try:
                # the first image in message attach full message text
                if image_num == 1:
                    global_vars.tg_bot.sendDocument(tg_group_id, pic, caption=full_msg)
                else:
                    global_vars.tg_bot.sendDocument(tg_group_id, pic)
            except BadRequest:
                # when error occurs, download picture and send link instead
                error(message)
                traceback.print_exc()
                if pic_send_mode == 0:
                    qq_download_pic(filename)
                my_url = get_short_url(SERVER_PIC_URL + filename)
                pic = my_url
                tg_bot.sendMessage(tg_group_id, pic + '\n' + full_msg)

        # jpg/png pictures send as photo
        else:
            try:
                # the first image in message attach full message text
                if image_num == 1:
                    global_vars.tg_bot.sendPhoto(tg_group_id, pic, caption=full_msg)
                else:
                    global_vars.tg_bot.sendPhoto(tg_group_id, pic)
            except BadRequest:
                # when error occurs, download picture and send link instead
                error(message)
                traceback.print_exc()
                if pic_send_mode == 0:
                    qq_download_pic(filename)
                my_url = get_short_url(SERVER_PIC_URL + filename)
                pic = my_url
                global_vars.tg_bot.sendMessage(tg_group_id, pic + '\n' + full_msg)

    # send plain text message with bold group member name
    if image_num == 0:
        if str(message.qq) in name_list:
            full_msg_bold = '<b>' + name_list[str(message.qq)] + '</b>: ' + text.strip().replace('<', '&lt;').replace('>', '&gt;')
        else:
            full_msg_bold = '<b>' + str(message.qq) + '</b>: ' + text.strip().replace('<', '&lt;').replace('>', '&gt;')
        global_vars.tg_bot.sendMessage(tg_group_id, full_msg_bold, parse_mode='HTML')


# add commands

@command_listener('[drive mode on]')
def drive_mode_on(forward_index, tg_group_id, qq_group_id):
    DRIVE_MODE[forward_index] = True
    msg = 'Telegram向QQ转发消息已暂停'
    global_vars.tg_bot.sendMessage(tg_group_id, msg)
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))


@command_listener('[drive mode off]')
def drive_mode_on(forward_index, tg_group_id, qq_group_id):
    DRIVE_MODE[forward_index] = False
    msg = 'Telegram向QQ转发消息已重启'
    global_vars.tg_bot.sendMessage(tg_group_id, msg)
    global_vars.qq_bot.send(SendGroupMessage(group=qq_group_id, text=msg))
