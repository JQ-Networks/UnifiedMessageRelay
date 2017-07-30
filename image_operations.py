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

