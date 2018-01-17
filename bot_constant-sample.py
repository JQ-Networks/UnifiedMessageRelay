# -*- coding: utf-8 -*-

DEBUG_MODE = True  # log will not take up much place, but it is necessary when locating problems

BAIDU_API = 'asdasdaasd'

# cq-http-api server config
API_ROOT = 'http://127.0.0.1:5700/'  # should be the same as cq-http-api api address
ACCESS_TOKEN = 'access_token'  # should be the same as cq-http-api config
SECRET = 'secret '  # should be the same as cq-http-api config

# cq-http-api client config, should be the same as cq-http-api post config
HOST = '127.0.0.1'
PORT = 8080

TOKEN = 'telegram_bot_token'
QQ_BOT_ID = 'qq_number'
FORWARD_LIST = [
    {'DISCUSS': 2314324234325346543,
     'TG': -2323143534534645,
     'DRIVE_MODE': False,
     'IMAGE_LINK': True},
    {'QQ': 12345678,
     'TG': -123456789,
     'DRIVE_MODE': False,
     'IMAGE_LINK': True}
]
SERVER_PIC_URL = 'http://expample.com/image/'
CQ_ROOT = '/home/user/coolq/'
