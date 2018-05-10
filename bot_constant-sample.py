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
    {'QQ': 1234334534534,
     'TG': -2323143534534645,
     'DRIVE_MODE': False,
     'IMAGE_LINK': True},
    {'QQ': 12345678,
     'TG': -123456789,
     'DRIVE_MODE': False,
     'IMAGE_LINK': True}
]
USE_SHORT_URL = True
SERVER_PIC_URL = 'http://expample.com/image/'
CQ_ROOT = '/home/user/coolq/'
# if you need socks5 proxy, setup proxy_url as below
# PROXY_URL = 'socks5://127.0.0.1:1080/'
# if you don't need socks5 proxy, set an empty variable
PROXY_URL = ''


