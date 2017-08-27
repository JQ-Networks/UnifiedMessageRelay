import os
import traceback
from PIL import Image
from utils import CQ_IMAGE_ROOT, error
from configparser import ConfigParser
from urllib.request import urlretrieve


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

