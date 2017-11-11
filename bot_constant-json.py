# -*- coding: utf-8 -*-
"""
将本文件重名为为 bot_constant.py 以启用JSON格式配置文件支持。
本脚本支持读取外部配置文件,默认读取bot_constant.json

请将外部配置文件的路径添加至环境变量 CTB_JSON_SETTINGS_PATH
例如：/home/user/bot_constant.json 或 ../esuSet.json
"""

import os
import json

filepath = os.getenv('CTB_JSON_SETTINGS_PATH', 'bot_constant.json')
with open(filepath, 'r') as f1:
    settingsJSON = json.loads(f1.read())

TOKEN = settingsJSON['TOKEN']
QQ_BOT_ID = settingsJSON['QQ_BOT_ID']
FORWARD_LIST = settingsJSON['FORWARD_LIST']
SERVER_PIC_URL = settingsJSON['SERVER_PIC_URL']
CQ_ROOT = settingsJSON['CQ_ROOT']
CQ_PORT = settingsJSON['CQ_PORT']
JQ_MODE = settingsJSON['JQ_MODE']  # if use Coolq Pro, set as True, otherwise False
print('[CTBot] JSON Config file support [EN]')