import hashlib
from functools import partial
from PIL import Image
import os
import shutil
import ffmpy
import requests
import json
import global_vars
import logging
from telegram import TelegramError

from bot_constant import CQ_ROOT, USE_SHORT_URL, SERVER_PIC_URL

logger = logging.getLogger('CTB.' + __name__)

CQ_IMAGE_ROOT = os.path.join(CQ_ROOT, r'data/image')


def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()


def get_url(filename: str):
    """
    get url for file
    :param filename: file name
    :return: short url or long url
    """
    long_url = SERVER_PIC_URL + filename
    if not USE_SHORT_URL:
        return long_url
    # change long url to `t.cn` short url
    sina_api_prefix = 'http://api.t.sina.com.cn/short_url/shorten.json?source=3271760578&url_long='
    try:
        r = requests.get(sina_api_prefix + long_url)
        obj = json.loads(r.text)
        short_url = obj[0]['url_short']
        return short_url

    # when error occurs, return origin long url
    except:
        logger.exception('Error occurred when retrieving short URL:')
        return long_url


def tg_get_file(file_id: str, mp4: bool=False):
    """
    download image from Telegram Server
    :param file_id: telegram file id
    :param mp4: file is mp4
    :return: file name
    """
    result = global_vars.fdb.get_filename_by_fileid(file_id)
    if result:  # result contains filename
        return result

    file = global_vars.tg_bot.getFile(file_id)
    filename = os.path.join(CQ_IMAGE_ROOT, file_id)
    for i in range(1, 6):
        try:
            file.download(custom_path=os.path.join(CQ_IMAGE_ROOT, file_id))
            break
        except TelegramError as e:
            logger.warning(f'{e.message} occurred {i} time(s) while downloading {file_id}.')

    if mp4:  # mp4 will be transcoded to gif
        mp4_input = filename
        new_name = file_id + '.gif'
        new_name_full = os.path.join(CQ_IMAGE_ROOT, new_name)
        ff = ffmpy.FFmpeg(inputs={mp4_input: None},
                          outputs={'/tmp/palettegen.png': '-vf palettegen'},
                          global_options=('-y'))
        ff.run()
        ff = ffmpy.FFmpeg(inputs={mp4_input: None, '/tmp/palettegen.png': None},
                          outputs={new_name_full: '-filter_complex paletteuse'},
                          global_options=('-y'))
        ff.run()
        os.remove(filename)
        file_size = os.path.getsize(new_name_full)
        global_vars.fdb.tg_add_resource(file_id, new_name, 'gif', md5sum(new_name_full), file_size)
        return new_name

    image = Image.open(filename)
    file_type = image.format
    if file_type == 'JPEG':
        image.close()
        new_name = file_id + '.jpg'
        new_name_full = os.path.join(CQ_IMAGE_ROOT, new_name)
        os.rename(filename, new_name_full)
        file_size = os.path.getsize(new_name_full)
        global_vars.fdb.tg_add_resource(file_id, new_name, 'jpg', md5sum(new_name_full), file_size)
    elif file_type == 'PNG':
        image.close()
        new_name = file_id + '.png'
        new_name_full = os.path.join(CQ_IMAGE_ROOT, new_name)
        os.rename(filename, new_name_full)
        file_size = os.path.getsize(new_name_full)
        global_vars.fdb.tg_add_resource(file_id, new_name, 'png', md5sum(new_name_full), file_size)
    elif file_type == 'GIF':
        image.close()
        new_name = file_id + '.gif'
        new_name_full = os.path.join(CQ_IMAGE_ROOT, new_name)
        os.rename(filename, new_name_full)
        file_size = os.path.getsize(new_name_full)
        global_vars.fdb.tg_add_resource(file_id, new_name, 'gif', md5sum(new_name_full), file_size)
    elif file_type == 'WEBP':
        new_name = file_id + '.png'
        new_name_full = os.path.join(CQ_IMAGE_ROOT, new_name)
        image.convert('RGBA').save(new_name_full, 'PNG')
        image.close()
        os.remove(filename)
        file_size = os.path.getsize(new_name_full)
        global_vars.fdb.tg_add_resource(file_id, new_name, 'png', md5sum(new_name_full), file_size)
    else:
        logger.debug(f'Unhandled format: {file_type} filename: {filename}')
        new_name = file_id + '.jpg'
        new_name_full = os.path.join(CQ_IMAGE_ROOT, new_name)
        image.save(new_name_full, 'JPEG')
        image.close()
        os.remove(filename)
        file_size = os.path.getsize(new_name_full)
        global_vars.fdb.tg_add_resource(file_id, new_name, 'jpg', md5sum(new_name_full), file_size)
    return new_name

