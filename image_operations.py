from PIL import Image
import os
from utils import CQ_IMAGE_ROOT, error
from configparser import ConfigParser
import threading
from urllib.request import urlretrieve
import traceback

def create_jpg_image(path, name):
    ## convert Telegram webp image to jpg image
    im = Image.open(os.path.join(path, name)).convert("RGB")
    im.save(os.path.join(path, name + ".jpg"), "JPEG")

def create_png_image(path, name):
    ## convert Telegram webp image to png image
    im = Image.open(os.path.join(path, name)).convert("RGBA")
    im.save(os.path.join(path, name + ".png"), "PNG")

def qq_get_pic_url(filename):
    ## get real image url from cqimg file
    cqimg = os.path.join(CQ_IMAGE_ROOT, filename+'.cqimg')
    parser = ConfigParser()
    parser.read(cqimg)
    url = parser['image']['url']
    return url

def qq_download_pic(filename):
    ## download image by cqimg file
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

def tg_get_pic_url(file_id, pic_type):
    ## download image from Telegram Server, and generate new image link that send to QQ group
    file_path = tg_bot.getFile(file_id)
    urlretrieve('https://api.telegram.org/file/bot' + tg_token + "/" + file_path[u'file_path'], os.path.join(CQ_IMAGE_ROOT, file_id))
    if pic_type == 'jpg':
        create_jpg_image(CQ_IMAGE_ROOT, file_id)
        pic_url = get_short_url(server_pic_url + file_id + '.jpg')
    elif pic_type == 'png':
        create_png_image(CQ_IMAGE_ROOT, file_id)
        pic_url = get_short_url(server_pic_url + file_id + '.png')
    return pic_url
