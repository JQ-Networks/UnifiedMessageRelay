# -*- coding: utf-8 -*-

DEBUG_MODE = True

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
     'Drive_mode': False,
     'Pic_link': True},
    {'QQ': 12345678,
     'TG': -123456789,
     'Drive_mode': False,
     'Pic_link': True}
]
SERVER_PIC_URL = 'http://expample.com/image/'
CQ_ROOT = '/home/user/coolq/'
JQ_MODE = True  # If you are using CoolQ AIr, change to False
