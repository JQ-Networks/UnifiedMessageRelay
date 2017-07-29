from PIL import Image
import os
from utils import CQ_IMAGE_ROOT, error
from configparser import ConfigParser
import threading
from urllib.request import urlretrieve
import traceback


def create_jpg_image(path, name):
    im = Image.open(os.path.join(path, name)).convert("RGB")
    im.save(os.path.join(path, name + ".jpg"), "JPEG")


def create_png_image(path, name):
    im = Image.open(os.path.join(path, name)).convert("RGBA")
    im.save(os.path.join(path, name + ".png"), "PNG")


def get_image_url(filename):
    cqimg = os.path.join(CQ_IMAGE_ROOT, filename+'.cqimg')
    parser = ConfigParser()
    parser.read(cqimg)
    url = parser['image']['url']
    return url


class ImageDownloader(threading.Thread):
    def __init__(self, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename

    def run(self):
        try:
            path = os.path.join(CQ_IMAGE_ROOT, self.filename)
            if os.path.exists(path):
                return

            cqimg = os.path.join(CQ_IMAGE_ROOT, self.filename+'.cqimg')
            parser = ConfigParser()
            parser.read(cqimg)

            url = parser['image']['url']
            urlretrieve(url, path)
        except:
            error(self.filename)
            traceback.print_exc()
